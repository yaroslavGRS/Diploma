"""
Тести self-healing Selenium фреймворку.

5 сценаріїв мутацій DOM:
  v1 — стабільний DOM (еталон, без мутацій)
  v2 — перейменовані ID
  v3 — перейменовані ID та CSS-класи
  v4 — wrapper-div навколо елементів
  v5 — комбінована мутація (ID + класи + name + текст кнопки)

Результати зберігаються у results/results_table.txt
"""

import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE     = "http://localhost:5000"
EMAIL    = "admin@test.com"
PASSWORD = "password123"
RESULTS_FILE = os.path.join(os.path.dirname(__file__), "..", "results", "results_table.txt")

# Статистика по кожному сценарію окремо
scenario_results = []


def _login(driver, version: str, scenario_name: str):
    """
    Виконує сценарій логіну на вказаній версії сторінки.
    Скидає статистику перед кожним сценарієм і записує результат.
    """
    driver.stats = {"normal": 0, "healed": 0, "failed": 0}
    driver.get(f"{BASE}/{version}/login")

    driver.send_keys_to(By.ID, "email",    EMAIL,    element_id="email")
    driver.send_keys_to(By.ID, "password", PASSWORD, element_id="password")
    driver.click(       By.ID, "login-btn",           element_id="btn")

    WebDriverWait(driver._driver, 5).until(EC.url_contains("success"))

    s = driver.stats
    broken   = s["healed"] + s["failed"]
    rate     = int(s["healed"] / broken * 100) if broken else 100

    scenario_results.append({
        "scenario": scenario_name,
        "normal":   s["normal"],
        "healed":   s["healed"],
        "failed":   s["failed"],
        "rate":     rate,
    })

    assert "success" in driver.current_url


# ---------------------------------------------------------------------------
# Сценарій 1 — v1, стабільний DOM
# ---------------------------------------------------------------------------

def test_v1_stable_dom(driver):
    """Всі елементи знаходяться звичайним Selenium. Self-healing не активується."""
    _login(driver, "v1", "v1 — стабільний DOM")
    print(f"\n  [v1] PASSED — всі елементи знайдено Selenium")


# ---------------------------------------------------------------------------
# Сценарій 2 — v2, перейменовані ID
# ---------------------------------------------------------------------------

def test_v2_renamed_ids(driver):
    """ID перейменовані — YOLOv8 відновлює всі 3 елементи."""
    _login(driver, "v2", "v2 — перейменовані ID")
    print(f"\n  [v2] PASSED — елементи відновлено YOLOv8")


# ---------------------------------------------------------------------------
# Сценарій 3 — v3, перейменовані ID та класи
# ---------------------------------------------------------------------------

def test_v3_renamed_classes(driver):
    """ID та CSS-класи перейменовані — YOLOv8 відновлює за візуальним виглядом."""
    _login(driver, "v3", "v3 — перейменовані класи")
    print(f"\n  [v3] PASSED — елементи відновлено YOLOv8")


# ---------------------------------------------------------------------------
# Сценарій 4 — v4, wrapper-div навколо елементів
# ---------------------------------------------------------------------------

def test_v4_wrapper_divs(driver):
    """Кожен елемент обгорнутий у додатковий div — YOLOv8 знаходить елементи всередині."""
    _login(driver, "v4", "v4 — wrapper div")
    print(f"\n  [v4] PASSED — елементи відновлено YOLOv8")


# ---------------------------------------------------------------------------
# Сценарій 5 — v5, комбінована мутація
# ---------------------------------------------------------------------------

def test_v5_combined_mutation(driver):
    """ID + класи + name + текст кнопки змінено одночасно — YOLOv8 відновлює всі елементи."""
    _login(driver, "v5", "v5 — комбінована мутація")
    print(f"\n  [v5] PASSED — елементи відновлено YOLOv8")


# ---------------------------------------------------------------------------
# Таблиця результатів
# ---------------------------------------------------------------------------

def test_save_results(driver):
    """Виводить і зберігає таблицю результатів по всіх сценаріях."""

    lines = []
    lines.append("=" * 65)
    lines.append("  РЕЗУЛЬТАТИ SELF-HEALING ТЕСТІВ (YOLOv8)")
    lines.append("=" * 65)
    lines.append(f"  {'Сценарій':<30} {'Selenium':>8} {'YOLOv8':>8} {'Fail':>6} {'Rate':>6}")
    lines.append("-" * 65)

    for r in scenario_results:
        lines.append(
            f"  {r['scenario']:<30} {r['normal']:>8} {r['healed']:>8} "
            f"{r['failed']:>6} {r['rate']:>5}%"
        )

    total_normal = sum(r["normal"] for r in scenario_results)
    total_healed = sum(r["healed"] for r in scenario_results)
    total_failed = sum(r["failed"] for r in scenario_results)
    total_broken = total_healed + total_failed
    total_rate   = int(total_healed / total_broken * 100) if total_broken else 100

    lines.append("-" * 65)
    lines.append(
        f"  {'РАЗОМ':<30} {total_normal:>8} {total_healed:>8} "
        f"{total_failed:>6} {total_rate:>5}%"
    )
    lines.append("=" * 65)

    output = "\n".join(lines)
    print("\n" + output)

    # Зберігаємо у файл для дипломної роботи
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        f.write(output + "\n")
    print(f"\n  Результати збережено → {RESULTS_FILE}")

    assert total_failed == 0, f"{total_failed} елементів не вдалось відновити"
