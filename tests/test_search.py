"""
Search form tests — demonstrate self-healing on a third form type (search with dropdown).

v1/search — stable DOM, Selenium finds query input and button normally.
v2/search — renamed IDs, YOLOv8 recovers input and button visually.
v3/search — combined mutation (IDs + classes + wrappers), YOLOv8 recovers both elements.

Note: The YOLOv8 model detects custom UI components (Button, input, Dropdown).
Native HTML <select> elements are not reliably detected as Dropdown because the
training dataset contained custom-styled dropdowns, not browser-native select boxes.
This is a known limitation discussed in the thesis. The dropdown category field
on the search form uses its default empty value — the form submits successfully
based on the search query alone.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

BASE  = "http://localhost:5000"
QUERY = "laptop"


def _search(driver, version: str):
    """Reset stats, navigate, type search query, click button."""
    driver.stats  = {"normal": 0, "healed": 0, "failed": 0}
    driver.timing = {"normal": 0.0, "yolo": 0.0}
    driver.get(f"{BASE}/{version}/search")

    driver.send_keys_to(By.ID, "search-query", QUERY, element_id="search-query")
    driver.click(By.ID, "search-btn", element_id="search-btn")

    WebDriverWait(driver._driver, 5).until(
        lambda d: "search-success" in d.current_url or "success" in d.current_url
    )


def test_search_v1(driver):
    """v1 — stable DOM. Selenium finds query input and search button."""
    _search(driver, "v1")
    assert "success" in driver.current_url
    s = driver.stats
    assert s["failed"] == 0
    print(f"\n  [search v1] PASSED — Selenium: {s['normal']}, YOLOv8: {s['healed']}")


def test_search_v2(driver):
    """v2 — renamed IDs. YOLOv8 recovers query input and button visually."""
    _search(driver, "v2")
    assert "success" in driver.current_url
    s = driver.stats
    assert s["failed"] == 0
    print(f"\n  [search v2] PASSED — Selenium: {s['normal']}, YOLOv8: {s['healed']}")


def test_search_v3(driver):
    """v3 — combined mutation (IDs + classes + wrapper divs).
    YOLOv8 recovers both elements despite all three change types applied at once."""
    _search(driver, "v3")
    assert "success" in driver.current_url
    s = driver.stats
    assert s["failed"] == 0
    print(f"\n  [search v3] PASSED — Selenium: {s['normal']}, YOLOv8: {s['healed']}")
