"""
Figure generation for CARMA manuscript v3.
==========================================
Generates publication-ready figures:

  Fig. 2 — Parametric MAC step-function curves (3 panels, one per archetype)
  Fig. 3 — Decision regime heatmaps (budget × carbon-price, 3 networks)

Output: paper/figures/fig2_mac_curves.png/.pdf
        paper/figures/fig3_regime_heatmaps.png/.pdf

Usage
-----
  python experiments/generate_figures.py
"""
from __future__ import annotations

import os
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

from experiments.parametric_abatement import (
    build_salamanca,
    build_iberian,
    build_frankfurt,
    run_parametric_sweep,
    build_decision_regimes,
    CARBON_PRICES_EUR_T,
)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
FIGURES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "paper", "figures")
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

NETWORK_META = {
    "Salamanca": {
        "title": "Salamanca domestic\n(truck/rail, 12 routes, Spain)",
        "color": "#2166ac",
        "infeas_threshold": None,
    },
    "Iberian": {
        "title": "Iberian regional\n(truck/rail/ship, 12 routes)",
        "color": "#1a9641",
        "infeas_threshold": None,
    },
    "Frankfurt": {
        "title": "Frankfurt European hub\n(truck/rail/air, 14 routes)",
        "color": "#d73027",
        "infeas_threshold": 30,
    },
}

ETS_REFS = [
    (65,  "#e41a1c", "EU ETS 2024 (65 €/t)"),
    (150, "#ff7f00", "ETS 2 scenario (150 €/t)"),
]


# ---------------------------------------------------------------------------
# Figure 2 — MAC step-function curves
# ---------------------------------------------------------------------------

def generate_mac_figure(df_all: pd.DataFrame) -> str:
    """Three-panel figure showing logistics cost + MAC per network."""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.5))
    fig.subplots_adjust(wspace=0.45)

    for ax, (name, meta) in zip(axes, NETWORK_META.items()):
        sub = df_all[df_all["network"] == name].copy().reset_index(drop=True)
        color = meta["color"]

        x = sub["reduction_pct"].values
        cost_k = sub["optimal_cost_eur"].values / 1000.0

        # ---- Left y-axis: logistics cost ----
        ax.plot(x, cost_k, "o-", color=color, linewidth=2.2, markersize=5,
                label="Logistics cost (€k)", zorder=3)
        ax.set_xlabel("Carbon reduction target (%)", fontsize=10)
        ax.set_ylabel("Optimal logistics cost (€k)", fontsize=9, color=color)
        ax.tick_params(axis="y", labelcolor=color)
        ax.set_xlim(-2, 55)

        # ---- Infeasibility shading ----
        thresh = meta["infeas_threshold"]
        if thresh is not None:
            ax.axvspan(thresh, 55, alpha=0.08, color="red")
            ax.text(thresh + 1, cost_k.min() * 0.98, "infeasible",
                    fontsize=7, color="red", va="bottom", ha="left")

        # ---- Right y-axis: MAC bars ----
        ax2 = ax.twinx()
        mac_vals = sub["finite_diff_mac_eur_t"].values  # may contain None/NaN
        bar_x, bar_h = [], []
        for i in range(1, len(sub)):
            mv = mac_vals[i]
            try:
                fv = float(mv)
                if mv is not None and not np.isnan(fv) and not np.isinf(fv) and fv > 0:
                    bar_x.append(x[i])
                    bar_h.append(fv)
            except (TypeError, ValueError):
                pass

        if bar_h:
            ax2.bar(bar_x, bar_h, width=4.2, alpha=0.45, color=color, zorder=2,
                    label="MAC (€/t CO₂e)")

        # ETS reference lines
        for ets_p, ets_c, ets_lbl in ETS_REFS:
            ax2.axhline(y=ets_p, linestyle="--", color=ets_c, linewidth=1.3,
                        alpha=0.85, label=ets_lbl)

        max_mac = max(bar_h) if bar_h else 200
        ax2.set_ylim(0, max_mac * 1.18)
        ax2.set_ylabel("MAC (€/tonne CO₂e)", fontsize=9)
        ax2.yaxis.set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda v, _: f"{int(v):,}")
        )

        # Annotate key MAC values
        for bx, bh in zip(bar_x, bar_h):
            if bh > max_mac * 0.25:
                ax2.text(bx, bh + max_mac * 0.02, f"{int(bh):,}",
                         ha="center", va="bottom", fontsize=6.5, color=color,
                         fontweight="bold")

        ax.set_title(meta["title"], fontsize=9.5, fontweight="bold", pad=6)

    # Shared legend
    legend_elements = [
        mpatches.Patch(color="#444", alpha=0.45, label="MAC (€/t CO₂e)"),
        plt.Line2D([0], [0], color="#e41a1c", linestyle="--", label="EU ETS 2024 (65 €/t)"),
        plt.Line2D([0], [0], color="#ff7f00", linestyle="--", label="ETS 2 scenario (150 €/t)"),
        mpatches.Patch(color="red", alpha=0.08, label="Infeasible region"),
    ]
    fig.legend(handles=legend_elements, loc="lower center", ncol=4,
               fontsize=8.5, bbox_to_anchor=(0.5, -0.03), frameon=True)

    out_png = os.path.join(FIGURES_DIR, "fig2_mac_curves.png")
    fig.savefig(out_png, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out_png}")
    return out_png


# ---------------------------------------------------------------------------
# Figure 3 — Regime heatmaps
# ---------------------------------------------------------------------------

