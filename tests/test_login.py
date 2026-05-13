"""
Тести логіну що демонструють self-healing через YOLOv8.

Порядок виконання:
1. test_v1_login  — логін на v1, всі селектори працюють звичайно.
2. test_v2_login  — логін на v2, селектори зламані, YOLOv8 відновлює їх.
3. test_results   — виводить таблицю результатів.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE    = "http://localhost:5000"
EMAIL   = "admin@test.com"
PASSWORD = "password123"


# ---------------------------------------------------------------------------
# v1 — звичайний логін (всі ID існують)
# ---------------------------------------------------------------------------

def test_v1_login(driver):
    """
    Selenium знаходить елементи по стандартних ID.
    Self-healing не активується — всі локатори працюють.
    """
    driver.get(f"{BASE}/v1/login")

    driver.send_keys_to(By.ID, "email",     EMAIL,    element_id="email")
    driver.send_keys_to(By.ID, "password",  PASSWORD, element_id="password")
    driver.click(       By.ID, "login-btn",            element_id="btn")

    WebDriverWait(driver._driver, 5).until(EC.url_contains("success"))

    assert "success" in driver.current_url, (
        f"Очікувався редирект на success, отримано: {driver.current_url}"
    )
    print(f"\n  [v1] логін успішний → {driver.current_url}")


# ---------------------------------------------------------------------------
# v2 — логін зі зламаними селекторами (YOLOv8 відновлює)
# ---------------------------------------------------------------------------

def test_v2_login(driver):
    """
    На v2 всі ID перейменовані — Selenium кидає NoSuchElementException.
    SelfHealingDriver перехоплює помилку, запускає YOLOv8,
    знаходить елементи візуально і продовжує тест.
    """
    driver.get(f"{BASE}/v2/login")

    # Ці ID не існують на v2 — спрацює відновлення через YOLOv8
    driver.send_keys_to(By.ID, "email",     EMAIL,    element_id="email")
    driver.send_keys_to(By.ID, "password",  PASSWORD, element_id="password")
    driver.click(       By.ID, "login-btn",            element_id="btn")

    # Чекаємо поки URL зміниться на success — редирект може зайняти момент
    WebDriverWait(driver._driver, 5).until(EC.url_contains("success"))

    assert "success" in driver.current_url, (
        f"Очікувався редирект на success після відновлення, отримано: {driver.current_url}"
    )
    print(f"\n  [v2] логін успішний (відновлено YOLOv8) → {driver.current_url}")


# ---------------------------------------------------------------------------
# Таблиця результатів
# ---------------------------------------------------------------------------

def test_results(driver):
    """Виводить підсумкову таблицю після всіх тестів."""
    s = driver.stats
    total   = s["normal"] + s["healed"] + s["failed"]
    broken  = s["healed"] + s["failed"]   # елементи що потребували відновлення
    rate    = (s["healed"] / broken * 100) if broken else 100

    print("\n")
    print("=" * 50)
    print("  РЕЗУЛЬТАТИ SELF-HEALING ТЕСТІВ")
    print("=" * 50)
    print(f"  Всього звернень до елементів : {total}")
    print(f"  Знайдено звичайним Selenium  : {s['normal']}")
    print(f"  Потребували відновлення      : {broken}")
    print(f"  Відновлено через YOLOv8      : {s['healed']}")
    print(f"  Не вдалось відновити         : {s['failed']}")
    print(f"  Recovery rate                : {rate:.0f}%")
    print("=" * 50)

    assert s["failed"] == 0, f"{s['failed']} елементів не вдалось відновити"
