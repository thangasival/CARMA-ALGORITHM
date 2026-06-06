"""
generate_figure1.py
-------------------
Generates Fig. 1 — CARMA Six-Phase Pipeline Architecture
Style modelled after Sánchez-Pravos et al. (Supply Chain Analytics 2025, gr1.jpg):
  • Left-side coloured italic layer labels + thin grey separator
  • Rounded-rect boxes with light fills / coloured borders per phase
  • Solid arrows for main flow; dashed blue arrow for MAPE feedback
  • White background, 300 dpi PNG + PDF

Output:
  paper/figures/fig1_carma_pipeline.png
  paper/figures/fig1_carma_pipeline.pdf
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe

# ── paths ─────────────────────────────────────────────────────────────────────
HERE    = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "..", "paper", "figures")
os.makedirs(OUT_DIR, exist_ok=True)

# ── canvas ────────────────────────────────────────────────────────────────────
FW, FH = 9.2, 13.6
fig, ax = plt.subplots(figsize=(FW, FH))
ax.set_xlim(0, FW)
ax.set_ylim(0, FH)
ax.axis("off")
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# ── colour palette (fill, border) ─────────────────────────────────────────────
C = {
    "inp":  ("#C8E6C9", "#2E7D32"),
    "piem": ("#BBDEFB", "#1565C0"),
    "ml":   ("#FFE0B2", "#E65100"),
    "milp": ("#E0F7FA", "#00695C"),
    "dcct": ("#FFF9C4", "#F57F17"),
    "ns3":  ("#C8E6C9", "#2E7D32"),
    "ci":   ("#FFE0B2", "#E65100"),
    "out":  ("#FCE4EC", "#C62828"),
}

# ── layout constants ─────────────────────────────────────────────────────────
LBL_X  = 0.05    # left edge of layer labels
SEP_X  = 1.80    # x of the grey vertical separator line
BOX_L  = 1.95    # left edge of the content area
CX     = 5.55    # centre-x for full-width single boxes
BH     = 0.72    # standard box height

# y-centres of each layer (top to bottom)
Y = dict(
    inp  = 12.50,
    p1   = 10.85,
    p2a  =  9.18,   # ML base-learners row
    p2b  =  8.10,   # ML meta-learner row
    p3   =  6.72,
    dcct =  5.22,   # DCCT band centre
    p4   =  3.78,
    p5   =  2.32,
    p6   =  0.82,
)

# ── helpers ───────────────────────────────────────────────────────────────────
def rbox(cx, cy, w, h, lines, fc, ec, fs=7.6, bold=True):
    """Draw a rounded rectangle centred at (cx, cy) with multi-line text."""
    patch = FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.07",
        facecolor=fc, edgecolor=ec, linewidth=1.5, zorder=3,
    )
    ax.add_patch(patch)
    if isinstance(lines, str):
        lines = lines.split("\n")
    n = len(lines)
    # space lines evenly within the box
    step = h / (n + 1) if n > 1 else 0
    for i, ln in enumerate(lines):
        lfs = fs       if (bold and i == 0 and n > 1) else (fs - 0.7)
        lfw = "bold"   if (bold and i == 0 and n > 1) else "normal"
        ly  = cy + step * ((n - 1) / 2 - i)
        ax.text(cx, ly, ln, ha="center", va="center",
                fontsize=lfs, fontweight=lfw, zorder=4)


def arr(x1, y1, x2, y2, label="", dashed=False,
        color="#333333", lw=1.25, rad=0.0, lx=0.10, ly=0.06):
    """Draw an arrow; optional inline label beside the midpoint."""
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="->", color=color, lw=lw,
            linestyle="--" if dashed else "-",
            connectionstyle=f"arc3,rad={rad}",
        ),
        zorder=5,
    )
    if label:
        mx = (x1 + x2) / 2 + lx
        my = (y1 + y2) / 2 + ly
        ax.text(mx, my, label, fontsize=6.8, color=color,
                va="center", ha="left", zorder=6)


def lbl(y, text, color):
    """Left-margin coloured italic layer label."""
    ax.text(LBL_X, y, text,
            fontsize=7.8, fontweight="bold", fontstyle="italic",
            color=color, va="center", ha="left")


# ── separator line ────────────────────────────────────────────────────────────
ax.plot([SEP_X, SEP_X], [0.25, 13.25],
        color="#CCCCCC", lw=0.9, zorder=1)

# ══════════════════════════════════════════════════════════════════════════════
# LAYER 1 — Input Data
# ══════════════════════════════════════════════════════════════════════════════
lbl(Y["inp"], "Layer 1:\nInput Data", C["inp"][1])

rbox(3.15, Y["inp"], 2.15, BH,
     ["Route Set R",  "d, w, mode, θ"], *C["inp"])
rbox(5.60, Y["inp"], 2.15, BH,
     ["EPA / IMO",    "Emission Factors"], *C["inp"])
rbox(7.95, Y["inp"], 2.00, BH,
     ["Ember / eGRID", "CI Profiles"], *C["inp"])

# ══════════════════════════════════════════════════════════════════════════════
# LAYER 2 — PIEM  (Physics-Informed Emission Model)
# ══════════════════════════════════════════════════════════════════════════════
lbl(Y["p1"], "Layer 2:\nPIEM", C["piem"][1])

rbox(4.50, Y["p1"], 3.80, BH,
     ["Physics-Informed Emission Model (PIEM)",
      "E = d · w · EF_m  ×  f_load × f_speed × f_temp",
      "                 ×  f_cong × f_slope × f_weather"],
     *C["piem"], fs=7.2)

rbox(7.90, Y["p1"], 2.10, BH,
     ["15 Physics Features",
      "load_factor, f_cong,",
      "f_slope, f_weather, …"],
     *C["piem"], fs=7.2)

# ══════════════════════════════════════════════════════════════════════════════
# LAYER 3 — ML Ensemble
# ══════════════════════════════════════════════════════════════════════════════
lbl(Y["p2a"] - 0.35, "Layer 3:\nML Ensemble", C["ml"][1])

# base learners
rbox(3.05, Y["p2a"], 2.10, BH,
     ["Random Forest", "(Robust / outliers)"], *C["ml"])
rbox(5.55, Y["p2a"], 2.30, BH,
     ["Segmented MoE", "6 segments  ·  MAPE 1.44 %"], *C["ml"])
rbox(8.05, Y["p2a"], 2.00, BH,
     ["XGBoost", "(High accuracy)"], *C["ml"])

# meta-learner
rbox(5.55, Y["p2b"], 5.20, 0.62,
     ["Stacked Meta-Learner (Ridge OOF)   →   ê  CO₂e / route"],
     *C["ml"], fs=7.5, bold=False)

# ══════════════════════════════════════════════════════════════════════════════
# LAYER 4 — Carbon-Budget MILP
# ══════════════════════════════════════════════════════════════════════════════
lbl(Y["p3"], "Layer 4:\nMILP", C["milp"][1])

rbox(4.50, Y["p3"], 3.80, BH,
     ["Carbon-Budget MILP",
      "min Σ (c_rm + λ_ETS · e_rm) · x_rm",
      "s.t.  Σ e_rm · x_rm ≤ B ,   x ∈ {0,1}"],
     *C["milp"], fs=7.2)

rbox(7.90, Y["p3"], 2.10, BH,
     ["PuLP / CBC  ·  53 ms",
      "X*_MILP  (primal)",
      "λ*  (dual shadow price)"],
     *C["milp"], fs=7.2)

# ══════════════════════════════════════════════════════════════════════════════
# DCCT BAND
# ══════════════════════════════════════════════════════════════════════════════
lbl(Y["dcct"], "DCCT", C["dcct"][1])

BAND_H = 1.05
dcct_bg = FancyBboxPatch(
    (BOX_L, Y["dcct"] - BAND_H / 2), 7.10, BAND_H,
    boxstyle="round,pad=0.08",
    facecolor=C["dcct"][0], edgecolor=C["dcct"][1],
    linewidth=2.0, zorder=2,
)
ax.add_patch(dcct_bg)
ax.text(BOX_L + 0.15, Y["dcct"] + BAND_H / 2 - 0.16,
        "DCCT — Dual-Channel Certificate Transfer",
        fontsize=8.5, fontweight="bold", color=C["dcct"][1],
        va="top", ha="left", zorder=4)

rbox(3.80, Y["dcct"] - 0.08, 2.85, 0.58,
     ["Ch 1 · CAPS  (Primal X*)",
      "⌊N/4⌋ = 21 seeded individuals",
      "Thm 1: X* ∈ PF*   Thm 2: G*(ε) = 0"],
     "#FFFDE7", C["dcct"][1], fs=6.7)

rbox(7.20, Y["dcct"] - 0.08, 2.85, 0.58,
     ["Ch 2 · SPRD  (Dual λ*)",
      "Biases Das-Dennis ref. directions",
      "Thm 3: density ≥ (1+α)×"],
     "#FFFDE7", C["dcct"][1], fs=6.7)

# ══════════════════════════════════════════════════════════════════════════════
# LAYER 5 — NSGA-III
# ══════════════════════════════════════════════════════════════════════════════
lbl(Y["p4"], "Layer 5:\nNSGA-III", C["ns3"][1])

rbox(4.35, Y["p4"], 3.55, BH,
     ["DCCT-NSGA-III",
      "M = 4 obj  ·  N = 84 ref dirs  ·  G = 80",
      "CRI = 1 − exp(−Λ)  reliability objective"],
     *C["ns3"], fs=7.2)

rbox(7.90, Y["p4"], 2.10, BH,
     ["Pareto Front PF*",
      "84 Pareto solutions",
      "2.6×  speedup vs. standard"],
     *C["ns3"], fs=7.2)

# ══════════════════════════════════════════════════════════════════════════════
# LAYER 6 — Dynamic CI Departure Scheduling
# ══════════════════════════════════════════════════════════════════════════════
lbl(Y["p5"], "Layer 6:\nDynamic CI", C["ci"][1])

rbox(CX, Y["p5"], 6.70, BH,
     ["Dynamic CI Departure Scheduling  (Phase 5)",
      "t*_r  =  argmin_{h ∈ ±8 h window}  E_elec(r, h)",
      "8 EU + US regional CI profiles   ·   265.8 t CO₂e / yr saving  (Rotterdam)"],
     *C["ci"], fs=7.2)

# ══════════════════════════════════════════════════════════════════════════════
# LAYER 7 — Synthesis / Output
# ══════════════════════════════════════════════════════════════════════════════
lbl(Y["p6"], "Layer 7:\nOutput", C["out"][1])

rbox(CX, Y["p6"], 6.70, BH,
     ["Tchebycheff Synthesis  (Phase 6)   →   X*_pref",
      "argmin_k { w_k · |f_k − f*_k| / r_k }",
      "Certified Pareto-optimal route assignment  ·  4 objectives balanced"],
     *C["out"], fs=7.2)

# ══════════════════════════════════════════════════════════════════════════════
# ARROWS — main flow
# ══════════════════════════════════════════════════════════════════════════════

# Input → PIEM (Route data feeds PIEM formula; EF feeds PIEM formula; CI feeds features)
arr(3.15, Y["inp"] - BH/2,  4.10, Y["p1"] + BH/2)
arr(5.60, Y["inp"] - BH/2,  5.00, Y["p1"] + BH/2)
arr(7.95, Y["inp"] - BH/2,  7.90, Y["p1"] + BH/2)

# PIEM formula → PIEM features (horizontal)
arr(6.40, Y["p1"],  6.85, Y["p1"])

# PIEM formula → RF  (diagonal left-down)
arr(3.85, Y["p1"] - BH/2,  3.05, Y["p2a"] + BH/2)

# PIEM features → XGB  (straight down)
arr(7.90, Y["p1"] - BH/2,  8.05, Y["p2a"] + BH/2)

# PIEM formula → Segmented MoE (straight down from formula centre)
arr(5.50, Y["p1"] - BH/2,  5.55, Y["p2a"] + BH/2)

# ML base learners → meta-learner (converge)
arr(3.05, Y["p2a"] - BH/2,  4.20, Y["p2b"] + 0.31)
arr(5.55, Y["p2a"] - BH/2,  5.55, Y["p2b"] + 0.31)
arr(8.05, Y["p2a"] - BH/2,  6.90, Y["p2b"] + 0.31)

# Meta-learner → MILP
arr(5.55, Y["p2b"] - 0.31,  5.00, Y["p3"] + BH/2)

# MILP formula → MILP output box (horizontal)
arr(6.40, Y["p3"],  6.85, Y["p3"])

# MILP output → DCCT CAPS  (X*  — curves left)
arr(7.40, Y["p3"] - BH/2,  3.80, Y["dcct"] + BAND_H/2 - 0.18,
    label="X*_MILP", rad=0.20, lx=-0.80, ly=0.10)

# MILP output → DCCT SPRD  (λ* — short drop)
arr(8.10, Y["p3"] - BH/2,  7.20, Y["dcct"] + BAND_H/2 - 0.18,
    label="λ*", rad=-0.15, lx=0.10, ly=0.06)

# DCCT CAPS → NSGA-III
arr(3.80, Y["dcct"] - BAND_H/2,  4.10, Y["p4"] + BH/2)

# DCCT SPRD → NSGA-III
arr(7.20, Y["dcct"] - BAND_H/2,  6.00, Y["p4"] + BH/2)

# NSGA-III → Pareto Front (horizontal)
arr(6.12, Y["p4"],  6.85, Y["p4"])

# Pareto Front → Dynamic CI (diagonal down-left)
arr(7.90, Y["p4"] - BH/2,  6.50, Y["p5"] + BH/2)

# Dynamic CI → Output
arr(CX, Y["p5"] - BH/2,  CX, Y["p6"] + BH/2)

# ── MAPE feedback dashed arrow (style matching sample "Evaluation" arc) ──────
ax.annotate(
    "", xy=(8.60, Y["p2a"] + BH/2),
    xytext=(8.60, Y["p2b"] - 0.31),
    arrowprops=dict(
        arrowstyle="->", color="#1565C0", lw=1.1,
        linestyle="--",
        connectionstyle="arc3,rad=-0.4",
    ),
    zorder=5,
)
ax.text(9.00, (Y["p2a"] + BH/2 + Y["p2b"] - 0.31) / 2,
        "MAPE\nEvaluation",
        fontsize=6.5, color="#1565C0", va="center", ha="left",
        fontstyle="italic", zorder=6)

# ── figure caption note ───────────────────────────────────────────────────────
ax.text(CX, 0.12,
        "Fig. 1.  CARMA six-phase pipeline.  Dashed arrow = MAPE-driven weight evaluation.",
        ha="center", va="bottom", fontsize=7.0, color="#555555", style="italic")

# ── save ─────────────────────────────────────────────────────────────────────
plt.tight_layout(pad=0.3)
for ext in ("png", "pdf"):
    path = os.path.join(OUT_DIR, f"fig1_carma_pipeline.{ext}")
    plt.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    print(f"Saved: {path}")
plt.close()
