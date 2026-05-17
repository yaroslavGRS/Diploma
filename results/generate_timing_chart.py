"""
generate_timing_chart.py — comparison of average lookup time:
  Standard Selenium  vs  YOLOv8 self-healing fallback.

Shows the overhead cost of visual recovery and justifies why
Selenium is tried first (fast path) before invoking YOLOv8.

Run: python results/generate_timing_chart.py
Output: results/timing_chart.png
"""

import sys
import os
import time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from selenium.webdriver.common.by import By
from self_healing.driver import SelfHealingDriver

BASE    = "http://localhost:5000"
OUTPUT  = os.path.join(os.path.dirname(__file__), "timing_chart.png")
RUNS    = 5   # number of repetitions per scenario for stable averages

SCENARIOS = [
    # (url, element_id_list, label)
    ("/v1/login",    ["email", "password", "btn"],                        "Login v1\n(Selenium)"),
    ("/v2/login",    ["email", "password", "btn"],                        "Login v2\n(YOLOv8)"),
    ("/v1/register", ["reg-name", "reg-email", "reg-password", "reg-btn"], "Register v1\n(Selenium)"),
    ("/v2/register", ["reg-name", "reg-email", "reg-password", "reg-btn"], "Register v2\n(YOLOv8)"),
    ("/v1/search",   ["search-query", "search-category", "search-btn"],   "Search v1\n(Selenium)"),
    ("/v2/search",   ["search-query", "search-category", "search-btn"],   "Search v2\n(YOLOv8)"),
]


def measure_scenario(driver, url, element_ids, runs):
    """Run one scenario `runs` times, return (avg_selenium_ms, avg_yolo_ms, avg_total_ms)."""
    selenium_times, yolo_times = [], []

    for _ in range(runs):
        driver.stats  = {"normal": 0, "healed": 0, "failed": 0}
        driver.timing = {"normal": 0.0, "yolo": 0.0}
        driver.get(f"{BASE}{url}")

        for eid in element_ids:
            try:
                driver.find_element(By.ID, eid, element_id=eid)
            except Exception:
                pass

        selenium_times.append(driver.timing["normal"] * 1000)
        yolo_times.append(driver.timing["yolo"] * 1000)

    return np.mean(selenium_times), np.mean(yolo_times)


def main():
    print("Starting Flask must be running at http://localhost:5000")
    print("Initializing driver...")
    driver = SelfHealingDriver(headless=True)

    selenium_avgs, yolo_avgs, labels = [], [], []

    for url, eids, label in SCENARIOS:
        print(f"  Measuring: {label.replace(chr(10), ' ')} ({RUNS} runs)...")
        sel_ms, yolo_ms = measure_scenario(driver, url, eids, RUNS)
        selenium_avgs.append(sel_ms)
        yolo_avgs.append(yolo_ms)
        labels.append(label)

    driver.quit()

    # -----------------------------------------------------------------------
    # Plot
    # -----------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(13, 6))
    fig.patch.set_facecolor("#f8f9fa")
    ax.set_facecolor("#ffffff")

    x      = np.arange(len(labels))
    width  = 0.35

    bars1 = ax.bar(x - width/2, selenium_avgs, width,
                   label="Standard Selenium lookup (ms)",
                   color="#2980b9", alpha=0.88, edgecolor="white", linewidth=0.8)
    bars2 = ax.bar(x + width/2, yolo_avgs, width,
                   label="YOLOv8 visual recovery (ms)",
                   color="#c0392b", alpha=0.88, edgecolor="white", linewidth=0.8)

    # Value labels on top of each bar
    for bar in bars1:
        h = bar.get_height()
        if h > 0.5:
            ax.text(bar.get_x() + bar.get_width()/2, h + 2,
                    f"{h:.0f}", ha="center", va="bottom", fontsize=8, color="#2980b9")

    for bar in bars2:
        h = bar.get_height()
        if h > 0.5:
            ax.text(bar.get_x() + bar.get_width()/2, h + 2,
                    f"{h:.0f}", ha="center", va="bottom", fontsize=8, color="#c0392b")

    ax.set_xlabel("Test scenario", fontsize=11)
    ax.set_ylabel("Average time per scenario (ms)", fontsize=11)
    ax.set_title("Lookup Time: Standard Selenium vs YOLOv8 Visual Recovery",
                 fontsize=13, fontweight="bold", pad=14)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.legend(fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.spines[["top", "right"]].set_visible(False)

    note = (f"Each bar = average over {RUNS} runs.\n"
            "Stable pages (v1): YOLOv8 not invoked → bar is 0.\n"
            "Mutated pages (v2+): Selenium fails fast, YOLOv8 does visual search.")
    fig.text(0.5, -0.04, note, ha="center", fontsize=8.5, color="#666",
             style="italic")

    plt.tight_layout()
    plt.savefig(OUTPUT, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"\nTiming chart saved → {OUTPUT}")


if __name__ == "__main__":
    main()
