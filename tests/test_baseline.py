"""
Baseline tests — standard Selenium WITHOUT self-healing.

Purpose: demonstrate that without YOLOv8 recovery, standard Selenium
fails completely on every mutated page (v2–v5 login, v2–v4 register,
v2–v3 search). Only the stable v1 pages pass.

This is the control group that justifies the self-healing approach.

Run separately (uses plain webdriver, not the SelfHealingDriver fixture):
    pytest tests/test_baseline.py -v
"""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException

BASE      = "http://localhost:5000"
EMAIL     = "admin@test.com"
PASSWORD  = "password123"
NAME      = "Test User"
REG_EMAIL = "test@example.com"
QUERY     = "laptop"


@pytest.fixture(scope="module")
def plain_driver():
    """Standard Selenium driver — no self-healing."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,800")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


def _try_login(driver, version: str) -> bool:
    """Returns True if login redirected to success, False on element or timeout error."""
    start_url = f"{BASE}/{version}/login"
    driver.get(start_url)
    try:
        driver.find_element(By.ID, "email").send_keys(EMAIL)
        driver.find_element(By.ID, "password").send_keys(PASSWORD)
        driver.find_element(By.ID, "login-btn").click()
        WebDriverWait(driver, 3).until(lambda d: d.current_url != start_url)
        return "success" in driver.current_url
    except (NoSuchElementException, TimeoutException):
        return False


def _try_register(driver, version: str) -> bool:
    """Returns True if registration redirected to success, False on element or timeout error."""
    start_url = f"{BASE}/{version}/register"
    driver.get(start_url)
    try:
        driver.find_element(By.ID, "reg-name").send_keys(NAME)
        driver.find_element(By.ID, "reg-email").send_keys(REG_EMAIL)
        driver.find_element(By.ID, "reg-password").send_keys(PASSWORD)
        driver.find_element(By.ID, "reg-btn").click()
        WebDriverWait(driver, 3).until(lambda d: d.current_url != start_url)
        return "success" in driver.current_url
    except (NoSuchElementException, TimeoutException):
        return False


def _try_search(driver, version: str) -> bool:
    """Returns True if search redirected to success, False on element or timeout error."""
    start_url = f"{BASE}/{version}/search"
    driver.get(start_url)
    try:
        driver.find_element(By.ID, "search-query").send_keys(QUERY)
        driver.find_element(By.ID, "search-btn").click()
        WebDriverWait(driver, 3).until(lambda d: d.current_url != start_url)
        return "success" in driver.current_url
    except (NoSuchElementException, TimeoutException):
        return False


# -----------------------------------------------------------------------
# Login baseline tests
# -----------------------------------------------------------------------

def test_baseline_login_v1_passes(plain_driver):
    """v1 stable DOM — standard Selenium PASSES (control)."""
    result = _try_login(plain_driver, "v1")
    assert result is True, "v1 should pass with standard Selenium"


def test_baseline_login_v2_fails(plain_driver):
    """v2 renamed IDs — standard Selenium FAILS (no healing available)."""
    result = _try_login(plain_driver, "v2")
    assert result is False, "v2 must fail with standard Selenium (proves healing is needed)"


def test_baseline_login_v3_fails(plain_driver):
    """v3 renamed classes — standard Selenium FAILS."""
    result = _try_login(plain_driver, "v3")
    assert result is False, "v3 must fail with standard Selenium"


def test_baseline_login_v4_fails(plain_driver):
    """v4 wrapper divs — standard Selenium FAILS."""
    result = _try_login(plain_driver, "v4")
    assert result is False, "v4 must fail with standard Selenium"


def test_baseline_login_v5_fails(plain_driver):
    """v5 combined mutation — standard Selenium FAILS."""
    result = _try_login(plain_driver, "v5")
    assert result is False, "v5 must fail with standard Selenium"


# -----------------------------------------------------------------------
# Register baseline tests
# -----------------------------------------------------------------------

def test_baseline_register_v1_passes(plain_driver):
    """Register v1 stable DOM — standard Selenium PASSES."""
    result = _try_register(plain_driver, "v1")
    assert result is True, "register v1 should pass with standard Selenium"


def test_baseline_register_v2_fails(plain_driver):
    """Register v2 renamed IDs — standard Selenium FAILS."""
    result = _try_register(plain_driver, "v2")
    assert result is False, "register v2 must fail with standard Selenium"


def test_baseline_register_v3_fails(plain_driver):
    """Register v3 renamed classes — standard Selenium FAILS."""
    result = _try_register(plain_driver, "v3")
    assert result is False, "register v3 must fail with standard Selenium"


def test_baseline_register_v4_fails(plain_driver):
    """Register v4 wrapper divs — standard Selenium FAILS."""
    result = _try_register(plain_driver, "v4")
    assert result is False, "register v4 must fail with standard Selenium"


# -----------------------------------------------------------------------
# Search baseline tests
# -----------------------------------------------------------------------

def test_baseline_search_v1_passes(plain_driver):
    """Search v1 stable DOM — standard Selenium PASSES."""
    result = _try_search(plain_driver, "v1")
    assert result is True, "search v1 should pass with standard Selenium"


def test_baseline_search_v2_fails(plain_driver):
    """Search v2 renamed IDs — standard Selenium FAILS."""
    result = _try_search(plain_driver, "v2")
    assert result is False, "search v2 must fail with standard Selenium"


def test_baseline_search_v3_fails(plain_driver):
    """Search v3 combined mutation — standard Selenium FAILS."""
    result = _try_search(plain_driver, "v3")
    assert result is False, "search v3 must fail with standard Selenium"
