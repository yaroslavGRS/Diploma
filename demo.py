"""
demo.py — demonstration of the self-healing framework.

Run:
    python demo.py

What happens:
    1. Flask server starts automatically in the background.
    2. SelfHealingDriver runs login tests on 5 DOM mutation scenarios.
    3. SelfHealingDriver runs registration tests on v1 and v2.
    4. Results table is printed to console.

No manual setup needed — just: python demo.py
"""

import time
import subprocess
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from self_healing.driver import SelfHealingDriver

BASE     = "http://localhost:5000"
EMAIL    = "admin@test.com"
PASSWORD = "password123"
NAME     = "Test User"

LOGIN_SCENARIOS = [
    ("v1", "Login  v1 — stable DOM       "),
    ("v2", "Login  v2 — renamed IDs      "),
    ("v3", "Login  v3 — renamed classes  "),
    ("v4", "Login  v4 — wrapper divs     "),
    ("v5", "Login  v5 — combined mutation"),
]

REGISTER_SCENARIOS = [
    ("v1", "Register v1 — stable DOM     "),
    ("v2", "Register v2 — renamed IDs    "),
]


def start_flask():
    subprocess.Popen(
        [sys.executable, "app/app.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(2)


def run_login(driver, version: str, label: str) -> dict:
    """Runs a login scenario and returns stats."""
    driver.stats  = {"normal": 0, "healed": 0, "failed": 0}
    driver.timing = {"normal": 0.0, "yolo": 0.0}
    driver.get(f"{BASE}/{version}/login")

    driver.send_keys_to(By.ID, "email",    EMAIL,    element_id="email")
    driver.send_keys_to(By.ID, "password", PASSWORD, element_id="password")
    driver.click(       By.ID, "login-btn",           element_id="btn")

    WebDriverWait(driver._driver, 5).until(EC.url_contains("success"))
    return _record(driver, label)


def run_register(driver, version: str, label: str) -> dict:
    """Runs a registration scenario and returns stats."""
    driver.stats  = {"normal": 0, "healed": 0, "failed": 0}
    driver.timing = {"normal": 0.0, "yolo": 0.0}
    driver.get(f"{BASE}/{version}/register")

    driver.send_keys_to(By.ID, "reg-name",     NAME,     element_id="reg-name")
    driver.send_keys_to(By.ID, "reg-email",    EMAIL,    element_id="reg-email")
    driver.send_keys_to(By.ID, "reg-password", PASSWORD, element_id="reg-password")
    driver.click(       By.ID, "reg-btn",                element_id="reg-btn")

    WebDriverWait(driver._driver, 5).until(EC.url_contains("success"))
    return _record(driver, label)


def _record(driver, label: str) -> dict:
    s      = driver.stats
    broken = s["healed"] + s["failed"]
    rate   = int(s["healed"] / broken * 100) if broken else 100
    status = "PASSED" if s["failed"] == 0 else "FAILED"

    print(f"  {label}  [{status}]  "
          f"Selenium: {s['normal']}  YOLOv8: {s['healed']}  "
          f"Recovery: {rate}%")
    return {"label": label, **s, "rate": rate}


def print_table(results: list):
    print("\n")
    print("=" * 72)
    print("  COMPARISON: Standard Selenium vs Self-Healing (YOLOv8)")
    print("=" * 72)
    print(f"  {'Scenario':<32} {'No healing':>10} {'Healed':>8} {'Gain':>8}")
    print("-" * 72)

    for r in results:
        total     = r["normal"] + r["healed"] + r["failed"]
        without   = int(r["normal"] / total * 100) if total else 0
        with_heal = int((r["normal"] + r["healed"]) / total * 100) if total else 0
        gain      = with_heal - without
        gain_str  = f"+{gain}%" if gain > 0 else f"{gain}%"
        print(f"  {r['label']:<32} {without:>9}% {with_heal:>7}% {gain_str:>8}")

    healed_total = sum(r["healed"] for r in results)
    failed_total = sum(r["failed"] for r in results)
    broken_total = healed_total + failed_total
    overall_rate = int(healed_total / broken_total * 100) if broken_total else 100

    print("-" * 72)
    print(f"  {'Overall recovery rate':<32} {' ':>10} {' ':>8} {overall_rate:>7}%")
    print("=" * 72)


def main():
    print("=" * 72)
    print("  Self-Healing Selenium + YOLOv8 — Demo")
    print("=" * 72)
    print("\n  Starting Flask server...")
    start_flask()
    print("  Server ready → http://localhost:5000")

    print("\n  Initializing browser and YOLOv8 model...")
    driver = SelfHealingDriver(headless=True)

    results = []

    print("\n  --- LOGIN FORM SCENARIOS ---\n")
    for version, label in LOGIN_SCENARIOS:
        results.append(run_login(driver, version, label))

    print("\n  --- REGISTRATION FORM SCENARIOS ---\n")
    for version, label in REGISTER_SCENARIOS:
        results.append(run_register(driver, version, label))

    driver.quit()
    print_table(results)
    print("\n  Demo complete.")


if __name__ == "__main__":
    main()
