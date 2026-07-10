# ── Appium ───────────────────────────────────────────────────────────────────
# URL of your running Appium server (default port is 4723)
APPIUM_SERVER = "http://localhost:4723"

# Name of your Android emulator or real device.
# Run `adb devices` to see the connected devices/emulators.
# Emulators are usually named "emulator-5554"
DEVICE_NAME = "emulator-5554"

# ── Timing ───────────────────────────────────────────────────────────────────
# How long (seconds) to wait for each UI element to appear
ELEMENT_TIMEOUT = 15

# How long (seconds) to wait after typing a username before reading the status.
CHECK_DELAY = 0.8

# Pause (seconds) between consecutive username checks.
DELAY_BETWEEN_CHECKS = 0.3

# Take a break every N checks to avoid WhatsApp rate limiting.
# Set to 0 to disable breaks entirely.
BREAK_EVERY = 300

# How long (seconds) to pause during each break.
BREAK_DURATION = 120  # 2 minutes

# ── Files ─────────────────────────────────────────────────────────────────────
# Input: one username per line. Lines starting with # are ignored.
USERNAMES_FILE = "usernames.txt"

# Output: CSV with columns username, status, checked_at
OUTPUT_FILE = "results.csv"
