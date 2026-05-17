"""
threshold_experiment.py — експеримент з порогом впевненості YOLOv8.

Запускає детекцію на сторінках v2-v5 при різних значеннях conf (0.1 — 0.9).
Показує як поріг впевненості впливає на кількість знайдених елементів
і recovery rate системи.

Запуск (Flask має бути запущений):
    python results/threshold_experiment.py
"""

import sys
import os
import time
import numpy as np
import cv2
import matplotlib.pyplot as plt
from ultralytics import YOLO
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

MODEL_PATH   = os.path.join(os.path.dirname(__file__), "..", "best.pt")
OUTPUT_TABLE = os.path.join(os.path.dirname(__file__), "threshold_table.txt")
OUTPUT_CHART = os.path.join(os.path.dirname(__file__), "threshold_chart.png")
BASE         = "http://localhost:5000"

# Порогові значення для експерименту
THRESHOLDS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

# Які класи і скільки їх має бути на сторінці логіну
EXPECTED = {"input": 2, "Button": 1}
TOTAL_ELEMENTS = sum(EXPECTED.values())  # 3

# Тестуємо на v2 (зламані селектори — реальний сценарій healing)
TEST_URL = f"{BASE}/v2/login"


def take_screenshot(url: str) -> np.ndarray:
    """Відкриває сторінку в headless Chrome і робить скріншот."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,800")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(1)
    png = driver.get_screenshot_as_png()
    driver.quit()
    return cv2.imdecode(np.frombuffer(png, np.uint8), cv2.IMREAD_COLOR)


def run_experiment(screenshot: np.ndarray, model: YOLO):
    """
    Запускає детекцію при кожному пороговому значенні.
    Повертає список словників з результатами.
    """
    results = []

    for conf in THRESHOLDS:
        detections = model(screenshot, conf=conf, verbose=False)

        # Рахуємо знайдені елементи по класах
        found = {"input": 0, "Button": 0, "Dropdown": 0}
        for box in detections[0].boxes:
            cls = model.names[int(box.cls)]
            if cls in found:
                found[cls] += 1

        # Recovery rate = скільки з потрібних елементів знайдено
        recovered = min(found["input"], EXPECTED["input"]) + \
                    min(found["Button"], EXPECTED["Button"])
        rate = int(recovered / TOTAL_ELEMENTS * 100)

        results.append({
            "conf":      conf,
            "inputs":    found["input"],
            "buttons":   found["Button"],
            "recovered": recovered,
            "rate":      rate,
            "total":     sum(found.values()),
        })

        print(f"  conf={conf:.1f} | inputs={found['input']} "
              f"buttons={found['Button']} | recovery={rate}%")

    return results


def save_table(results: list):
    lines = []
    lines.append("=" * 65)
    lines.append("  CONFIDENCE THRESHOLD EXPERIMENT (YOLOv8 on v2 page)")
    lines.append("=" * 65)
    lines.append(f"  {'Threshold':>10} {'Inputs':>8} {'Buttons':>9} "
                 f"{'Recovered':>10} {'Rate':>7}")
    lines.append("-" * 65)
    for r in results:
        lines.append(f"  {r['conf']:>10.1f} {r['inputs']:>8} {r['buttons']:>9} "
                     f"{r['recovered']:>10} {r['rate']:>6}%")
    lines.append("=" * 65)
    output = "\n".join(lines)
    print("\n" + output)
    with open(OUTPUT_TABLE, "w", encoding="utf-8") as f:
        f.write(output + "\n")
    print(f"\n  Table saved → {OUTPUT_TABLE}")


def save_chart(results: list):
    confs = [r["conf"] for r in results]
    rates = [r["rate"] for r in results]
    total = [r["total"] for r in results]

    fig, ax1 = plt.subplots(figsize=(10, 5))

    color1 = "#2ecc71"
    color2 = "#3498db"

    ax1.plot(confs, rates, "o-", color=color1, linewidth=2.5,
             markersize=8, label="Recovery Rate (%)")
    ax1.set_xlabel("Confidence Threshold", fontsize=12)
    ax1.set_ylabel("Recovery Rate (%)", color=color1, fontsize=12)
    ax1.tick_params(axis="y", labelcolor=color1)
    ax1.set_ylim(-5, 115)
    ax1.set_xticks(confs)
    ax1.axhline(y=100, color=color1, linestyle="--", alpha=0.3)
    ax1.axvline(x=0.3, color="gray", linestyle=":", alpha=0.5,
                label="Default threshold (0.3)")

    # Друга вісь — загальна кількість детекцій
    ax2 = ax1.twinx()
    ax2.bar(confs, total, width=0.04, color=color2, alpha=0.3,
            label="Total detections")
    ax2.set_ylabel("Total detections", color=color2, fontsize=12)
    ax2.tick_params(axis="y", labelcolor=color2)

    # Підписи recovery rate на точках
    for conf, rate in zip(confs, rates):
        ax1.annotate(f"{rate}%", (conf, rate),
                     textcoords="offset points", xytext=(0, 10),
                     ha="center", fontsize=9, color=color1)

    ax1.set_title("Effect of Confidence Threshold on Recovery Rate\n"
                  "(YOLOv8 detection on mutated DOM — v2 page)",
                  fontsize=13, fontweight="bold")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower left", fontsize=10)

    ax1.grid(axis="y", linestyle="--", alpha=0.3)
    fig.tight_layout()
    plt.savefig(OUTPUT_CHART, dpi=150)
    print(f"  Chart saved → {OUTPUT_CHART}")


def main():
    print("=" * 65)
    print("  Confidence Threshold Experiment")
    print("=" * 65)
    print(f"\n  Taking screenshot of {TEST_URL} ...")
    screenshot = take_screenshot(TEST_URL)

    print("  Loading YOLOv8 model ...")
    model = YOLO(MODEL_PATH)

    print(f"\n  Running detection at {len(THRESHOLDS)} threshold values:\n")
    results = run_experiment(screenshot, model)

    save_table(results)
    save_chart(results)
    print("\n  Experiment complete.")


if __name__ == "__main__":
    main()
