"""
Parameter Sensitivity Analysis
================================
Tests robustness of carbon compliance regime classification under perturbation
of key cost and emission-factor parameters.

Sweeps at the 20% budget reduction level (representative binding constraint)
across parameters most likely to shift regime classification.

Parameters swept
----------------
  1. Rail terminal cost    : €300, €500, €680 (baseline), €900, €1,200
  2. Truck cost rate       : ×0.75, ×0.90, ×1.00, ×1.25, ×1.50
  3. Rail cost rate        : ×0.75, ×0.90, ×1.00, ×1.25
  4. Rail emission factor  : ×0.50, ×0.75, ×1.00, ×1.30, ×1.60
  5. Carbon price scenario : 25, 50, 65, 75, 100, 150 €/t

Outputs
-------
  experiments/results/parameter_sensitivity.csv
  experiments/results/parameter_sensitivity_summary.txt

Usage
-----
  python experiments/parameter_sensitivity.py
"""
from __future__ import annotations

import copy
import os
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from algorithm.optimization.carbon_milp import CarbonBudgetMILP, MILPRoute

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# ---- Base parameters (from parametric_abatement.py) ----
BASE_EF = {
    "truck": 0.0762,
    "rail":  0.0285,
    "ship":  0.0110,
    "air":   0.6800,
}
BASE_COST = {
    "truck": 0.110,
    "rail":  0.055,
    "ship":  0.028,
    "air":   9.500,
}
BASE_TERMINAL = {
    "truck": 0.0,
    "rail":  680.0,
    "ship":  750.0,
    "air":   350.0,
}

ANALYSIS_BUDGET_PCT = 20   # representative binding budget

CARBON_PRICE_SCENARIOS = [25, 50, 65, 75, 100, 150]


def build_routes_with_params(
    raw_network: list,
    cost_rates: dict,
    terminals: dict,
    ef: dict,
    frankfurt_ef_rail: float | None = None,
) -> list:
    """
    Reconstruct MILPRoute list from raw network data with modified parameters.

    raw_network items: (origin, dest, dist_km, weight_t, feasible_modes)
    """
    routes = []
    for item in raw_network:
        origin, dest, dist_km, weight_t, feasible_modes = item
        cost_per_mode = {}
        em_per_mode   = {}
        for m in feasible_modes:
            transfer = terminals.get(m, 0.0) if m != "truck" else 0.0
            rail_ef  = frankfurt_ef_rail if (m == "rail" and frankfurt_ef_rail is not None) else ef[m]
            mode_ef  = rail_ef if m == "rail" else ef[m]
            cost_per_mode[m] = dist_km * weight_t * cost_rates[m] + transfer
            em_per_mode[m]   = dist_km * weight_t * mode_ef
        routes.append(MILPRoute(
            route_id=f"{origin[:3].upper()}-{dest[:3].upper()}",
            origin=origin, destination=dest,
            distance_km=dist_km, weight_tons=weight_t,
            commodity_type="general", current_mode="truck",
            feasible_modes=list(feasible_modes),
            cost_per_mode=cost_per_mode,
            emission_per_mode=em_per_mode,
        ))
    return routes


# ---- Pre-encoded raw networks (mode availability per route) ----

SALAMANCA_RAW = [
    ("Salamanca", "Zamora",     63,  8.5,  ["truck"]),
    ("Salamanca", "Avila",      98,  7.2,  ["truck"]),
    ("Salamanca", "Valladolid",115,  9.8,  ["truck", "rail"]),
    ("Salamanca", "Leon",      196, 11.0,  ["truck", "rail"]),
    ("Salamanca", "Madrid",    212, 22.0,  ["truck", "rail"]),
    ("Salamanca", "Caceres",   213,  8.0,  ["truck", "rail"]),
    ("Salamanca", "Burgos",    246, 10.5,  ["truck", "rail"]),
    ("Salamanca", "Merida",    261,  7.5,  ["truck", "rail"]),
    ("Salamanca", "Santander", 355, 12.0,  ["truck", "rail"]),
    ("Salamanca", "Bilbao",    375, 14.0,  ["truck", "rail"]),
    ("Salamanca", "Seville",   398, 18.0,  ["truck", "rail"]),
    ("Salamanca", "Barcelona", 510, 20.0,  ["truck", "rail"]),
]

