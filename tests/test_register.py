"""
Тести реєстрації — демонструють що self-healing працює
на другій тестовій сторінці (не тільки на формі логіну).

v1/register — стабільний DOM, Selenium знаходить всі поля звичайно.
v2/register — перейменовані ID, YOLOv8 відновлює всі 4 елементи.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE     = "http://localhost:5000"
NAME     = "Test User"
EMAIL    = "test@example.com"
PASSWORD = "pass1234"


def test_register_v1(driver):
    """
    Реєстрація на v1 — всі ID існують, Selenium знаходить поля без healing.
    """
    driver.stats  = {"normal": 0, "healed": 0, "failed": 0}
    driver.timing = {"normal": 0.0, "yolo": 0.0}
    driver.get(f"{BASE}/v1/register")

    driver.save_detection_visual("register_v1",
                                 "Register v1: Stable DOM | Selenium finds all fields")

    driver.send_keys_to(By.ID, "reg-name",     NAME,     element_id="reg-name")
    driver.send_keys_to(By.ID, "reg-email",    EMAIL,    element_id="reg-email")
    driver.send_keys_to(By.ID, "reg-password", PASSWORD, element_id="reg-password")
    driver.click(       By.ID, "reg-btn",                element_id="reg-btn")

    WebDriverWait(driver._driver, 5).until(EC.url_contains("success"))

    assert "success" in driver.current_url
    s = driver.stats
    print(f"\n  [register v1] PASSED — Selenium: {s['normal']}, YOLOv8: {s['healed']}")


def test_register_v2(driver):
    """
    Реєстрація на v2 — всі ID перейменовані.
    YOLOv8 відновлює всі 3 inputs і кнопку за візуальним виглядом.
    """
    driver.stats  = {"normal": 0, "healed": 0, "failed": 0}
    driver.timing = {"normal": 0.0, "yolo": 0.0}
    driver.get(f"{BASE}/v2/register")

    driver.save_detection_visual("register_v2",
                                 "Register v2: Mutated DOM | YOLOv8 recovers fields")

    # Ці ID не існують на v2 — спрацює YOLOv8
    driver.send_keys_to(By.ID, "reg-name",     NAME,     element_id="reg-name")
    driver.send_keys_to(By.ID, "reg-email",    EMAIL,    element_id="reg-email")
    driver.send_keys_to(By.ID, "reg-password", PASSWORD, element_id="reg-password")
    driver.click(       By.ID, "reg-btn",                element_id="reg-btn")

    WebDriverWait(driver._driver, 5).until(EC.url_contains("success"))

    assert "success" in driver.current_url
    s = driver.stats
    print(f"\n  [register v2] PASSED — Selenium: {s['normal']}, YOLOv8: {s['healed']}")
