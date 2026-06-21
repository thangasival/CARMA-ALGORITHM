"""
Budget-Step Robustness Analysis
================================
Tests whether the finite-difference MAC and decision-regime classification
are stable across three budget step sizes: 2.5%, 5%, 10%.

This addresses a methodological concern: because MAC is estimated by finite
difference, a reviewer may ask whether the 5% step creates artificial jumps.

Outputs
-------
  experiments/results/budget_step_robustness.csv
  experiments/results/budget_step_robustness_summary.txt

Usage
-----
  python experiments/budget_step_robustness.py
"""
from __future__ import annotations

import os
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from algorithm.optimization.carbon_milp import CarbonBudgetMILP
from experiments.parametric_abatement import (
    build_salamanca,
    build_iberian,
    build_frankfurt,
    build_decision_regimes,
    CARBON_PRICES_EUR_T,
)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

ETS_PRICE = 65  # reference EU ETS price €/t

STEP_CONFIGS = {
    "2.5%": list(range(0, 51, 1))[::1],  # refined: 0,1,2,...50 but we'll use 2.5% steps
    "5%":   list(range(0, 51, 5)),
    "10%":  list(range(0, 51, 10)),
}

# Explicit float steps for 2.5%
BUDGET_25 = [i * 2.5 for i in range(21)]  # 0, 2.5, 5, ..., 50
BUDGET_50 = list(range(0, 51, 5))          # 0, 5, 10, ..., 50
BUDGET_10 = list(range(0, 51, 10))         # 0, 10, 20, ..., 50


def run_sweep_at_step(routes: list, network_name: str, budget_levels: list) -> pd.DataFrame:
    """Run parametric MILP sweep at arbitrary budget step sizes."""
    solver = CarbonBudgetMILP(ets_price_eur_per_kg=0.0)
    rows = []
    for pct in budget_levels:
        result = solver.optimise(routes, budget_reduction_pct=pct)
        rows.append({
            "network":               network_name,
            "reduction_pct":         pct,
            "optimal_cost_eur":      round(result.total_cost, 2),
            "actual_emissions_kg":   round(result.total_emissions_kg, 1),
            "baseline_cost_eur":     round(result.baseline_cost, 2),
            "baseline_emissions_kg": round(result.baseline_emissions, 1),
            "n_mode_shifts":         len(result.mode_shifts),
            "status":                result.status,
        })

    df = pd.DataFrame(rows)

    # Finite-difference MAC between consecutive budget levels
    macs = [None]
    for i in range(1, len(df)):
        dCost = df.iloc[i]["optimal_cost_eur"] - df.iloc[i - 1]["optimal_cost_eur"]
        dEm   = df.iloc[i - 1]["actual_emissions_kg"] - df.iloc[i]["actual_emissions_kg"]
        if dEm > 0.5:
            mac = dCost / dEm
        else:
            mac = None
        macs.append(mac)

    df["mac_eur_kg"] = macs
    df["mac_eur_t"]  = df["mac_eur_kg"].apply(
        lambda x: round(x * 1000, 1) if x is not None else None
    )
    return df


def classify_regime(mac_eur_kg, carbon_price_eur_t: float, status: str) -> str:
    """Single-cell regime classification."""
    p_kg = carbon_price_eur_t / 1000.0
    if status != "Optimal":
        return "infeasible"
    if mac_eur_kg is None:
        return "non-binding"
    if mac_eur_kg <= 0.0:
        return "co-benefit"
    ratio = mac_eur_kg / p_kg
    if ratio < 0.90:
        return "shift_preferred"
    if ratio <= 1.10:
        return "parity"
    return "allowance_preferred"


def main():
    networks = {
        "Salamanca": build_salamanca(),
        "Iberian":   build_iberian(),
        "Frankfurt": build_frankfurt(),
    }

    step_configs = {
        "2.5%": BUDGET_25,
        "5%":   BUDGET_50,
        "10%":  BUDGET_10,
    }

    # Common reference budget levels that appear in all three step sizes
    common_budgets = [0, 10, 20, 30, 40, 50]

    all_results = []
    summary_rows = []

    for net_name, routes in networks.items():
        print(f"\nNetwork: {net_name}")
        step_dfs = {}
        for step_label, budget_levels in step_configs.items():
            print(f"  Step size {step_label} ({len(budget_levels)} levels)...")
            df = run_sweep_at_step(routes, net_name, budget_levels)
            df["step_size"] = step_label
            step_dfs[step_label] = df
            all_results.append(df)

        # Compare regime at common budget levels
        for cb in common_budgets:
            regimes = {}
            for step_label, df in step_dfs.items():
                # Find closest budget level
                closest = df.iloc[(df["reduction_pct"] - cb).abs().argsort()[:1]]
                if closest.empty:
                    regimes[step_label] = "N/A"
                    continue
                row = closest.iloc[0]
                mac = row.get("mac_eur_kg")
                regime = classify_regime(mac, ETS_PRICE, row["status"])
                regimes[step_label] = regime

            all_same = len(set(regimes.values())) == 1
            summary_rows.append({
                "network":      net_name,
                "budget_%":     cb,
                "step_2.5%":    regimes.get("2.5%", "N/A"),
                "step_5%":      regimes.get("5%",   "N/A"),
                "step_10%":     regimes.get("10%",  "N/A"),
                "stable":       "YES" if all_same else "NO",
            })

    df_all = pd.concat(all_results, ignore_index=True)
    df_all.to_csv(
        os.path.join(RESULTS_DIR, "budget_step_robustness.csv"), index=False
    )

    df_summary = pd.DataFrame(summary_rows)

    # Print summary table
    print("\n" + "=" * 90)
    print(f"BUDGET-STEP ROBUSTNESS: Regime classification at EU ETS {ETS_PRICE} €/t")
    print("  Stable = regime is the same across 2.5%, 5%, and 10% step sizes")
    print("=" * 90)
    for net in ["Salamanca", "Iberian", "Frankfurt"]:
        sub = df_summary[df_summary["network"] == net]
        print(f"\n{net}:")
        print(sub[["budget_%", "step_2.5%", "step_5%", "step_10%", "stable"]].to_string(index=False))

    # Stability statistics
    stable_count   = df_summary["stable"].eq("YES").sum()
    total_count    = len(df_summary)
    stable_pct     = 100 * stable_count / total_count
    print(f"\nOverall stability: {stable_count}/{total_count} ({stable_pct:.0f}%) regime cells "
          f"are identical across step sizes.")

    # Save summary
    out_txt = os.path.join(RESULTS_DIR, "budget_step_robustness_summary.txt")
    with open(out_txt, "w") as f:
        f.write(f"BUDGET-STEP ROBUSTNESS SUMMARY\n")
        f.write(f"Reference carbon price: {ETS_PRICE} €/t\n\n")
        f.write(df_summary.to_string(index=False))
        f.write(f"\n\nOverall stability: {stable_count}/{total_count} "
                f"({stable_pct:.0f}%) regime cells identical across step sizes.\n")

    df_summary.to_csv(
        os.path.join(RESULTS_DIR, "budget_step_robustness_summary.csv"), index=False
    )
    print(f"\nSaved: {out_txt}")
    print(f"Saved: {RESULTS_DIR}/budget_step_robustness_summary.csv")

    return df_summary


if __name__ == "__main__":
    main()
