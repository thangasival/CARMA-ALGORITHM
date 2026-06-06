"""
generate_figure3.py
-------------------
Fig. 3 — DCCT Dual-Channel Certificate Transfer Mechanism
  • White background
  • Light fills per channel (blue = CAPS, pink = SPRD, green = output)
  • Dark connector arrows (#1F2937)
  • Theorem boxes in amber with dashed guarantee arrows
  • Output: SVG + PNG + PDF  (300 dpi for raster)

Run: python experiments/generate_figure3.py
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ── output paths ──────────────────────────────────────────────────────────────
HERE    = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.normpath(os.path.join(HERE, "..", "paper", "figures"))
os.makedirs(OUT_DIR, exist_ok=True)

# ── canvas ────────────────────────────────────────────────────────────────────
FW, FH = 12.0, 10.5
fig, ax = plt.subplots(figsize=(FW, FH))
ax.set_xlim(0, FW)
ax.set_ylim(0, FH)
ax.axis("off")
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# ── colour palette ────────────────────────────────────────────────────────────
MILP_FC, MILP_EC  = "#E0F7FA", "#00695C"   # teal
CAPS_FC, CAPS_EC  = "#DBEAFE", "#1E40AF"   # blue (CAPS / Ch1)
SPRD_FC, SPRD_EC  = "#FCE7F3", "#9D174D"   # pink (SPRD / Ch2)
NS3_FC,  NS3_EC   = "#DCFCE7", "#166534"   # green
PF_FC,   PF_EC    = "#F0FDF4", "#166534"   # light green
THM_FC,  THM_EC   = "#FFFBEB", "#B45309"   # amber
DARK    = "#1F2937"                          # dark connector colour
C1_BG,  C1_BG_EC  = "#EFF6FF", "#93C5FD"  # channel 1 container
C2_BG,  C2_BG_EC  = "#FDF2F8", "#F9A8D4"  # channel 2 container

# ── layout constants ──────────────────────────────────────────────────────────
C1X  = 2.5    # channel 1 centre x
CX   = 6.0    # overall centre x
C2X  = 9.5    # channel 2 centre x
BH   = 0.85   # standard box height
BH_S = 0.72   # inner-channel box height

# y-centres (top → bottom)
Y = dict(
    milp = 9.60,
    top  = 8.10,   # X*_MILP, λ* boxes
    mid  = 6.85,   # CAPS, SPRD operation boxes
    bot  = 5.60,   # P₀, Ref̂ boxes
    ns3  = 3.70,
    pf   = 2.30,
    thm  = 0.85,   # theorem boxes row
)

# channel container band (y range)
CHAN_TOP = Y["top"]  + BH_S / 2 + 0.20
CHAN_BOT = Y["bot"]  - BH_S / 2 - 0.20
CHAN_H   = CHAN_TOP - CHAN_BOT


# ── helpers ───────────────────────────────────────────────────────────────────

def rbox(cx, cy, w, h, lines, fc, ec, fs=8.2, bold=True):
    """Rounded rectangle centred at (cx, cy) with auto-spaced multi-line text."""
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.09",
        facecolor=fc, edgecolor=ec, linewidth=1.7, zorder=3,
    ))
    if isinstance(lines, str):
        lines = lines.split("\n")
    n = len(lines)
    step = h / (n + 1) if n > 1 else 0
    for i, ln in enumerate(lines):
        lfs = fs       if (bold and i == 0 and n > 1) else fs - 1.2
        lfw = "bold"   if (bold and i == 0 and n > 1) else "normal"
        ax.text(cx, cy + step * ((n - 1) / 2 - i),
                ln, ha="center", va="center",
                fontsize=lfs, fontweight=lfw, zorder=4)


def arr(x1, y1, x2, y2, label="", dashed=False,
        color=DARK, lw=1.5, rad=0.0, lx=0.10, ly=0.07):
    """Arrow from (x1,y1) → (x2,y2) with optional inline label."""
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="-|>", color=color, lw=lw,
            linestyle="--" if dashed else "-",
            connectionstyle=f"arc3,rad={rad}",
            mutation_scale=14,
        ), zorder=5,
    )
    if label:
        ax.text((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly,
                label, fontsize=7.5, color=color,
                va="center", ha="left", fontstyle="italic", zorder=6)


# ══════════════════════════════════════════════════════════════════════════════
# Channel containers
# ══════════════════════════════════════════════════════════════════════════════
for cx_c, fc, ec, label, lcolor in (
    (C1X, C1_BG, C1_BG_EC, "Channel 1 — CAPS", "#1E40AF"),
    (C2X, C2_BG, C2_BG_EC, "Channel 2 — SPRD", "#9D174D"),
):
    ax.add_patch(FancyBboxPatch(
        (cx_c - 2.05, CHAN_BOT), 4.10, CHAN_H,
        boxstyle="round,pad=0.10",
        facecolor=fc, edgecolor=ec, linewidth=1.8, zorder=1, alpha=0.75,
    ))
    ax.text(cx_c, CHAN_TOP + 0.08, label,
            ha="center", va="bottom",
            fontsize=9.8, fontweight="bold", color=lcolor)

# ══════════════════════════════════════════════════════════════════════════════
# Phase 3 — MILP
# ══════════════════════════════════════════════════════════════════════════════
rbox(CX, Y["milp"], 7.8, BH,
     ["Phase 3 — Carbon-Budget MILP",
      "min Σ (c_rm + λ_ETS · e_rm) · x_rm     s.t.  Σ e_rm · x_rm ≤ B,   x ∈ {0,1}",
      "PuLP / CBC   ·   53 ms   ·   certified globally optimal"],
     MILP_FC, MILP_EC)

# ══════════════════════════════════════════════════════════════════════════════
# Channel 1 inner boxes
# ══════════════════════════════════════════════════════════════════════════════
rbox(C1X, Y["top"], 3.6, BH_S,
     ["X*_MILP  (primal solution)",
      "Certified-optimal binary mode assignment"],
     CAPS_FC, CAPS_EC)

rbox(C1X, Y["mid"], 3.6, BH_S,
     ["CAPS — Certificate-Anchored Population Seeding",
      "{X*} ∪ {flip_gene(X*): ⌊N/4⌋−1} ∪ {random: 3N/4}"],
     CAPS_FC, CAPS_EC)

rbox(C1X, Y["bot"], 3.6, BH_S,
     ["P₀  —  Initial Population",
      "21 MILP-seeded  +  63 random   (N = 84 total)"],
     CAPS_FC, CAPS_EC)

# ══════════════════════════════════════════════════════════════════════════════
# Channel 2 inner boxes
# ══════════════════════════════════════════════════════════════════════════════
rbox(C2X, Y["top"], 3.6, BH_S,
     ["λ*  (dual shadow price)",
      "€ / kg CO₂e at binding budget constraint"],
     SPRD_FC, SPRD_EC)

rbox(C2X, Y["mid"], 3.6, BH_S,
     ["SPRD — Shadow-Priced Ref Dir Weighting",
      "α = min(1, λ*·10)     p_j ∝ (1 + α · e₂ⱼ)"],
     SPRD_FC, SPRD_EC)

rbox(C2X, Y["bot"], 3.6, BH_S,
     ["R̂ef  —  Augmented Reference Directions",
      "84 Das-Dennis + ⌈α·84⌉ extra  ·  denser in R_λ region"],
     SPRD_FC, SPRD_EC)

# ══════════════════════════════════════════════════════════════════════════════
# Phase 4 — NSGA-III
# ══════════════════════════════════════════════════════════════════════════════
rbox(CX, Y["ns3"], 7.8, BH,
     ["Phase 4 — DCCT-NSGA-III",
      "M = 4 objectives  ·  N = 84 reference directions  ·  G_max = 80 generations",
      "CRI = 1 − exp(−Λ)  reliability objective   ·   10.6 s  (2.6× speedup vs. standard 28.1 s)"],
     NS3_FC, NS3_EC)

# ══════════════════════════════════════════════════════════════════════════════
# Certificate-Anchored Pareto Front PF*
# ══════════════════════════════════════════════════════════════════════════════
rbox(CX, Y["pf"], 7.8, BH,
     ["Certificate-Anchored Pareto Front PF*",
      "84–92 Pareto-optimal solutions   ·   X*_MILP ∈ PF*  guaranteed at all generations",
      "−74.85 % emission  ·  −75.63 % cost  ·  10.7× cost spread  (Rotterdam network)"],
     PF_FC, PF_EC)

# ══════════════════════════════════════════════════════════════════════════════
# Theorem boxes (bottom row)
# ══════════════════════════════════════════════════════════════════════════════
THM_W, THM_H = 2.50, 0.90

rbox(1.80, Y["thm"], THM_W, THM_H,
     ["Theorem 1 — Extremal Anchor",
      "X* ∈ PF*  at all g ≥ 0"],
     THM_FC, THM_EC, fs=7.8)

rbox(6.00, Y["thm"], THM_W, THM_H,
     ["Theorem 2 — O(1) Convergence",
      "G*(ε) = 0  vs  Ω(|S|/N)  standard"],
     THM_FC, THM_EC, fs=7.8)

rbox(10.20, Y["thm"], THM_W, THM_H,
     ["Theorem 3 — SPRD Density",
      "E[dirs in R_λ] ≥ (1+α)× uniform"],
     THM_FC, THM_EC, fs=7.8)

# ══════════════════════════════════════════════════════════════════════════════
# ARROWS — main flow
# ══════════════════════════════════════════════════════════════════════════════

# MILP → X*_MILP (primal)
arr(4.20, Y["milp"] - BH / 2,
    C1X,  Y["top"]  + BH_S / 2,
    label="primal X*", rad=0.18, lx=-1.20, ly=0.12)

# MILP → λ* (dual)
arr(7.80, Y["milp"] - BH / 2,
    C2X,  Y["top"]  + BH_S / 2,
    label="dual λ*", rad=-0.18, lx=0.10, ly=0.12)

# Ch1 inner flow  X* → CAPS → P₀
arr(C1X, Y["top"] - BH_S / 2, C1X, Y["mid"] + BH_S / 2)
arr(C1X, Y["mid"] - BH_S / 2, C1X, Y["bot"] + BH_S / 2)

# Ch2 inner flow  λ* → SPRD → R̂ef
arr(C2X, Y["top"] - BH_S / 2, C2X, Y["mid"] + BH_S / 2)
arr(C2X, Y["mid"] - BH_S / 2, C2X, Y["bot"] + BH_S / 2)

# P₀ → NSGA-III
arr(C1X, Y["bot"] - BH_S / 2, 4.10, Y["ns3"] + BH / 2, rad=0.10)

# R̂ef → NSGA-III
arr(C2X, Y["bot"] - BH_S / 2, 7.90, Y["ns3"] + BH / 2, rad=-0.10)

# NSGA-III → PF*
arr(CX, Y["ns3"] - BH / 2, CX, Y["pf"] + BH / 2)

# ══════════════════════════════════════════════════════════════════════════════
# ARROWS — theorem guarantees (dashed amber)
# ══════════════════════════════════════════════════════════════════════════════

# T1 → PF*  (bottom-left corner of PF*)
arr(1.80, Y["thm"] + THM_H / 2,
    3.10, Y["pf"]  - BH / 2,
    label="guarantees", dashed=True, color=THM_EC, lw=1.2,
    rad=-0.20, lx=-1.35, ly=0.10)

# T2 → NSGA-III  (straight up)
arr(6.00, Y["thm"] + THM_H / 2,
    6.00, Y["ns3"] - BH / 2,
    label="guarantees", dashed=True, color=THM_EC, lw=1.2,
    lx=0.10, ly=0.06)

# T3 → R̂ef  (up-left curve)
arr(10.20, Y["thm"] + THM_H / 2,
    C2X,   Y["bot"]  - BH_S / 2,
    label="guarantees", dashed=True, color=THM_EC, lw=1.2,
    rad=0.25, lx=0.12, ly=0.08)

# ══════════════════════════════════════════════════════════════════════════════
# Caption
# ══════════════════════════════════════════════════════════════════════════════
ax.text(CX, 0.12,
        ("Fig. 3.   DCCT dual-channel certificate transfer mechanism.  "
         "Blue = Ch 1 CAPS (primal X*).   Pink = Ch 2 SPRD (dual λ*).   "
         "Dashed amber arrows = formal theorem guarantees."),
        ha="center", va="bottom", fontsize=7.5,
        color="#4B5563", fontstyle="italic")

# ══════════════════════════════════════════════════════════════════════════════
# Save
# ══════════════════════════════════════════════════════════════════════════════
plt.tight_layout(pad=0.3)
for ext in ("svg", "png", "pdf"):
    path = os.path.join(OUT_DIR, f"fig3_dcct_mechanism.{ext}")
    plt.savefig(path, dpi=300, bbox_inches="tight", facecolor="white",
                format=ext if ext != "png" else None)
    print(f"Saved: {path}")
plt.close()
