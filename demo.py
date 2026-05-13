"""
demo.py — демонстраційний запуск self-healing фреймворку.

Запуск:
    python demo.py

Що відбувається:
    1. Автоматично запускається Flask-сервер у фоні.
    2. SelfHealingDriver виконує логін на всіх 5 версіях сторінки.
    3. Виводиться таблиця результатів у консоль.
    4. Flask-сервер зупиняється.

Не потрібно нічого запускати вручну — лише python demo.py.
"""

import time
import threading
import subprocess
import sys
import os

# Додаємо корінь проекту до шляху імпорту
sys.path.insert(0, os.path.dirname(__file__))

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from self_healing.driver import SelfHealingDriver

BASE     = "http://localhost:5000"
EMAIL    = "admin@test.com"
PASSWORD = "password123"

SCENARIOS = [
    ("v1", "v1 — стабільний DOM        "),
    ("v2", "v2 — перейменовані ID      "),
    ("v3", "v3 — перейменовані класи   "),
    ("v4", "v4 — wrapper div           "),
    ("v5", "v5 — комбінована мутація   "),
]


def start_flask():
    """Запускає Flask у фоновому потоці."""
    subprocess.Popen(
        [sys.executable, "app/app.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # Чекаємо поки сервер підніметься
    time.sleep(2)


def run_scenario(driver, version: str, label: str) -> dict:
    """Виконує один сценарій і повертає статистику."""
    driver.stats = {"normal": 0, "healed": 0, "failed": 0}
    driver.get(f"{BASE}/{version}/login")

    driver.send_keys_to(By.ID, "email",    EMAIL,    element_id="email")
    driver.send_keys_to(By.ID, "password", PASSWORD, element_id="password")
    driver.click(       By.ID, "login-btn",           element_id="btn")

    WebDriverWait(driver._driver, 5).until(EC.url_contains("success"))

    s      = driver.stats
    broken = s["healed"] + s["failed"]
    rate   = int(s["healed"] / broken * 100) if broken else 100

    status = "✓ PASSED" if s["failed"] == 0 else "✗ FAILED"
    print(f"  {label}  {status}  "
          f"(Selenium: {s['normal']}, YOLOv8: {s['healed']}, "
          f"Recovery: {rate}%)")

    return {"label": label, **s, "rate": rate}


def print_table(results: list):
    """Виводить підсумкову таблицю."""
    print("\n")
    print("=" * 65)
    print("  РЕЗУЛЬТАТИ SELF-HEALING ТЕСТІВ (YOLOv8)")
    print("=" * 65)
    print(f"  {'Сценарій':<30} {'Selenium':>8} {'YOLOv8':>8} {'Fail':>6} {'Rate':>6}")
    print("-" * 65)

    for r in results:
        print(f"  {r['label']:<30} {r['normal']:>8} {r['healed']:>8} "
              f"{r['failed']:>6} {r['rate']:>5}%")

    total_normal = sum(r["normal"] for r in results)
    total_healed = sum(r["healed"] for r in results)
    total_failed = sum(r["failed"] for r in results)
    total_broken = total_healed + total_failed
    total_rate   = int(total_healed / total_broken * 100) if total_broken else 100

    print("-" * 65)
    print(f"  {'РАЗОМ':<30} {total_normal:>8} {total_healed:>8} "
          f"{total_failed:>6} {total_rate:>5}%")
    print("=" * 65)


def main():
    print("=" * 65)
    print("  Self-Healing Selenium + YOLOv8 — Demo")
    print("=" * 65)
    print("\n  Запускаємо Flask-сервер...")
    start_flask()
    print("  Сервер готовий → http://localhost:5000")

    print("\n  Ініціалізуємо браузер і модель YOLOv8...")
    driver = SelfHealingDriver(headless=True)

    print("\n  Запускаємо сценарії:\n")
    results = []
    for version, label in SCENARIOS:
        results.append(run_scenario(driver, version, label))

    driver.quit()
    print_table(results)
    print("\n  Демонстрацію завершено.")


if __name__ == "__main__":
    main()
