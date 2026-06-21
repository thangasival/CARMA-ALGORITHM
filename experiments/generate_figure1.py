"""
generate_figure1.py
-------------------
Generates Fig. 1 — CARMA v3 Framework Pipeline (5-step vertical flow)

  Step 1: Intermodal network specification
  Step 2: Parametric MILP budget sweep
  Step 3: Finite-difference MAC estimation
  Step 4: Five-regime classification
  Step 5: Compliance instrument decision

Output:
  paper/figures/fig1_carma_pipeline.png
  paper/figures/fig1_carma_pipeline.pdf
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE    = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "..", "paper", "figures")
os.makedirs(OUT_DIR, exist_ok=True)

# ── canvas ─────────────────────────────────────────────────────────────────────
FW, FH = 8.5, 12.0
fig, ax = plt.subplots(figsize=(FW, FH))
ax.set_xlim(0, FW)
ax.set_ylim(0, FH)
ax.axis("off")
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# ── colour palette (fill, border) ──────────────────────────────────────────────
STEPS = [
    {
        "label":  "Step 1",
        "title":  "Intermodal Network Specification",
        "lines":  [
            "Routes R = {1…|R|}, modes M = {truck, rail, ship, air}",
            "Cost c_{rm} (€)  ·  Emission ef_{rm} (kg CO₂e)",
            "Baseline E₀ = Σ ef_{r,truck} for r ∈ R",
        ],
        "fill":  "#C8E6C9",
        "edge":  "#2E7D32",
    },
    {
        "label":  "Step 2",
        "title":  "Parametric MILP Budget Sweep",
        "lines":  [
            "For r ∈ {0, 5, 10, … , 50}%:",
            "  min  Σ_{r,m} c_{rm} · x_{rm}",
            "  s.t. Σ_{r,m} ef_{rm} · x_{rm} ≤ B(r) = E₀(1 − r/100)",
            "       Σ_m x_{rm} = 1  ∀r ,   x_{rm} ∈ {0,1}",
            "→  Z(r), E(r)  for each budget level  [33 solves / archetype]",
        ],
        "fill":  "#BBDEFB",
        "edge":  "#1565C0",
    },
    {
        "label":  "Step 3",
        "title":  "Finite-Difference MAC Estimation",
        "lines":  [
            "λ̂(r)  =  [Z(r) − Z(r−Δr)] / [E(r−Δr) − E(r)]   (€/kg CO₂e)",
            "B*(r) = λ̂(r) × 1000   (€/t CO₂e — for comparison with π)",
            "Bypasses LP-relaxation duals (zero in all 33 base-archetype solves)",
            "Recovers step-function MAC from sequential integer solutions",
        ],
        "fill":  "#E0F7FA",
        "edge":  "#00695C",
    },
    {
        "label":  "Step 4",
        "title":  "Five-Regime Classification",
        "lines":  [
            "Compare B*(r) against observable carbon price π (e.g. 65 €/t EU ETS):",
            "  R1 — Mode shift preferred    :  λ̂ < 0.90π",
            "  R2 — Parity zone             :  0.90π ≤ λ̂ ≤ 1.10π",
            "  R3 — Allowance pref.         :  λ̂ > 1.10π",
            "  R4 — Co-benefit (non-binding):  E(r) ≤ B(r) without constraint",
            "  R5 — Infeasible              :  no feasible modal assignment exists",
        ],
        "fill":  "#FFF9C4",
        "edge":  "#F57F17",
    },
    {
        "label":  "Step 5",
        "title":  "Compliance Instrument Decision",
        "lines":  [
            "R1 → reconfigure logistics network (physical mode shift)",
            "R2 → margin-neutral; decide on strategic / reliability grounds",
            "R3 → purchase ETS allowances at price π (cheaper than shifting)",
            "R4 → recognise co-benefit; no carbon instrument required",
            "R5 → network redesign or long-haul reconfiguration required",
        ],
        "fill":  "#FCE4EC",
        "edge":  "#C62828",
    },
]

BOX_W  = 6.80   # box width
BOX_H  = 1.70   # box height
CX     = FW / 2  # horizontal centre
GAP    = 0.28   # vertical gap between boxes
TOTAL  = len(STEPS) * BOX_H + (len(STEPS) - 1) * GAP
TOP_Y  = FH - 0.45  # top of first box

def rbox(cx, cy, w, h, title, lines, fc, ec):
    patch = FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.10",
        facecolor=fc, edgecolor=ec, linewidth=2.0, zorder=3,
    )
    ax.add_patch(patch)
    # Title
    ax.text(cx, cy + h / 2 - 0.22, title,
            ha="center", va="top", fontsize=9.5, fontweight="bold",
            color=ec, zorder=4)
    # Body lines
    n = len(lines)
    y_start = cy + h / 2 - 0.48
    step = (h - 0.55) / max(n, 1)
    for i, line in enumerate(lines):
        ax.text(cx, y_start - i * step, line,
                ha="center", va="top", fontsize=7.6, color="#222222",
                fontfamily="monospace", zorder=4)


def draw_arrow(x, y1, y2, color):
    ax.annotate(
        "", xy=(x, y2), xytext=(x, y1),
        arrowprops=dict(
            arrowstyle="->", color=color, lw=2.0,
            connectionstyle="arc3,rad=0.0",
        ),
        zorder=5,
    )


# Draw boxes and arrows
for i, step in enumerate(STEPS):
    cy = TOP_Y - i * (BOX_H + GAP) - BOX_H / 2
    rbox(CX, cy, BOX_W, BOX_H,
         step["title"], step["lines"],
         step["fill"], step["edge"])

    # Step label badge on left margin
    lx = CX - BOX_W / 2 - 0.55
    ax.text(lx, cy, step["label"],
            ha="center", va="center", fontsize=8.5,
            fontweight="bold", color=step["edge"],
            bbox=dict(boxstyle="round,pad=0.25", fc=step["fill"],
                      ec=step["edge"], lw=1.5))

    # Arrow from this box to the next
    if i < len(STEPS) - 1:
        arrow_top = cy - BOX_H / 2
        arrow_bot = arrow_top - GAP
        draw_arrow(CX, arrow_top, arrow_bot, color=step["edge"])

plt.tight_layout(pad=0.3)
path = os.path.join(OUT_DIR, "fig1_carma_pipeline.png")
plt.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
print(f"Saved: {path}")
plt.close()
