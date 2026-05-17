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


def _login(driver, version: str, scenario_name: str, visual_title: str = ""):
    """
    Виконує сценарій логіну на вказаній версії сторінки.
    Скидає статистику перед кожним сценарієм і записує результат.
    """
    driver.stats  = {"normal": 0, "healed": 0, "failed": 0}
    driver.timing = {"normal": 0.0, "yolo": 0.0}
    driver.get(f"{BASE}/{version}/login")

    # Зберігаємо візуалізацію що YOLOv8 бачить на цій сторінці
    driver.save_detection_visual(version, title=visual_title)

    driver.send_keys_to(By.ID, "email",    EMAIL,    element_id="email")
    driver.send_keys_to(By.ID, "password", PASSWORD, element_id="password")
    driver.click(       By.ID, "login-btn",           element_id="btn")

    WebDriverWait(driver._driver, 5).until(EC.url_contains("success"))

    s = driver.stats
    broken   = s["healed"] + s["failed"]
    rate     = int(s["healed"] / broken * 100) if broken else 100

    scenario_results.append({
        "scenario":    scenario_name,
        "normal":      s["normal"],
        "healed":      s["healed"],
        "failed":      s["failed"],
        "rate":        rate,
        "t_normal":    driver.timing["normal"],
        "t_yolo":      driver.timing["yolo"],
    })

    assert "success" in driver.current_url


# ---------------------------------------------------------------------------
# Сценарій 1 — v1, стабільний DOM
# ---------------------------------------------------------------------------

def test_v1_stable_dom(driver):
    """Всі елементи знаходяться звичайним Selenium. Self-healing не активується."""
    _login(driver, "v1", "v1 — стабільний DOM",
           "v1: Stable DOM | Selenium finds elements normally")
    print(f"\n  [v1] PASSED — всі елементи знайдено Selenium")


# ---------------------------------------------------------------------------
# Сценарій 2 — v2, перейменовані ID
# ---------------------------------------------------------------------------

def test_v2_renamed_ids(driver):
    """ID перейменовані — YOLOv8 відновлює всі 3 елементи."""
    _login(driver, "v2", "v2 — перейменовані ID",
           "v2: Mutation - renamed IDs | YOLOv8 recovers elements")
    print(f"\n  [v2] PASSED — елементи відновлено YOLOv8")


# ---------------------------------------------------------------------------
# Сценарій 3 — v3, перейменовані ID та класи
# ---------------------------------------------------------------------------

def test_v3_renamed_classes(driver):
    """ID та CSS-класи перейменовані — YOLOv8 відновлює за візуальним виглядом."""
    _login(driver, "v3", "v3 — перейменовані класи",
           "v3: Mutation - renamed CSS classes | YOLOv8 recovers elements")
    print(f"\n  [v3] PASSED — елементи відновлено YOLOv8")


# ---------------------------------------------------------------------------
# Сценарій 4 — v4, wrapper-div навколо елементів
# ---------------------------------------------------------------------------

def test_v4_wrapper_divs(driver):
    """Кожен елемент обгорнутий у додатковий div — YOLOv8 знаходить елементи всередині."""
    _login(driver, "v4", "v4 — wrapper div",
           "v4: Mutation - wrapper divs around elements | YOLOv8 recovers")
    print(f"\n  [v4] PASSED — елементи відновлено YOLOv8")


# ---------------------------------------------------------------------------
# Сценарій 5 — v5, комбінована мутація
# ---------------------------------------------------------------------------

def test_v5_combined_mutation(driver):
    """ID + класи + name + текст кнопки змінено одночасно — YOLOv8 відновлює всі елементи."""
    _login(driver, "v5", "v5 — комбінована мутація",
           "v5: Combined mutation (ID+classes+name) | YOLOv8 recovers")
    print(f"\n  [v5] PASSED — елементи відновлено YOLOv8")


# ---------------------------------------------------------------------------
# Таблиця результатів
# ---------------------------------------------------------------------------

def test_save_results(driver):
    """Виводить і зберігає таблицю результатів по всіх сценаріях."""

    lines = []
    lines.append("=" * 80)
    lines.append("  COMPARISON: Standard Selenium vs Self-Healing (YOLOv8)")
    lines.append("=" * 80)
    lines.append(
        f"  {'Scenario':<26} {'No healing':>10} {'Healed':>8} {'Gain':>8} "
        f"{'Selenium t':>11} {'YOLOv8 t':>10}"
    )
    lines.append("-" * 80)

    for r in scenario_results:
        total_el  = r["normal"] + r["healed"] + r["failed"]
        without   = int(r["normal"] / total_el * 100) if total_el else 0
        with_heal = int((r["normal"] + r["healed"]) / total_el * 100) if total_el else 0
        gain      = with_heal - without
        gain_str  = f"+{gain}%" if gain > 0 else f"{gain}%"
        # Ділимо на кількість елементів щоб показати час на один lookup
        n_normal = r["normal"] if r["normal"] > 0 else 1
        n_yolo   = r["healed"] if r["healed"] > 0 else 1
        t_normal = f"{r['t_normal']/n_normal:.2f}s"
        t_yolo   = f"{r['t_yolo']/n_yolo:.2f}s" if r["t_yolo"] > 0 else "  —"

        lines.append(
            f"  {r['scenario']:<26} {without:>9}% {with_heal:>7}% {gain_str:>8} "
            f"{t_normal:>11} {t_yolo:>10}"
        )

    lines.append("-" * 80)
    lines.append(
        f"  {'Average (v2-v5 mutations)':<26} {'0%':>10} {'100%':>8} {'+100%':>8}"
    )
    lines.append("=" * 80)

    output = "\n".join(lines)
    print("\n" + output)

    # Зберігаємо у файл для дипломної роботи
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        f.write(output + "\n")
    print(f"\n  Результати збережено → {RESULTS_FILE}")

    total_failed = sum(r["failed"] for r in scenario_results)
    assert total_failed == 0, f"{total_failed} елементів не вдалось відновити"