IBERIAN_RAW = [
    ("Madrid",    "Barcelona",  620, 22.0, ["truck", "rail", "ship"]),
    ("Madrid",    "Valencia",   590,  8.0, ["truck", "rail", "ship"]),
    ("Madrid",    "Sevilla",    530, 14.0, ["truck", "rail", "ship"]),
    ("Madrid",    "Bilbao",     395, 12.0, ["truck", "rail"]),
    ("Madrid",    "Zaragoza",   325,  9.0, ["truck", "rail"]),
    ("Madrid",    "Toledo",     280,  5.0, ["truck", "rail"]),
    ("Bilbao",    "Barcelona",  620, 35.0, ["truck", "rail", "ship"]),
    ("Barcelona", "Madrid",     620, 18.0, ["truck", "rail", "ship"]),
    ("Valencia",  "Hamburg",   2200, 60.0, ["truck", "rail", "ship"]),
    ("Bilbao",    "Madrid",     395, 12.0, ["truck", "rail"]),
    ("Salamanca", "Barcelona",  510,  7.0, ["truck", "rail"]),
    ("Algeciras", "Genova",    1800, 50.0, ["truck", "rail", "ship"]),
]

FRANKFURT_RAW = [
    ("Frankfurt", "Prague CZ",    280,  8.0, ["truck", "rail"]),
    ("Frankfurt", "Zurich CH",    350, 10.0, ["truck", "rail"]),
    ("Frankfurt", "Amsterdam NL", 370, 12.0, ["truck", "rail"]),
    ("Frankfurt", "Brussels BE",  395, 11.0, ["truck", "rail"]),
    ("Frankfurt", "Hamburg DE",   480, 14.0, ["truck", "rail"]),
    ("Frankfurt", "Berlin DE",    550, 13.0, ["truck", "rail"]),
    ("Frankfurt", "Paris FR",     485, 15.0, ["truck", "rail"]),
    ("Frankfurt", "Vienna AT",    620, 16.0, ["truck", "rail"]),
    ("Frankfurt", "Warsaw PL",   1100, 18.0, ["truck", "rail", "air"]),
    ("Frankfurt", "Milan IT",     700, 20.0, ["truck", "rail", "air"]),
    ("Frankfurt", "Lyon FR",      630, 14.0, ["truck", "rail"]),
    ("Frankfurt", "Barcelona ES",1500, 22.0, ["truck", "rail", "air"]),
    ("Frankfurt", "Madrid ES",   1800, 25.0, ["truck", "rail"]),
    ("Frankfurt", "Budapest HU",  840, 12.0, ["truck", "rail"]),
]

FRANKFURT_BASE_RAIL_EF = 0.0570   # German grid, higher than Spanish


NETWORKS = {
    "Salamanca": (SALAMANCA_RAW, None),
    "Iberian":   (IBERIAN_RAW,   None),
    "Frankfurt": (FRANKFURT_RAW, FRANKFURT_BASE_RAIL_EF),
}


def compute_mac_at_budget(routes: list, budget_pct: float) -> tuple[float | None, str]:
    """Solve MILP at budget_pct and budget_pct-5%, return MAC (€/kg) and status."""
    solver = CarbonBudgetMILP(ets_price_eur_per_kg=0.0)

    r_full  = solver.optimise(routes, budget_reduction_pct=max(0, budget_pct - 5))
    r_tight = solver.optimise(routes, budget_reduction_pct=budget_pct)

    if r_tight.status != "Optimal":
        return None, "infeasible"

    dCost = r_tight.total_cost - r_full.total_cost
    dEm   = r_full.total_emissions_kg - r_tight.total_emissions_kg
    if dEm < 0.5:
        return None, "non-binding"

    mac_kg = dCost / dEm
    if mac_kg < 0:
        return mac_kg, "co-benefit"
    return mac_kg, "Optimal"


def classify_regime(mac_eur_kg: float | None, carbon_price_eur_t: float,
                    status: str) -> str:
    if status == "infeasible":
        return "infeasible"
    if mac_eur_kg is None or status == "non-binding":
        return "non-binding"
    if mac_eur_kg <= 0:
        return "co-benefit"
    p_kg = carbon_price_eur_t / 1000.0
    ratio = mac_eur_kg / p_kg
    if ratio < 0.90:
        return "shift_preferred"
    if ratio <= 1.10:
        return "parity"
    return "allowance_preferred"


