"""
Negative tests — verify that the self-healing framework does NOT
hallucinate elements that genuinely do not exist on the page.

If an element is not found by Selenium AND YOLOv8 cannot locate a
matching visual element, the framework must raise NoSuchElementException
instead of silently returning a wrong element.

This demonstrates that self-healing is safe and predictable —
it only recovers when there is a real visual match.
"""

import pytest
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


BASE = "http://localhost:5000"


def test_nonexistent_element_raises(driver):
    """
    Searching for an element whose ID has never existed and whose
    logical name is not in ELEMENT_MAP must raise NoSuchElementException.
    The framework must not silently swallow the error.
    """
    driver.get(f"{BASE}/v1/login")

    with pytest.raises(NoSuchElementException):
        # "ghost-element" is not in ELEMENT_MAP and does not exist in DOM
        driver.find_element(By.ID, "ghost-element")


def test_wrong_element_id_not_in_map_raises(driver):
    """
    An element_id that is NOT registered in ELEMENT_MAP triggers the
    'not in ELEMENT_MAP' branch and falls through to raise the original
    NoSuchElementException.
    """
    driver.get(f"{BASE}/v1/login")

    with pytest.raises(NoSuchElementException):
        # 'xyz-field' does not exist in DOM or in ELEMENT_MAP
        driver.find_element(By.ID, "xyz-field", element_id="xyz-field")


def test_healing_does_not_affect_stable_page(driver):
    """
    On a stable page (v1), all elements are found by standard Selenium.
    The healed counter must remain 0 — YOLOv8 is never invoked.
    """
    driver.stats  = {"normal": 0, "healed": 0, "failed": 0}
    driver.timing = {"normal": 0.0, "yolo": 0.0}
    driver.get(f"{BASE}/v1/login")

    driver.find_element(By.ID, "email",     element_id="email")
    driver.find_element(By.ID, "password",  element_id="password")
    driver.find_element(By.ID, "login-btn", element_id="btn")

    assert driver.stats["healed"] == 0, "YOLOv8 must not be triggered on a stable page"
    assert driver.stats["normal"] == 3, "All 3 elements must be found by standard Selenium"