REGIME_COLOR = {
    "co-benefit":         "#3498db",
    "non-binding":        "#3498db",
    "shift_preferred":    "#27ae60",
    "parity":             "#f39c12",
    "allowance_preferred": "#e74c3c",
    "infeasible":         "#95a5a6",
}
REGIME_ABBR = {
    "co-benefit":         "CO-BEN",
    "non-binding":        "CO-BEN",
    "shift_preferred":    "SHIFT",
    "parity":             "PARITY",
    "allowance_preferred": "ALLOW",
    "infeasible":         "INF",
}
REGIME_NUM = {
    "co-benefit": 0, "non-binding": 0,
    "shift_preferred": 1,
    "parity": 2,
    "allowance_preferred": 3,
    "infeasible": 4,
}
from matplotlib.colors import ListedColormap

REGIME_CMAP = ListedColormap([
    "#3498db",  # 0 co-benefit
    "#27ae60",  # 1 shift preferred
    "#f39c12",  # 2 parity
    "#e74c3c",  # 3 allowance preferred
    "#95a5a6",  # 4 infeasible
])


def generate_regime_heatmap(df_regime: pd.DataFrame) -> str:
    """Fig. 3: 3-panel regime heatmaps (network × carbon-price × budget)."""

    budget_levels = sorted(df_regime["reduction_pct"].unique())
    carbon_prices = sorted(df_regime["carbon_price_eur_t"].unique())
    n_budgets = len(budget_levels)
    n_prices  = len(carbon_prices)

    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    fig.subplots_adjust(wspace=0.35)

    for ax, (name, meta) in zip(axes, NETWORK_META.items()):
        sub = df_regime[df_regime["network"] == name]

        num_matrix = np.full((n_budgets, n_prices), 4, dtype=int)  # default: infeasible
        txt_matrix = [[""] * n_prices for _ in range(n_budgets)]

        for bi, bp in enumerate(budget_levels):
            for ci, cp in enumerate(carbon_prices):
                cell = sub[(sub["reduction_pct"] == bp) & (sub["carbon_price_eur_t"] == cp)]
                if not cell.empty:
                    regime = cell.iloc[0]["regime"]
                else:
                    regime = "infeasible"
                num_matrix[bi, ci] = REGIME_NUM.get(regime, 4)
                txt_matrix[bi][ci] = REGIME_ABBR.get(regime, "?")

        im = ax.imshow(num_matrix, cmap=REGIME_CMAP, aspect="auto",
                       vmin=-0.5, vmax=4.5, origin="upper")

        ax.set_xticks(range(n_prices))
        ax.set_xticklabels([f"€{int(p)}" for p in carbon_prices], fontsize=8.5)
        ax.set_yticks(range(n_budgets))
        ax.set_yticklabels([f"{int(bp)}%" for bp in budget_levels], fontsize=8.5)
        ax.set_xlabel("Carbon price (€/t CO₂e)", fontsize=9.5)
        ax.set_ylabel("Carbon reduction target (%)", fontsize=9.5)
        ax.set_title(meta["title"], fontsize=9.5, fontweight="bold", pad=6)

        # Annotate cells
        for bi in range(n_budgets):
            for ci in range(n_prices):
                num = num_matrix[bi, ci]
                txt = txt_matrix[bi][ci]
                fc = "white" if num >= 3 else "black"
                ax.text(ci, bi, txt, ha="center", va="center",
                        fontsize=7, color=fc, fontweight="bold")

        # Mark ETS 65 column
        try:
            ets_ci = carbon_prices.index(65)
            ax.axvline(x=ets_ci - 0.5, color="#e41a1c", linewidth=2, linestyle=":")
            ax.axvline(x=ets_ci + 0.5, color="#e41a1c", linewidth=2, linestyle=":")
        except ValueError:
            pass

    legend_patches = [
        mpatches.Patch(color="#3498db", label="Co-benefit / non-binding (Regime 4)"),
        mpatches.Patch(color="#27ae60", label="Mode shift preferred (Regime 1)"),
        mpatches.Patch(color="#f39c12", label="Parity zone (Regime 2)"),
        mpatches.Patch(color="#e74c3c", label="Allowance preferred (Regime 3)"),
        mpatches.Patch(color="#95a5a6", label="Infeasible (Regime 5)"),
    ]
    fig.legend(handles=legend_patches, loc="lower center", ncol=5,
               fontsize=9, bbox_to_anchor=(0.5, -0.04), frameon=True)

    out_png = os.path.join(FIGURES_DIR, "fig3_regime_heatmaps.png")
    fig.savefig(out_png, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out_png}")
    return out_png


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("\nRunning parametric sweeps for figure generation...")
    networks = {
        "Salamanca": build_salamanca(),
        "Iberian":   build_iberian(),
        "Frankfurt": build_frankfurt(),
    }
    sweeps = []
    for name, routes in networks.items():
        print(f"  Sweeping {name}...")
        df = run_parametric_sweep(routes, name)
        sweeps.append(df)

    df_all = pd.concat(sweeps, ignore_index=True)
    df_regime = build_decision_regimes(df_all)

    # Save CSVs for reuse
    df_all.to_csv(os.path.join(RESULTS_DIR, "parametric_abatement_all.csv"), index=False)
    df_regime.to_csv(os.path.join(RESULTS_DIR, "decision_regime_all.csv"), index=False)

    print("\nGenerating Fig. 2 (MAC step-function curves)...")
    generate_mac_figure(df_all)

    print("\nGenerating Fig. 3 (decision regime heatmaps)...")
    generate_regime_heatmap(df_regime)

    print("\nAll figures saved to paper/figures/")


if __name__ == "__main__":
    main()
