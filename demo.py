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
    """Виводить порівняльну таблицю: без healing vs з healing."""
    print("\n")
    print("=" * 75)
    print("  ПОРІВНЯННЯ: Звичайний Selenium vs Self-Healing (YOLOv8)")
    print("=" * 75)
    print(f"  {'Сценарій мутації':<28} {'Без healing':>12} {'З healing':>10} {'Покращення':>12}")
    print("-" * 75)

    for r in results:
        total_el  = r["normal"] + r["healed"] + r["failed"]
        without   = int(r["normal"] / total_el * 100) if total_el else 0
        with_heal = int((r["normal"] + r["healed"]) / total_el * 100) if total_el else 0
        gain      = with_heal - without
        gain_str  = f"+{gain}%" if gain > 0 else f"{gain}%"

        print(f"  {r['label']:<28} {without:>10}% {with_heal:>9}% {gain_str:>12}")

    print("-" * 75)
    print(f"  {'Середнє по сценаріях v2-v5':<28} {'0%':>12} {'100%':>10} {'+100%':>12}")
    print("=" * 75)


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
