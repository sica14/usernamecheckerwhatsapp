"""
WhatsApp Username Availability Checker
Uses Appium + Android emulator to check usernames in batch.

Prerequisites: See README.md
"""

import time
import csv
import logging
import sys
from pathlib import Path
from datetime import datetime

from appium import webdriver
from appium.options.android.uiautomator2.base import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, StaleElementReferenceException,
    InvalidSessionIdException,
)

import config

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("checker.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


# ── Result constants ──────────────────────────────────────────────────────────
AVAILABLE   = "available"
TAKEN       = "taken"
INVALID     = "invalid"
ERROR       = "error"


class WhatsAppUsernameChecker:
    def __init__(self):
        options = UiAutomator2Options()
        options.platform_name          = "Android"
        options.device_name            = config.DEVICE_NAME
        options.app_package            = "com.whatsapp"
        options.app_activity           = "com.whatsapp.Main"
        options.no_reset               = True   # keep WhatsApp logged in
        # Must be longer than BREAK_DURATION so session stays alive during breaks
        options.new_command_timeout    = max(config.BREAK_DURATION + 120, 300)

        log.info("Connecting to Appium server at %s …", config.APPIUM_SERVER)
        self.driver = webdriver.Remote(config.APPIUM_SERVER, options=options)
        self.wait   = WebDriverWait(self.driver, config.ELEMENT_TIMEOUT)

    # ── Navigation helpers ────────────────────────────────────────────────────

    def _find(self, by, value, timeout=None):
        t = timeout or config.ELEMENT_TIMEOUT
        return WebDriverWait(self.driver, t).until(
            EC.presence_of_element_located((by, value))
        )

    def _tap(self, by, value, timeout=None):
        self._find(by, value, timeout).click()

    def _open_whatsapp(self):
        """Bring WhatsApp to the foreground (it should already be logged in)."""
        self.driver.activate_app("com.whatsapp")
        time.sleep(2)

    def _go_to_username_screen(self):
        """
        Waits for the user to manually open the WhatsApp username input screen,
        then verifies that an EditText is visible before proceeding.
        """
        print()
        print("═" * 60)
        print("ACTION REQUIRED:")
        print("  On the emulator, open WhatsApp and navigate to:")
        print("  Settings → tap your name/profile → Username")
        print("  Make sure the username TEXT FIELD is visible on screen.")
        print("═" * 60)
        input("Press ENTER here when you are on the username screen…")
        print()
        time.sleep(1)

    def _clear_and_type(self, element, text):
        element.click()
        time.sleep(0.3)
        try:
            # Most reliable on Android: atomically replace the whole value
            self.driver.execute_script(
                "mobile: replaceElementValue",
                {"elementId": element.id, "value": text}
            )
        except Exception:
            # Fallback: clear then type
            element.clear()
            time.sleep(0.5)
            element.send_keys(text)

    def _read_availability(self) -> str:
        """
        Read the availability status label shown below the username field.
        Returns one of: AVAILABLE, TAKEN, INVALID, ERROR.
        """
        time.sleep(config.CHECK_DELAY)

        # WhatsApp shows a helper text under the input field.
        # Common text patterns (may vary by app version / locale):
        available_hints = ["available", "is available", "username is available"]
        taken_hints     = ["taken", "already taken", "not available", "unavailable"]
        invalid_hints   = ["too short", "too long", "invalid", "only letters",
                           "characters", "must contain"]
        # Texts that contain "available" but are NOT personal account availability
        business_hints  = ["business", "empresa", "web", "whatsapp business"]

        try:
            # Scan EVERY TextView on screen — most reliable across WhatsApp versions
            all_texts = self.driver.find_elements(
                AppiumBy.CLASS_NAME, "android.widget.TextView"
            )

            visible_texts = []
            for el in all_texts:
                text = el.text.strip().lower()
                if text:
                    visible_texts.append(text)
                    if any(h in text for h in taken_hints):
                        return TAKEN
                    if any(h in text for h in invalid_hints):
                        return INVALID
                    if any(h in text for h in available_hints):
                        # Make sure it's not a WhatsApp Business false positive
                        if any(b in text for b in business_hints):
                            log.debug("Skipping business/web match: %s", text)
                            continue
                        return AVAILABLE

            # Save page source for debugging if nothing matched
            log.warning("Could not read status. Visible texts on screen: %s", visible_texts)
            with open("page_source_debug.xml", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            log.warning("Full page source saved to page_source_debug.xml for inspection.")
            return ERROR

        except Exception as exc:
            log.warning("Error reading availability: %s", exc)
            return ERROR

    def _go_back_to_username_field(self):
        """Press back once to return to the username input screen."""
        self.driver.back()
        time.sleep(0.5)

    # ── Core check ────────────────────────────────────────────────────────────

    def _get_input_field(self):
        """Find the username input field, caching it for reuse."""
        if self._input_field is not None:
            try:
                _ = self._input_field.is_displayed()
                return self._input_field
            except (StaleElementReferenceException, Exception):
                self._input_field = None

        try:
            self._input_field = self._find(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().resourceId("com.whatsapp:id/username_edit_text")',
                timeout=5
            )
        except TimeoutException:
            self._input_field = self._find(
                AppiumBy.CLASS_NAME, "android.widget.EditText", timeout=5
            )
        return self._input_field

    def check_username(self, username: str) -> str:
        for attempt in range(2):
            try:
                input_field = self._get_input_field()
                self._clear_and_type(input_field, username)
                result = self._read_availability()
                log.info("%-30s  →  %s", username, result.upper())
                return result
            except StaleElementReferenceException:
                # Element went stale (WhatsApp refreshed UI) — clear cache and retry
                self._input_field = None
                if attempt == 1:
                    log.error("Stale element for '%s' after retry", username)
                    return ERROR
            except TimeoutException:
                log.error("Username input field not found for '%s'", username)
                return ERROR
        return ERROR

    # ── Batch runner ──────────────────────────────────────────────────────────

    def run_batch(self, usernames: list[str], output_file: str):
        self._input_field = None  # cache reset

        # Resume support: skip usernames already in results.csv
        already_done = set()
        if Path(output_file).exists():
            with open(output_file, newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    already_done.add(row["username"])
            if already_done:
                log.info("Resuming — skipping %d already-checked usernames.", len(already_done))

        queue = [u.strip() for u in usernames
                 if u.strip() and not u.startswith("#") and u.strip() not in already_done]
        total = len(queue)
        log.info("%d usernames to check.", total)

        results = []
        try:
            self._go_to_username_screen()

            for i, username in enumerate(queue, 1):
                status = self.check_username(username)
                results.append({"username": username, "status": status,
                                 "checked_at": datetime.utcnow().isoformat()})

                # Append result immediately so we can resume on crash
                write_header = not Path(output_file).exists() or (i == 1 and not already_done)
                with open(output_file, "a", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=["username", "status", "checked_at"])
                    if write_header:
                        w.writeheader()
                    w.writerow(results[-1])

                # Auto-break every N checks
                if config.BREAK_EVERY and i % config.BREAK_EVERY == 0:
                    log.info("Break: %d/%d done. Pausing %ds to avoid rate limits…",
                             i, total, config.BREAK_DURATION)
                    # Send a keepalive ping every 60s so Appium session stays alive
                    elapsed = 0
                    while elapsed < config.BREAK_DURATION:
                        chunk = min(60, config.BREAK_DURATION - elapsed)
                        time.sleep(chunk)
                        elapsed += chunk
                        try:
                            self.driver.current_activity  # keepalive
                        except Exception:
                            pass
                    self._input_field = None  # re-find field after break
                else:
                    time.sleep(config.DELAY_BETWEEN_CHECKS)

        except Exception as exc:
            log.error("Fatal error during batch: %s", exc, exc_info=True)
        finally:
            self._print_summary(results, output_file)
            try:
                self.driver.quit()
            except Exception:
                pass  # session may already be dead

        return results

    @staticmethod
    def _print_summary(results: list[dict], path: str):
        available = [r for r in results if r["status"] == AVAILABLE]
        log.info("─" * 50)
        log.info("Session done. Checked %d usernames.", len(results))
        log.info("Available : %d", len(available))
        log.info("Taken     : %d", sum(1 for r in results if r["status"] == TAKEN))
        log.info("Invalid   : %d", sum(1 for r in results if r["status"] == INVALID))
        log.info("Errors    : %d", sum(1 for r in results if r["status"] == ERROR))
        log.info("Results saved to: %s", path)
        if available:
            log.info("Available usernames this session:")
            for r in available:
                log.info("  ✓  %s", r["username"])


def load_usernames(path: str) -> list[str]:
    p = Path(path)
    if not p.exists():
        log.error("Username list not found: %s", path)
        sys.exit(1)
    return p.read_text(encoding="utf-8").splitlines()


if __name__ == "__main__":
    usernames = load_usernames(config.USERNAMES_FILE)
    log.info("Loaded %d usernames from '%s'", len(usernames), config.USERNAMES_FILE)

    checker = WhatsAppUsernameChecker()
    checker.run_batch(usernames, config.OUTPUT_FILE)