def sensitivity_sweep() -> pd.DataFrame:
    rows = []

    # ---- Sweep 1: Rail terminal cost ----
    rail_terminal_values = [300, 500, 680, 900, 1200]
    for net_name, (raw, fra_ef) in NETWORKS.items():
        if net_name == "Iberian":
            continue  # co-benefit network, rail terminal doesn't change regime
        for rt in rail_terminal_values:
            terminals = {**BASE_TERMINAL, "rail": rt}
            routes = build_routes_with_params(raw, BASE_COST, terminals, BASE_EF, fra_ef)
            mac, status = compute_mac_at_budget(routes, ANALYSIS_BUDGET_PCT)
            for cp in CARBON_PRICE_SCENARIOS:
                regime = classify_regime(mac, cp, status)
                rows.append({
                    "network":    net_name,
                    "parameter":  "rail_terminal_eur",
                    "value":      rt,
                    "baseline":   680,
                    "pct_change": round(100 * (rt - 680) / 680, 0),
                    "mac_eur_t":  round(mac * 1000, 0) if mac is not None else None,
                    "carbon_price_eur_t": cp,
                    "regime":     regime,
                })

    # ---- Sweep 2: Truck cost rate multiplier ----
    truck_multipliers = [0.75, 0.90, 1.00, 1.25, 1.50]
    for net_name, (raw, fra_ef) in NETWORKS.items():
        if net_name == "Iberian":
            continue
        for mult in truck_multipliers:
            cost_rates = {**BASE_COST, "truck": BASE_COST["truck"] * mult}
            routes = build_routes_with_params(raw, cost_rates, BASE_TERMINAL, BASE_EF, fra_ef)
            mac, status = compute_mac_at_budget(routes, ANALYSIS_BUDGET_PCT)
            for cp in CARBON_PRICE_SCENARIOS:
                regime = classify_regime(mac, cp, status)
                rows.append({
                    "network":    net_name,
                    "parameter":  "truck_cost_rate_mult",
                    "value":      mult,
                    "baseline":   1.00,
                    "pct_change": round(100 * (mult - 1.0), 0),
                    "mac_eur_t":  round(mac * 1000, 0) if mac is not None else None,
                    "carbon_price_eur_t": cp,
                    "regime":     regime,
                })

    # ---- Sweep 3: Rail cost rate multiplier ----
    rail_multipliers = [0.50, 0.75, 1.00, 1.25, 1.50]
    for net_name, (raw, fra_ef) in NETWORKS.items():
        if net_name == "Iberian":
            continue
        for mult in rail_multipliers:
            cost_rates = {**BASE_COST, "rail": BASE_COST["rail"] * mult}
            routes = build_routes_with_params(raw, cost_rates, BASE_TERMINAL, BASE_EF, fra_ef)
            mac, status = compute_mac_at_budget(routes, ANALYSIS_BUDGET_PCT)
            for cp in CARBON_PRICE_SCENARIOS:
                regime = classify_regime(mac, cp, status)
                rows.append({
                    "network":    net_name,
                    "parameter":  "rail_cost_rate_mult",
                    "value":      mult,
                    "baseline":   1.00,
                    "pct_change": round(100 * (mult - 1.0), 0),
                    "mac_eur_t":  round(mac * 1000, 0) if mac is not None else None,
                    "carbon_price_eur_t": cp,
                    "regime":     regime,
                })

    # ---- Sweep 4: Rail emission factor multiplier ----
    ef_multipliers = [0.50, 0.75, 1.00, 1.30, 1.60]
    for net_name, (raw, fra_ef) in NETWORKS.items():
        if net_name == "Iberian":
            continue
        base_rail_ef = fra_ef if fra_ef is not None else BASE_EF["rail"]
        for mult in ef_multipliers:
            new_ef = {**BASE_EF, "rail": base_rail_ef * mult}
            fra_mult = base_rail_ef * mult if fra_ef is not None else None
            routes = build_routes_with_params(raw, BASE_COST, BASE_TERMINAL, new_ef, fra_mult)
            mac, status = compute_mac_at_budget(routes, ANALYSIS_BUDGET_PCT)
            for cp in CARBON_PRICE_SCENARIOS:
                regime = classify_regime(mac, cp, status)
                rows.append({
                    "network":    net_name,
                    "parameter":  "rail_ef_mult",
                    "value":      mult,
                    "baseline":   1.00,
                    "pct_change": round(100 * (mult - 1.0), 0),
                    "mac_eur_t":  round(mac * 1000, 0) if mac is not None else None,
                    "carbon_price_eur_t": cp,
                    "regime":     regime,
                })

    return pd.DataFrame(rows)


