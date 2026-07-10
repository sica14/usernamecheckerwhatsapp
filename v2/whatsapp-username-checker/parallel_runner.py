"""
Parallel WhatsApp Username Checker
Splits the username list across multiple emulators and runs them simultaneously.

Usage:
    python parallel_runner.py --workers 2 --devices emulator-5554 emulator-5556

Each worker needs:
  - A running Android emulator with that device name  (`adb devices` to list them)
  - WhatsApp installed and logged in on that emulator
  - A DIFFERENT phone number / WhatsApp account per emulator
"""

import argparse
import csv
import multiprocessing
import sys
import time
from pathlib import Path

import config


def load_remaining(usernames_file: str, output_file: str) -> list[str]:
    """Return usernames not yet in results.csv."""
    all_names = [
        u.strip()
        for u in Path(usernames_file).read_text(encoding="utf-8").splitlines()
        if u.strip() and not u.startswith("#")
    ]
    done = set()
    if Path(output_file).exists():
        with open(output_file, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                done.add(row["username"])
    remaining = [u for u in all_names if u not in done]
    print(f"Total: {len(all_names)}  |  Already done: {len(done)}  |  Remaining: {len(remaining)}")
    return remaining


def split_chunks(items: list, n: int) -> list[list]:
    """Split a list into n roughly equal chunks."""
    size = (len(items) + n - 1) // n
    return [items[i:i + size] for i in range(0, len(items), size)]


def worker(device_name: str, usernames: list[str], output_file: str, worker_id: int):
    """Run the checker for a subset of usernames on a specific emulator."""
    # Import here so each process gets its own driver instance
    from main import WhatsAppUsernameChecker, AVAILABLE, TAKEN, INVALID, ERROR, log
    import logging

    # Add worker ID to log prefix
    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s  [W{worker_id}] %(levelname)-7s  %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f"checker_worker{worker_id}.log", encoding="utf-8"),
        ],
        force=True,
    )

    # Override device for this worker
    original_device = config.DEVICE_NAME
    config.DEVICE_NAME = device_name

    try:
        checker = WhatsAppUsernameChecker()
        checker.run_batch(usernames, output_file)
    finally:
        config.DEVICE_NAME = original_device


def main():
    parser = argparse.ArgumentParser(description="Parallel WhatsApp username checker")
    parser.add_argument("--workers", type=int, default=2,
                        help="Number of parallel emulators (default: 2)")
    parser.add_argument("--devices", nargs="+",
                        help="Device names from `adb devices` "
                             "(default: emulator-5554, emulator-5556, …)")
    args = parser.parse_args()

    n = args.workers

    # Build device list
    if args.devices:
        devices = args.devices
    else:
        # Default: emulator-5554, emulator-5556, emulator-5558, …
        devices = [f"emulator-{5554 + i * 2}" for i in range(n)]

    if len(devices) < n:
        print(f"ERROR: Need {n} devices but only {len(devices)} provided.")
        sys.exit(1)

    remaining = load_remaining(config.USERNAMES_FILE, config.OUTPUT_FILE)
    if not remaining:
        print("Nothing left to check.")
        sys.exit(0)

    chunks = split_chunks(remaining, n)
    print(f"\nStarting {n} workers:")
    for i, (device, chunk) in enumerate(zip(devices, chunks)):
        print(f"  Worker {i+1}: {device}  ({len(chunk)} usernames)")
    print()

    # Shared output file — workers append rows, resume logic deduplicates
    processes = []
    for i, (device, chunk) in enumerate(zip(devices, chunks)):
        p = multiprocessing.Process(
            target=worker,
            args=(device, chunk, config.OUTPUT_FILE, i + 1),
            daemon=True,
        )
        p.start()
        processes.append(p)
        time.sleep(3)  # Stagger starts so manual navigation prompts don't overlap

    for p in processes:
        p.join()

    print("\nAll workers done.")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
