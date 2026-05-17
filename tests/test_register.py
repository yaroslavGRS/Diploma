"""
Registration tests — demonstrate that self-healing works across all four
DOM mutation types applied to the registration form.

v1/register — stable DOM, Selenium finds all fields normally.
v2/register — renamed IDs, YOLOv8 recovers all 4 elements.
v3/register — renamed IDs + CSS classes, YOLOv8 recovers all 4 elements.
v4/register — wrapper divs around every field, YOLOv8 recovers by position.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE     = "http://localhost:5000"
NAME     = "Test User"
EMAIL    = "test@example.com"
PASSWORD = "pass1234"


def _register(driver, version: str):
    """Reset stats, navigate to form, fill and submit."""
    driver.stats  = {"normal": 0, "healed": 0, "failed": 0}
    driver.timing = {"normal": 0.0, "yolo": 0.0}
    driver.get(f"{BASE}/{version}/register")

    driver.save_detection_visual(
        f"register_{version}",
        f"Register {version}: DOM mutation | Self-healing detection"
    )

    driver.send_keys_to(By.ID, "reg-name",     NAME,     element_id="reg-name")
    driver.send_keys_to(By.ID, "reg-email",    EMAIL,    element_id="reg-email")
    driver.send_keys_to(By.ID, "reg-password", PASSWORD, element_id="reg-password")
    driver.click(       By.ID, "reg-btn",                element_id="reg-btn")

    WebDriverWait(driver._driver, 5).until(EC.url_contains("success"))


def test_register_v1(driver):
    """v1 — stable DOM. Selenium finds all fields without healing."""
    _register(driver, "v1")
    assert "success" in driver.current_url
    s = driver.stats
    assert s["failed"] == 0
    print(f"\n  [register v1] PASSED — Selenium: {s['normal']}, YOLOv8: {s['healed']}")


def test_register_v2(driver):
    """v2 — all IDs renamed. YOLOv8 recovers all 3 inputs and the button."""
    _register(driver, "v2")
    assert "success" in driver.current_url
    s = driver.stats
    assert s["failed"] == 0
    print(f"\n  [register v2] PASSED — Selenium: {s['normal']}, YOLOv8: {s['healed']}")


def test_register_v3(driver):
    """v3 — renamed IDs + CSS classes. YOLOv8 recovers all elements visually."""
    _register(driver, "v3")
    assert "success" in driver.current_url
    s = driver.stats
    assert s["failed"] == 0
    print(f"\n  [register v3] PASSED — Selenium: {s['normal']}, YOLOv8: {s['healed']}")


def test_register_v4(driver):
    """v4 — wrapper divs around every field. YOLOv8 finds elements by visual position."""
    _register(driver, "v4")
    assert "success" in driver.current_url
    s = driver.stats
    assert s["failed"] == 0
    print(f"\n  [register v4] PASSED — Selenium: {s['normal']}, YOLOv8: {s['healed']}")