def print_sensitivity_summary(df: pd.DataFrame):
    print("\n" + "=" * 100)
    print(f"PARAMETER SENSITIVITY — Regime at {ANALYSIS_BUDGET_PCT}% budget reduction")
    print("  Baseline regime (Salamanca/Frankfurt at 20%) vs parameter perturbation")
    print("=" * 100)

    ets_price = 65
    sub = df[df["carbon_price_eur_t"] == ets_price]

    for net in ["Salamanca", "Frankfurt"]:
        print(f"\n{net} — carbon price {ets_price} €/t:")
        net_sub = sub[sub["network"] == net]
        for param in net_sub["parameter"].unique():
            p_sub = net_sub[net_sub["parameter"] == param].copy()
            p_sub = p_sub.sort_values("value")
            regimes = list(zip(p_sub["value"].round(2), p_sub["mac_eur_t"], p_sub["regime"]))
            print(f"  {param:30s}: {regimes}")


def main():
    print("\nRunning parameter sensitivity sweep...")
    print(f"  Budget level: {ANALYSIS_BUDGET_PCT}%  | Carbon prices: {CARBON_PRICE_SCENARIOS} €/t")
    print("  Parameters: rail terminal, truck/rail cost rate, rail emission factor")

    df = sensitivity_sweep()

    out_csv = os.path.join(RESULTS_DIR, "parameter_sensitivity.csv")
    df.to_csv(out_csv, index=False)

    print_sensitivity_summary(df)

    # Regime flip analysis: which parameter flips regime from allowance to shift?
    print("\n" + "=" * 100)
    print("REGIME FLIP ANALYSIS -- Conditions under which 'allowance_preferred' -> 'shift_preferred'")
    print("  (at EU ETS 65 €/t and 20% budget reduction)")
    print("=" * 100)

    ets_sub = df[(df["carbon_price_eur_t"] == 65)]
    for net in ["Salamanca", "Frankfurt"]:
        net_sub = ets_sub[ets_sub["network"] == net]
        shift_cases = net_sub[net_sub["regime"] == "shift_preferred"]
        if shift_cases.empty:
            print(f"\n  {net}: No parameter combination shifts regime to 'shift_preferred' at 65 €/t.")
        else:
            print(f"\n  {net}: Regime shifts to 'shift_preferred' under:")
            for _, row in shift_cases.iterrows():
                print(f"    {row['parameter']} = {row['value']} "
                      f"({row['pct_change']:+.0f}% vs baseline)  MAC={row['mac_eur_t']} €/t")

    # Summary statistics
    total_cells = len(df)
    allowance_cells = (df["regime"] == "allowance_preferred").sum()
    cobenefit_cells = (df["regime"] == "co-benefit").sum() + \
                      (df["regime"] == "non-binding").sum()
    infeasible_cells = (df["regime"] == "infeasible").sum()

    print(f"\nSummary across all {total_cells} sensitivity cells:")
    print(f"  allowance_preferred: {allowance_cells} ({100*allowance_cells/total_cells:.0f}%)")
    print(f"  co-benefit/non-binding: {cobenefit_cells} ({100*cobenefit_cells/total_cells:.0f}%)")
    print(f"  infeasible: {infeasible_cells} ({100*infeasible_cells/total_cells:.0f}%)")
    print(f"  shift_preferred / parity: "
          f"{total_cells - allowance_cells - cobenefit_cells - infeasible_cells} "
          f"({100*(total_cells - allowance_cells - cobenefit_cells - infeasible_cells)/total_cells:.0f}%)")

    out_txt = os.path.join(RESULTS_DIR, "parameter_sensitivity_summary.txt")
    with open(out_txt, "w") as f:
        f.write("PARAMETER SENSITIVITY SUMMARY\n")
        f.write(f"Budget level: {ANALYSIS_BUDGET_PCT}%\n\n")
        pivot = df[df["carbon_price_eur_t"] == 65].pivot_table(
            index=["network", "parameter", "value"],
            values=["mac_eur_t", "regime"],
            aggfunc="first",
        )
        f.write(pivot.to_string())

    print(f"\nSaved: {out_csv}")
    print(f"Saved: {out_txt}")
    return df


if __name__ == "__main__":
    main()
