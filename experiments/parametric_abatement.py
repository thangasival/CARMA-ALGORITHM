"""
Parametric Abatement Cost Analysis
===================================
Generates marginal abatement cost (MAC) curves for three intermodal network
archetypes using parametric MILP budget sweeps.

This experiment is the empirical foundation for the shadow-price decision
analytics framework:
  - How does MAC vary with carbon-budget tightness, modal availability, and
    network structure? (RQ1)
  - When does MAC support physical mode shifting rather than carbon allowance
    purchase? (RQ2)
  - Under what conditions does the framework fail (flat MAC, infeasibility)? (F5)

Networks
--------
  1. Salamanca domestic   — 12 routes, 2 modes (truck / rail), Spain
  2. Iberian regional     — 12 routes, 3 modes (truck / rail / ship), Spain
  3. Frankfurt European   — 14 routes, 3 modes (truck / rail / air), Germany hub

Method
------
  Parametric MILP (ets_price=0): solve min-cost routing at each budget level
  B(p) = baseline_emissions × (1 - p/100), p ∈ {0, 5, 10, … 50}.

  Finite-difference MAC:
    λ̂(p) = [Z(p-5) - Z(p)] / [E(p-5) - E(p)]   (€ / kg CO2e)
            = marginal logistics cost of the last 5% emission reduction

  This avoids reliance on LP-relaxation duals for the MIP and is fully
  defensible for integer programmes.

  LP dual shadow price is also reported for comparison.

Decision-regime analysis
------------------------
  At each (network, budget) point, compare λ̂ to carbon price scenarios
  [25, 50, 65, 75, 100, 150] €/tonne:
    λ̂ < p_carbon  → mode shift economically preferred
    λ̂ ≈ p_carbon  → parity zone (within 10%)
    λ̂ > p_carbon  → carbon allowance purchase preferred

Outputs — experiments/results/
-------------------------------
  parametric_abatement_all.csv        combined sweep table for all networks
  decision_regime_all.csv             regime map (network × budget × carbon price)
  abatement_summary.txt               publication-ready summary table

Usage
-----
  python experiments/parametric_abatement.py
  python experiments/parametric_abatement.py --verbose
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithm.optimization.carbon_milp import CarbonBudgetMILP, MILPRoute

logger = logging.getLogger(__name__)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Network definitions
# ---------------------------------------------------------------------------

# EU emission factors (kg CO2e / tonne-km)
EF = {
    "truck": 0.0762,   # HBEFA 4.2 HDV Euro VI
    "rail":  0.0285,   # Eurostat 2022 Spanish rail (Spain grid 175 gCO2/kWh)
    "ship":  0.0110,   # Eurostat 2022 short-sea coastal
    "air":   0.6800,   # ICAO CORSIA 2022
}

# Cost per tonne-km (€)
COST_PER_TONKM = {
    "truck": 0.110,    # KPMG 2023 European FTL average
    "rail":  0.055,    # DB Cargo / RENFE intermodal incl. terminal amortised
    "ship":  0.028,    # Eurostat 2022 short-sea feeder
    "air":   9.500,    # Lufthansa Cargo rate card 2023
}

# Terminal / handling cost per shipment (€) when switching from truck baseline
TERMINAL_EUR = {
    "truck": 0.0,
    "rail":  680.0,    # Rail terminal loading + unloading
    "ship":  750.0,    # Port handling
    "air":   350.0,    # Airport handling
}

# Minimum feasible distance (km) per mode
MIN_DIST_KM = {
    "truck": 0.0,
    "rail":  150.0,    # Rail viable for ≥ 150 km freight (Salamanca / Iberian)
    "ship":  400.0,    # Short-sea feasible for ≥ 400 km
    "air":   0.0,
}


def build_milp_route(
    rid: str,
    origin: str,
    dest: str,
    dist_km: float,
    weight_t: float,
    current_mode: str = "truck",
    rail_min_km: float = 150.0,
    ship_min_km: float = 400.0,
    air_available: bool = False,
) -> MILPRoute:
    """Construct a MILPRoute with pre-computed cost/emission per feasible mode."""
    feasible = ["truck"]
    if dist_km >= rail_min_km:
        feasible.append("rail")
    if dist_km >= ship_min_km:
        feasible.append("ship")
    if air_available:
        feasible.append("air")

    cost_per_mode = {}
    emission_per_mode = {}
    for m in feasible:
        transfer = TERMINAL_EUR[m] if m != current_mode else 0.0
        cost_per_mode[m] = dist_km * weight_t * COST_PER_TONKM[m] + transfer
        emission_per_mode[m] = dist_km * weight_t * EF[m]

    r = MILPRoute(
        route_id=rid,
        origin=origin,
        destination=dest,
        distance_km=dist_km,
        weight_tons=weight_t,
        commodity_type="general",
        current_mode=current_mode,
        feasible_modes=feasible,
        cost_per_mode=cost_per_mode,
        emission_per_mode=emission_per_mode,
    )
    return r


# ---- Network 1: Salamanca domestic (12 routes, truck/rail) -----------------

SALAMANCA_RAW = [
    # (destination, dist_km, weight_t)   — all starting from Salamanca
    ("Zamora",      63,  8.5),
    ("Avila",       98,  7.2),
    ("Valladolid", 115,  9.8),
    ("Leon",       196, 11.0),
    ("Madrid",     212, 22.0),
    ("Caceres",    213,  8.0),
    ("Burgos",     246, 10.5),
    ("Merida",     261,  7.5),
    ("Santander",  355, 12.0),
    ("Bilbao",     375, 14.0),
    ("Seville",    398, 18.0),
    ("Barcelona",  510, 20.0),
]


def build_salamanca() -> list:
    routes = []
    for i, (dest, dist, wt) in enumerate(SALAMANCA_RAW):
        routes.append(build_milp_route(
            rid=f"SAL-{i+1:02d}",
            origin="Salamanca", dest=dest,
            dist_km=dist, weight_t=wt,
            rail_min_km=150.0, ship_min_km=9999.0,  # no ship
            air_available=False,
        ))
    return routes


# ---- Network 2: Iberian regional (12 routes, truck/rail/ship) --------------

IBERIAN_RAW = [
    # (origin, destination, dist_km, weight_t)
    ("Madrid",    "Barcelona",    620,  22.0),
    ("Madrid",    "Valencia",     590,   8.0),
    ("Madrid",    "Sevilla",      530,  14.0),
    ("Madrid",    "Bilbao",       395,  12.0),
    ("Madrid",    "Zaragoza",     325,   9.0),
    ("Madrid",    "Toledo",       280,   5.0),
    ("Bilbao",    "Barcelona",    620,  35.0),
    ("Barcelona", "Madrid",       620,  18.0),
    ("Valencia",  "Hamburg",     2200,  60.0),
    ("Bilbao",    "Madrid",       395,  12.0),
    ("Salamanca", "Barcelona",    510,   7.0),
    ("Algeciras", "Genova",      1800,  50.0),
]


def build_iberian() -> list:
    routes = []
    for i, (orig, dest, dist, wt) in enumerate(IBERIAN_RAW):
        routes.append(build_milp_route(
            rid=f"IBR-{i+1:02d}",
            origin=orig, dest=dest,
            dist_km=dist, weight_t=wt,
            rail_min_km=150.0, ship_min_km=400.0,
            air_available=False,
        ))
    return routes


# ---- Network 3: Frankfurt European hub (14 routes, truck/rail/air) ----------
# Rail EF uses German grid (higher than Spanish): 380 gCO2/kWh → 0.057 kg/t-km
EF_FRANKFURT = {
    "truck": 0.0762,
    "rail":  0.0570,   # Eurostat 2022 EU-27 average (German mix)
    "air":   0.6800,
    "ship":  0.0110,
}

FRANKFURT_RAW = [
    # (destination, dist_km, weight_t, air_ok)
    ("Prague CZ",    280,  8.0, False),
    ("Zurich CH",    350, 10.0, False),
    ("Amsterdam NL", 370, 12.0, False),
    ("Brussels BE",  395, 11.0, False),
    ("Hamburg DE",   480, 14.0, False),
    ("Berlin DE",    550, 13.0, False),
    ("Paris FR",     485, 15.0, False),
    ("Vienna AT",    620, 16.0, False),
    ("Warsaw PL",   1100, 18.0, True),   # air needed for express
    ("Milan IT",     700, 20.0, True),
    ("Lyon FR",      630, 14.0, False),
    ("Barcelona ES", 1500, 22.0, True),
    ("Madrid ES",   1800, 25.0, False),
    ("Budapest HU",  840, 12.0, False),
]


def build_frankfurt() -> list:
    routes = []
    for i, (dest, dist, wt, air_ok) in enumerate(FRANKFURT_RAW):
        feasible = ["truck"]
        if dist >= 150:
            feasible.append("rail")
        if air_ok:
            feasible.append("air")

        cost_per_mode = {}
        em_per_mode = {}
        for m in feasible:
            transfer = TERMINAL_EUR[m] if m != "truck" else 0.0
            cost_per_mode[m] = dist * wt * COST_PER_TONKM[m] + transfer
            em_per_mode[m] = dist * wt * EF_FRANKFURT[m]

        r = MILPRoute(
            route_id=f"FRA-{i+1:02d}",
            origin="Frankfurt", destination=dest,
            distance_km=dist, weight_tons=wt,
            commodity_type="general", current_mode="truck",
            feasible_modes=feasible,
            cost_per_mode=cost_per_mode,
            emission_per_mode=em_per_mode,
        )
        routes.append(r)
    return routes


# ---------------------------------------------------------------------------
# Parametric sweep core
# ---------------------------------------------------------------------------

BUDGET_LEVELS = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
CARBON_PRICES_EUR_T = [25, 50, 65, 75, 100, 150]   # €/tonne CO2e


def run_parametric_sweep(
    routes: list,
    network_name: str,
    verbose: bool = False,
) -> pd.DataFrame:
    """
    Solve MILP at each budget level, extract costs/emissions and LP dual.

    Returns a DataFrame with one row per budget level, including:
      - optimal_cost_eur, actual_emissions_kg, shadow_price_eur_kg (LP dual)
      - finite_diff_mac_eur_kg (λ̂) computed between adjacent budget levels
    """
    solver = CarbonBudgetMILP(ets_price_eur_per_kg=0.0)  # pure cost minimisation

    rows = []
    for pct in BUDGET_LEVELS:
        result = solver.optimise(routes, budget_reduction_pct=pct)
        rows.append({
            "network":               network_name,
            "reduction_pct":         pct,
            "carbon_budget_kg":      round(result.carbon_budget_kg, 1),
            "optimal_cost_eur":      round(result.total_cost, 2),
            "actual_emissions_kg":   round(result.total_emissions_kg, 1),
            "baseline_cost_eur":     round(result.baseline_cost, 2),
            "baseline_emissions_kg": round(result.baseline_emissions, 1),
            "cost_change_pct":       round(result.cost_change_pct, 2),
            "emission_change_pct":   round(result.emission_change_pct, 2),
            "lp_shadow_price_eur_kg": round(result.shadow_price_eur_per_kg or 0.0, 6),
            "n_mode_shifts":          len(result.mode_shifts),
            "status":                result.status,
        })
        if verbose:
            sp = result.shadow_price_eur_per_kg or 0.0
            logger.info(
                f"  {network_name} {pct:3d}%  cost=€{result.total_cost:>10,.0f}  "
                f"em={result.total_emissions_kg:>9,.0f} kg  λ*={sp:.4f} €/kg  "
                f"shifts={len(result.mode_shifts)}  {result.status}"
            )

    df = pd.DataFrame(rows)

    # ---- Finite-difference MAC ----
    # λ̂(p) = ΔCost / |ΔEmissions|  between level p and p-5
    # Positive λ̂ = achieving the additional 5% reduction costs this much
    # Negative λ̂ = the 5% reduction is co-beneficial (also saves cost)
    macs = [None]  # no previous level for 0%
    for i in range(1, len(df)):
        dCost = df.iloc[i]["optimal_cost_eur"] - df.iloc[i-1]["optimal_cost_eur"]
        dEm   = df.iloc[i-1]["actual_emissions_kg"] - df.iloc[i]["actual_emissions_kg"]
        if dEm > 1.0:
            mac = dCost / dEm  # €/kg CO2e
        else:
            mac = None  # negligible change in emissions
        macs.append(mac)

    df["finite_diff_mac_eur_kg"] = macs
    # Also compute in €/tonne for readability
    df["finite_diff_mac_eur_t"] = df["finite_diff_mac_eur_kg"].apply(
        lambda x: round(x * 1000, 2) if x is not None else None
    )
    df["lp_shadow_price_eur_t"] = df["lp_shadow_price_eur_kg"] * 1000

    return df


def build_decision_regimes(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each (network, budget) point, classify the decision regime vs
    each carbon price scenario.

    Classification:
      'shift'     if λ̂ < p_carbon × 0.90  (mode shift clearly preferred)
      'parity'    if 0.90 ≤ λ̂/p_carbon ≤ 1.10
      'allowance' if λ̂ > p_carbon × 1.10  (allowance purchase preferred)
      'infeasible' if no optimal solution
      'non-binding' if λ̂ ≤ 0 (co-benefit — shift saves both cost and carbon)
    """
    rows = []
    for _, row in df.iterrows():
        mac = row["finite_diff_mac_eur_kg"]
        for p_t in CARBON_PRICES_EUR_T:
            p_kg = p_t / 1000.0
            if row["status"] != "Optimal":
                regime = "infeasible"
            elif mac is None:
                regime = "non-binding"
            elif mac <= 0.0:
                regime = "co-benefit"
            else:
                ratio = mac / p_kg
                if ratio < 0.90:
                    regime = "shift_preferred"
                elif ratio <= 1.10:
                    regime = "parity"
                else:
                    regime = "allowance_preferred"
            rows.append({
                "network":              row["network"],
                "reduction_pct":        row["reduction_pct"],
                "carbon_price_eur_t":   p_t,
                "mac_eur_t":            row["finite_diff_mac_eur_t"],
                "regime":               regime,
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Summary table (publication-ready)
# ---------------------------------------------------------------------------

def print_abatement_table(df_all: pd.DataFrame):
    print("\n" + "=" * 90)
    print("MARGINAL ABATEMENT COST (MAC) BY NETWORK AND BUDGET LEVEL")
    print("  Units: €/tonne CO2e  |  'co-benefit' = shift saves cost AND carbon")
    print("=" * 90)
    pivot = df_all.pivot_table(
        index="reduction_pct",
        columns="network",
        values="finite_diff_mac_eur_t",
        aggfunc="first",
    )
    # Reorder columns
    ordered_cols = [c for c in ["Salamanca", "Iberian", "Frankfurt"] if c in pivot.columns]
    pivot = pivot[ordered_cols]
    print(pivot.to_string(float_format=lambda x: f"{x:>8.1f}"))
    print()


def print_regime_summary(df_regime: pd.DataFrame):
    print("\n" + "=" * 90)
    print("DECISION REGIME AT EU ETS PRICE SCENARIOS (Mode shift vs Allowance purchase)")
    print("  shift_preferred = MAC < p_carbon * 0.90")
    print("  parity          = MAC ~ p_carbon (+/-10%)")
    print("  allowance_pref  = MAC > p_carbon * 1.10")
    print("  co-benefit      = MAC <= 0 (shift profitable without carbon incentive)")
    print("=" * 90)
    for network in df_regime["network"].unique():
        print(f"\n--- {network} ---")
        sub = df_regime[df_regime["network"] == network]
        pivot = sub.pivot_table(
            index="reduction_pct",
            columns="carbon_price_eur_t",
            values="regime",
            aggfunc="first",
        )
        print(pivot.to_string())
    print()


def print_mode_shift_details(df_all: pd.DataFrame, routes_map: dict):
    print("\n" + "=" * 90)
    print("MODE SHIFT PROFILE AT 20% BUDGET REDUCTION (decision reference point)")
    print("=" * 90)
    for network in df_all["network"].unique():
        row = df_all[(df_all["network"] == network) & (df_all["reduction_pct"] == 20)]
        if row.empty:
            continue
        row = row.iloc[0]
        print(f"\n{network}:")
        print(f"  Baseline cost   : €{row['baseline_cost_eur']:>12,.0f}")
        print(f"  Optimal cost    : €{row['optimal_cost_eur']:>12,.0f}  ({row['cost_change_pct']:+.1f}%)")
        print(f"  Baseline emis.  : {row['baseline_emissions_kg']:>12,.0f} kg CO2e")
        print(f"  Optimal emis.   : {row['actual_emissions_kg']:>12,.0f} kg CO2e  ({row['emission_change_pct']:+.1f}%)")
        print(f"  Mode shifts     : {row['n_mode_shifts']}")
        print(f"  LP shadow price : {row['lp_shadow_price_eur_t']:.1f} €/t CO2e")
        print(f"  Finite-diff MAC : {row['finite_diff_mac_eur_t']} €/t CO2e")


def print_regime_at_ets(df_regime: pd.DataFrame, ets_price: int = 65):
    print(f"\n{'='*90}")
    print(f"DECISION REGIME AT EU ETS 2024 PRICE ({ets_price} €/t CO2e)")
    print(f"{'='*90}")
    sub = df_regime[df_regime["carbon_price_eur_t"] == ets_price]
    pivot = sub.pivot_table(
        index="reduction_pct",
        columns="network",
        values="regime",
        aggfunc="first",
    )
    ordered_cols = [c for c in ["Salamanca", "Iberian", "Frankfurt"] if c in pivot.columns]
    pivot = pivot[ordered_cols]
    print(pivot.to_string())
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(verbose: bool = False):
    logging.basicConfig(
        level=logging.INFO if verbose else logging.WARNING,
        format="%(levelname)s  %(message)s",
    )

    print("\n" + "=" * 90)
    print("PARAMETRIC ABATEMENT COST ANALYSIS — CARMA Shadow-Price Decision Framework")
    print("Three intermodal network archetypes | Budget sweep 0-50% | ets_price=0")
    print("=" * 90)

    networks = {
        "Salamanca": build_salamanca(),
        "Iberian":   build_iberian(),
        "Frankfurt": build_frankfurt(),
    }

    all_sweeps = []
    for name, routes in networks.items():
        print(f"\nRunning {name} parametric sweep ({len(routes)} routes)...")
        df = run_parametric_sweep(routes, name, verbose=verbose)
        all_sweeps.append(df)

    df_all = pd.concat(all_sweeps, ignore_index=True)
    df_regime = build_decision_regimes(df_all)

    # ---- Print summaries ----
    print_abatement_table(df_all)
    print_regime_at_ets(df_regime, ets_price=65)
    print_mode_shift_details(df_all, networks)
    print_regime_summary(df_regime)

    # ---- Save CSVs ----
    out_sweep = os.path.join(RESULTS_DIR, "parametric_abatement_all.csv")
    df_all.to_csv(out_sweep, index=False)
    print(f"Saved: {out_sweep}")

    out_regime = os.path.join(RESULTS_DIR, "decision_regime_all.csv")
    df_regime.to_csv(out_regime, index=False)
    print(f"Saved: {out_regime}")

    # ---- Print manuscript-ready numbers ----
    print("\n" + "=" * 90)
    print("MANUSCRIPT KEY NUMBERS")
    print("=" * 90)
    for network in ["Salamanca", "Iberian", "Frankfurt"]:
        sub = df_all[df_all["network"] == network]
        baseline = sub.iloc[0]["baseline_emissions_kg"]
        base_cost = sub.iloc[0]["baseline_cost_eur"]
        print(f"\n{network}:")
        print(f"  Baseline: {baseline:,.0f} kg CO2e, €{base_cost:,.0f}")
        print(f"  {'Budget%':>8} | {'Cost':>12} | {'Emissions':>12} | {'Δcost%':>8} | {'Δemis%':>8} | {'MAC(€/t)':>10} | {'LP λ(€/t)':>10} | {'Shifts':>6}")
        print(f"  {'-'*8}-+-{'-'*12}-+-{'-'*12}-+-{'-'*8}-+-{'-'*8}-+-{'-'*10}-+-{'-'*10}-+-{'-'*6}")
        for _, row in sub.iterrows():
            mac_str = f"{row['finite_diff_mac_eur_t']:.1f}" if row["finite_diff_mac_eur_t"] is not None else "  —"
            print(
                f"  {row['reduction_pct']:>8.0f}% | "
                f"€{row['optimal_cost_eur']:>11,.0f} | "
                f"{row['actual_emissions_kg']:>12,.0f} | "
                f"{row['cost_change_pct']:>+8.1f}% | "
                f"{row['emission_change_pct']:>+8.1f}% | "
                f"{mac_str:>10} | "
                f"{row['lp_shadow_price_eur_t']:>10.1f} | "
                f"{row['n_mode_shifts']:>6}"
            )

    return df_all, df_regime


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parametric abatement cost analysis")
    parser.add_argument("--verbose", action="store_true",
                        help="Print per-solve log lines")
    args = parser.parse_args()
    main(verbose=args.verbose)
