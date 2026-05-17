"""
generate_chart.py — генерує стовпчикову діаграму результатів експерименту.

Запуск: python results/generate_chart.py
Результат: results/chart.png
"""

import matplotlib.pyplot as plt
import numpy as np
import os

OUTPUT = os.path.join(os.path.dirname(__file__), "chart.png")

scenarios  = ["v1\nStable DOM", "v2\nRenamed IDs", "v3\nRenamed Classes",
               "v4\nWrapper Divs", "v5\nCombined"]
without_hl = [100, 0, 0, 0, 0]   # Selenium без healing
with_hl    = [100, 100, 100, 100, 100]  # з self-healing

x     = np.arange(len(scenarios))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))

bars1 = ax.bar(x - width/2, without_hl, width, label="Selenium (no healing)",
               color="#e74c3c", alpha=0.85, edgecolor="white")
bars2 = ax.bar(x + width/2, with_hl,    width, label="Self-Healing (YOLOv8)",
               color="#2ecc71", alpha=0.85, edgecolor="white")

# Підписи значень над стовпцями
for bar in bars1:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, h + 1.5,
            f"{h}%", ha="center", va="bottom", fontsize=11, fontweight="bold")

for bar in bars2:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, h + 1.5,
            f"{h}%", ha="center", va="bottom", fontsize=11, fontweight="bold")

ax.set_xlabel("DOM Mutation Scenario", fontsize=12)
ax.set_ylabel("Test Success Rate (%)", fontsize=12)
ax.set_title("Self-Healing Selenium vs Standard Selenium\nacross 5 DOM Mutation Scenarios",
             fontsize=13, fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels(scenarios, fontsize=10)
ax.set_ylim(0, 115)
ax.set_yticks([0, 25, 50, 75, 100])
ax.legend(fontsize=11)
ax.grid(axis="y", linestyle="--", alpha=0.4)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

plt.tight_layout()
plt.savefig(OUTPUT, dpi=150)
print(f"Chart saved → {OUTPUT}")
