"""
generate_architecture.py — generates a system architecture flowchart.

Shows the self-healing flow:
  Selenium test → find_element() → [success] return element
                                 → [fail] YOLOv8 → [found] return element
                                                  → [not found] raise exception

Run: python results/generate_architecture.py
Output: results/architecture.png
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUTPUT = "results/architecture.png"

fig, ax = plt.subplots(1, 1, figsize=(14, 10))
ax.set_xlim(0, 14)
ax.set_ylim(-0.6, 9.2)
ax.axis("off")
fig.patch.set_facecolor("#f8f9fa")

# ------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------

def box(ax, x, y, w, h, text, color, textcolor="white", fontsize=10, radius=0.3):
    fancy = FancyBboxPatch((x - w/2, y - h/2), w, h,
                           boxstyle=f"round,pad=0.05,rounding_size={radius}",
                           facecolor=color, edgecolor="white", linewidth=1.5, zorder=3)
    ax.add_patch(fancy)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            color=textcolor, fontweight="bold", zorder=4,
            wrap=True, multialignment="center")

def diamond(ax, x, y, w, h, text, color, fontsize=9):
    dx, dy = w/2, h/2
    pts = [(x, y+dy), (x+dx, y), (x, y-dy), (x-dx, y)]
    diamond_patch = plt.Polygon(pts, closed=True, facecolor=color,
                                edgecolor="white", linewidth=1.5, zorder=3)
    ax.add_patch(diamond_patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            color="white", fontweight="bold", zorder=4, multialignment="center")

def arrow(ax, x1, y1, x2, y2, label="", color="#555"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color,
                                lw=1.8, mutation_scale=18), zorder=2)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx + 0.1, my, label, fontsize=8.5, color=color,
                ha="left", va="center", style="italic")

# ------------------------------------------------------------------
# Title
# ------------------------------------------------------------------
ax.text(7, 8.6, "Self-Healing Selenium + YOLOv8 — System Architecture",
        ha="center", va="center", fontsize=13, fontweight="bold", color="#1a1a2e")

# ------------------------------------------------------------------
# Nodes
# ------------------------------------------------------------------

# 1. Selenium Test
box(ax, 2.2, 7.5, 2.8, 0.75, "Selenium Test\n(pytest)", "#2c3e50", fontsize=9)

# 2. find_element()
box(ax, 2.2, 6.2, 2.8, 0.75, "find_element(By.ID, value)", "#2980b9", fontsize=9)

# 3. Decision: found?
diamond(ax, 2.2, 4.9, 2.6, 0.9, "Element\nfound?", "#8e44ad", fontsize=9)

# 4. Return element (success path)
box(ax, 5.2, 4.9, 2.4, 0.7, "Return Element\n✓ Test continues", "#27ae60", fontsize=9)

# 5. Screenshot
box(ax, 2.2, 3.5, 2.8, 0.75, "Take page\nscreenshot", "#e67e22", fontsize=9)

# 6. YOLOv8
box(ax, 2.2, 2.3, 2.8, 0.75, "YOLOv8 Detection\n(conf ≥ 0.3)", "#c0392b", fontsize=9)

# 7. Decision: match found?
diamond(ax, 2.2, 1.1, 2.6, 0.9, "Match\nfound?", "#8e44ad", fontsize=9)

# 8. elementFromPoint
box(ax, 5.2, 1.1, 2.6, 0.7, "document.\nelementFromPoint(cx, cy)", "#27ae60", fontsize=9)

# 9. Raise exception
box(ax, 2.2, -0.1, 2.8, 0.65, "Raise Exception\n✗ Test fails", "#7f8c8d", fontsize=9)

# ------------------------------------------------------------------
# Right side: components
# ------------------------------------------------------------------

# Flask app box
box(ax, 10.5, 7.0, 4.5, 1.2,
    "Flask Web Application\n/v1/login  /v2/login\n/v1/register  /v2/register",
    "#16a085", fontsize=8.5)

# Dataset box
box(ax, 10.5, 5.3, 4.5, 1.1,
    "YOLOv8n Model  (best.pt)\nTrained on 459 images\nClasses: Button | input | Dropdown",
    "#c0392b", fontsize=8.5)

# Stats box
box(ax, 10.5, 3.7, 4.5, 1.0,
    "Results & Metrics\nmAP@50: 0.668 | Precision: 0.631\nRecovery Rate: 100%",
    "#2980b9", fontsize=8.5)

# Legend
legend_items = [
    ("#2c3e50", "Test / Driver logic"),
    ("#27ae60", "Success path"),
    ("#c0392b", "YOLOv8 component"),
    ("#8e44ad", "Decision point"),
    ("#7f8c8d", "Failure path"),
]
for i, (color, label) in enumerate(legend_items):
    lx, ly = 8.2, 2.2 - i * 0.42
    fancy = FancyBboxPatch((lx, ly - 0.13), 0.3, 0.28,
                           boxstyle="round,pad=0.02",
                           facecolor=color, edgecolor="none", zorder=3)
    ax.add_patch(fancy)
    ax.text(lx + 0.45, ly + 0.01, label, fontsize=8.5, va="center", color="#333")

ax.text(8.2, 2.55, "Legend:", fontsize=9, fontweight="bold", color="#333")

# ------------------------------------------------------------------
# Arrows — main flow
# ------------------------------------------------------------------
arrow(ax, 2.2, 7.12, 2.2, 6.58, color="#2c3e50")
arrow(ax, 2.2, 5.83, 2.2, 5.35, color="#2980b9")

# Yes → return element
arrow(ax, 3.5, 4.9, 4.0, 4.9, label="Yes", color="#27ae60")

# No → screenshot
arrow(ax, 2.2, 4.45, 2.2, 3.88, label="No", color="#e67e22")

arrow(ax, 2.2, 3.12, 2.2, 2.68, color="#e67e22")
arrow(ax, 2.2, 1.93, 2.2, 1.55, color="#c0392b")

# Yes → elementFromPoint
arrow(ax, 3.5, 1.1, 3.92, 1.1, label="Yes", color="#27ae60")

# No → raise
arrow(ax, 2.2, 0.65, 2.2, 0.22, label="No", color="#7f8c8d")

# elementFromPoint → return (loop back)
ax.annotate("", xy=(5.2, 4.55), xytext=(5.2, 1.45),
            arrowprops=dict(arrowstyle="-|>", color="#27ae60",
                            lw=1.8, mutation_scale=18), zorder=2)
ax.text(5.55, 3.0, "Return\nHealed\nElement", fontsize=8, color="#27ae60",
        ha="left", va="center", style="italic")

# Dashed line: test calls Flask
ax.annotate("", xy=(8.2, 7.0), xytext=(3.6, 7.5),
            arrowprops=dict(arrowstyle="-|>", color="#16a085",
                            lw=1.5, linestyle="dashed", mutation_scale=15), zorder=2)
ax.text(5.8, 7.4, "HTTP request", fontsize=8, color="#16a085", style="italic")

# Dashed line: YOLOv8 uses model
ax.annotate("", xy=(8.2, 5.3), xytext=(3.6, 2.3),
            arrowprops=dict(arrowstyle="-|>", color="#c0392b",
                            lw=1.5, linestyle="dashed", mutation_scale=15), zorder=2)
ax.text(5.5, 3.9, "loads model", fontsize=8, color="#c0392b", style="italic")

plt.tight_layout()
plt.savefig(OUTPUT, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
print(f"Architecture diagram saved → {OUTPUT}")
