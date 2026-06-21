"""
Generated-Network Robustness Analysis
======================================
Validates that the carbon compliance regime taxonomy is a structural consequence
of modal economics, not an artifact of the three hand-built archetype examples.

Generates N_INSTANCES networks per archetype family with controlled variation,
runs the full parametric MAC sweep on each, and reports archetype-level
empirical regularities.

Archetype families
------------------
  1. Rail-limited domestic    — like Salamanca; truck/rail only, short-medium haul
  2. Maritime-accessible      — like Iberian; truck/rail/ship, long-haul corridors
  3. Hub limited redundancy   — like Frankfurt; truck/rail/air, European hub scale,
                                 higher rail emission factor

For each generated network:
  1. Solve unconstrained cost MILP.
  2. Check co-benefit condition.
  3. Run parametric budget sweep 0–50% in 5% steps.
  4. Compute finite-difference MAC at each level.
  5. Classify regime at EU ETS 65 €/t and 20% budget reference.
  6. Record maximum feasible abatement level.

Outputs
-------
  experiments/results/generated_network_results.csv     — per-instance detail
  experiments/results/generated_network_summary.csv     — archetype-level aggregate
  experiments/results/generated_network_summary.txt     — publication-ready table

Usage
-----
  python experiments/generated_network_robustness.py
  python experiments/generated_network_robustness.py --n 30        # fewer instances
  python experiments/generated_network_robustness.py --n 100       # more instances
"""
from __future__ import annotations

import argparse
import os
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from algorithm.optimization.carbon_milp import CarbonBudgetMILP, MILPRoute

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Base emission factors and costs (from parametric_abatement.py)
# ---------------------------------------------------------------------------
BASE_EF = {
    "truck": 0.0762,
    "rail":  0.0285,   # Spanish grid
    "ship":  0.0110,
    "air":   0.6800,
}
BASE_COST = {
    "truck": 0.110,
    "rail":  0.055,
    "ship":  0.028,
    "air":   9.500,
}

BUDGET_LEVELS    = list(range(0, 51, 5))
ETS_PRICE_EUR_T  = 65
REFERENCE_BUDGET = 20   # budget % for primary regime comparison
N_INSTANCES      = 50   # default instances per archetype


# ---------------------------------------------------------------------------
# Network generators
# ---------------------------------------------------------------------------

def _make_route(
    rid: str,
    dist_km: float,
    weight_t: float,
    feasible_modes: list[str],
    cost_rates: dict,
    emit_rates: dict,
    terminals: dict,
) -> MILPRoute:
    cost_per_mode = {}
    em_per_mode   = {}
    for m in feasible_modes:
        transfer = terminals.get(m, 0.0) if m != "truck" else 0.0
        cost_per_mode[m] = dist_km * weight_t * cost_rates[m] + transfer
        em_per_mode[m]   = dist_km * weight_t * emit_rates[m]
    return MILPRoute(
        route_id=rid,
        origin="O", destination=f"D{rid}",
        distance_km=dist_km, weight_tons=weight_t,
        commodity_type="general", current_mode="truck",
        feasible_modes=feasible_modes,
        cost_per_mode=cost_per_mode,
        emission_per_mode=em_per_mode,
    )


def generate_rail_limited_domestic(seed: int, n_routes: int | None = None) -> list[MILPRoute]:
    """
    Salamanca-family archetype.
    Characteristics: truck/rail only, domestic short-to-medium distances.
    Variation: rail terminal cost, route distances, weights, rail EF, rail min distance.
    """
    rng = np.random.default_rng(seed)

    if n_routes is None:
        n_routes = int(rng.integers(8, 17))  # 8–16 routes

    # Archetype-level parameters
    rail_terminal = float(rng.uniform(350, 950))          # €350–950 per shipment
    rail_min_km   = float(rng.uniform(100, 220))          # 100–220 km min for rail
    rail_cost_mult = float(rng.uniform(0.80, 1.20))       # ±20% rail cost
    truck_cost_mult = float(rng.uniform(0.85, 1.15))      # ±15% truck cost
    rail_ef_mult   = float(rng.uniform(0.70, 1.35))       # ±30% rail EF

    cost_rates = {
        "truck": BASE_COST["truck"] * truck_cost_mult,
        "rail":  BASE_COST["rail"]  * rail_cost_mult,
    }
    emit_rates = {
        "truck": BASE_EF["truck"],
        "rail":  BASE_EF["rail"] * rail_ef_mult,
    }
    terminals = {"truck": 0.0, "rail": rail_terminal}

    routes = []
    for i in range(n_routes):
        dist   = float(np.clip(rng.lognormal(np.log(220), 0.65), 40, 700))
        weight = float(np.clip(rng.lognormal(np.log(11),  0.45), 2, 55))
        feasible = ["truck"]
        if dist >= rail_min_km:
            feasible.append("rail")
        routes.append(_make_route(f"R{i:02d}", dist, weight, feasible,
                                  cost_rates, emit_rates, terminals))
    return routes


def generate_maritime_accessible(seed: int, n_routes: int | None = None) -> list[MILPRoute]:
    """
    Iberian-family archetype.
    Characteristics: truck/rail/ship; mix of domestic and long-haul international.
    Variation: ship terminal, ship min distance, fraction of long-haul routes.
    Structural invariant: ship is cost- AND emission-dominant on long routes (co-benefit).
    """
    rng = np.random.default_rng(seed)

    if n_routes is None:
        n_routes = int(rng.integers(9, 17))  # 9–16 routes

    # Archetype-level parameters
    rail_terminal = float(rng.uniform(500, 850))
    ship_terminal = float(rng.uniform(500, 1100))
    rail_min_km   = float(rng.uniform(150, 300))
    ship_min_km   = float(rng.uniform(350, 700))
    n_long_haul   = int(rng.integers(2, min(6, n_routes // 2 + 1)))

    # Ship cost varies: must stay below truck for long routes (structural property)
    ship_cost_mult = float(rng.uniform(0.85, 1.10))   # ship still cheapest per t-km
    rail_cost_mult = float(rng.uniform(0.80, 1.20))
    truck_cost_mult = float(rng.uniform(0.85, 1.15))

    cost_rates = {
        "truck": BASE_COST["truck"] * truck_cost_mult,
        "rail":  BASE_COST["rail"]  * rail_cost_mult,
        "ship":  BASE_COST["ship"]  * ship_cost_mult,
    }
    emit_rates = {
        "truck": BASE_EF["truck"],
        "rail":  BASE_EF["rail"] * float(rng.uniform(0.80, 1.10)),
        "ship":  BASE_EF["ship"] * float(rng.uniform(0.90, 1.10)),
    }
    terminals = {"truck": 0.0, "rail": rail_terminal, "ship": ship_terminal}

    routes = []
    # Long-haul routes (ship eligible)
    for i in range(n_long_haul):
        dist   = float(np.clip(rng.lognormal(np.log(1500), 0.45), 600, 3000))
        weight = float(np.clip(rng.lognormal(np.log(35), 0.55), 10, 120))
        feasible = ["truck", "rail", "ship"]
        routes.append(_make_route(f"LH{i:02d}", dist, weight, feasible,
                                  cost_rates, emit_rates, terminals))
    # Medium / domestic routes
    for i in range(n_routes - n_long_haul):
        dist   = float(np.clip(rng.lognormal(np.log(350), 0.55), 100, 800))
        weight = float(np.clip(rng.lognormal(np.log(12), 0.40), 3, 40))
        feasible = ["truck"]
        if dist >= rail_min_km:
            feasible.append("rail")
        if dist >= ship_min_km:
            feasible.append("ship")
        routes.append(_make_route(f"MD{i:02d}", dist, weight, feasible,
                                  cost_rates, emit_rates, terminals))
    return routes


def generate_hub_limited_redundancy(seed: int, n_routes: int | None = None) -> list[MILPRoute]:
    """
    Frankfurt-family archetype.
    Characteristics: truck/rail with some air; European hub scale; higher rail EF.
    Variation: rail terminal, German/EU-avg rail EF, air fraction, distances.
    Structural invariant: co-benefit co-exists with hard ceiling above ~20-30%.
    """
    rng = np.random.default_rng(seed)

    if n_routes is None:
        n_routes = int(rng.integers(10, 19))   # 10–18 routes

    # European/German-grid rail EF: 0.040–0.075 kg/t-km (higher than Spanish 0.0285)
    rail_ef        = float(rng.uniform(0.040, 0.075))
    rail_terminal  = float(rng.uniform(500, 950))
    air_fraction   = float(rng.uniform(0.10, 0.30))
    n_air          = max(1, int(round(n_routes * air_fraction)))

    rail_cost_mult  = float(rng.uniform(0.80, 1.20))
    truck_cost_mult = float(rng.uniform(0.85, 1.15))

    cost_rates = {
        "truck": BASE_COST["truck"] * truck_cost_mult,
        "rail":  BASE_COST["rail"]  * rail_cost_mult,
        "air":   BASE_COST["air"],
    }
    emit_rates = {
        "truck": BASE_EF["truck"],
        "rail":  rail_ef,
        "air":   BASE_EF["air"],
    }
    terminals = {"truck": 0.0, "rail": rail_terminal, "air": 350.0}

    routes = []
    for i in range(n_routes):
        dist   = float(np.clip(rng.lognormal(np.log(650), 0.65), 150, 2500))
        weight = float(np.clip(rng.lognormal(np.log(14),  0.45), 4, 60))
        feasible = ["truck", "rail"]   # all routes rail-eligible at hub distances
        if i < n_air:
            feasible.append("air")
        routes.append(_make_route(f"H{i:02d}", dist, weight, feasible,
                                  cost_rates, emit_rates, terminals))
    return routes


GENERATORS = {
    "rail_limited_domestic":     generate_rail_limited_domestic,
    "maritime_accessible":       generate_maritime_accessible,
    "hub_limited_redundancy":    generate_hub_limited_redundancy,
}


# ---------------------------------------------------------------------------
# Single-instance analysis
# ---------------------------------------------------------------------------

def analyse_instance(routes: list, network_id: str) -> dict:
    """
    Run full parametric sweep for one generated network.
    Returns a flat dict of key metrics.
    """
    solver = CarbonBudgetMILP(ets_price_eur_per_kg=0.0)

    # Unconstrained optimum
    r0 = solver.optimise(routes, budget_reduction_pct=0)
    baseline_cost = r0.baseline_cost
    baseline_em   = r0.baseline_emissions
    uncon_cost    = r0.total_cost
    uncon_em      = r0.total_emissions_kg
    uncon_shifts  = len(r0.mode_shifts)

    cobenefit_pct = 100 * (baseline_em - uncon_em) / baseline_em if baseline_em > 0 else 0
    is_cobenefit  = cobenefit_pct > 5.0  # unconstrained already decarbonizes > 5%

    # Parametric sweep
    sweep_rows = []
    prev_cost   = uncon_cost
    prev_em     = uncon_em
    max_feasible_pct = 0

    for pct in BUDGET_LEVELS:
        res = solver.optimise(routes, budget_reduction_pct=pct)
        if res.status == "Optimal":
            max_feasible_pct = pct
            mac_kg = None
            if pct > 0:
                dCost = res.total_cost - prev_cost
                dEm   = prev_em - res.total_emissions_kg
                if dEm > 0.5:
                    mac_kg = dCost / dEm
            sweep_rows.append({
                "pct": pct,
                "cost": res.total_cost,
                "em":   res.total_emissions_kg,
                "mac_kg": mac_kg,
                "status": "Optimal",
            })
            prev_cost = res.total_cost
            prev_em   = res.total_emissions_kg
        else:
            sweep_rows.append({"pct": pct, "cost": None, "em": None,
                                "mac_kg": None, "status": "Infeasible"})

    # Regime at reference budget (20%) and ETS 65 €/t
    ref_row = next(
        (r for r in sweep_rows if r["pct"] == REFERENCE_BUDGET), None
    )
    mac_at_ref   = ref_row["mac_kg"] if ref_row else None
    status_at_ref = ref_row["status"] if ref_row else "Infeasible"

    def _regime(mac_kg, status):
        p_kg = ETS_PRICE_EUR_T / 1000.0
        if status != "Optimal":
            return "infeasible"
        if mac_kg is None:
            return "non-binding"
        if mac_kg <= 0:
            return "co-benefit"
        ratio = mac_kg / p_kg
        if ratio < 0.90:
            return "shift_preferred"
        if ratio <= 1.10:
            return "parity"
        return "allowance_preferred"

    regime_at_ref = _regime(mac_at_ref, status_at_ref)

    # Median MAC across all binding budget levels
    mac_vals = [
        r["mac_kg"] * 1000
        for r in sweep_rows
        if r["mac_kg"] is not None and r["mac_kg"] > 0
    ]
    median_mac = float(np.median(mac_vals)) if mac_vals else None

    return {
        "network_id":             network_id,
        "n_routes":               len(routes),
        "baseline_cost_eur":      round(baseline_cost, 0),
        "baseline_em_kg":         round(baseline_em, 0),
        "uncon_cost_eur":         round(uncon_cost, 0),
        "uncon_em_kg":            round(uncon_em, 0),
        "uncon_shifts":           uncon_shifts,
        "cobenefit_pct_uncon":    round(cobenefit_pct, 1),
        "is_cobenefit":           is_cobenefit,
        "max_feasible_pct":       max_feasible_pct,
        "mac_at_ref_eur_t":       round(mac_at_ref * 1000, 0) if mac_at_ref is not None else None,
        "regime_at_ref":          regime_at_ref,
        "median_mac_eur_t":       round(median_mac, 0) if median_mac is not None else None,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(n_instances: int = N_INSTANCES):
    print(f"\n{'='*80}")
    print(f"GENERATED-NETWORK ROBUSTNESS ANALYSIS")
    print(f"  {n_instances} instances per archetype family ({3 * n_instances} total)")
    print(f"  {len(BUDGET_LEVELS)} budget levels per instance")
    print(f"  Reference: {REFERENCE_BUDGET}% budget @ EU ETS {ETS_PRICE_EUR_T} €/t")
    print(f"{'='*80}")

    all_rows = []

    for family_name, generator in GENERATORS.items():
        print(f"\nFamily: {family_name}")
        family_rows = []

        for inst_idx in range(n_instances):
            seed = (hash(family_name) + inst_idx * 97) % (2**31)
            routes = generator(seed)
            net_id = f"{family_name[:3].upper()}-{inst_idx:03d}"

            try:
                result = analyse_instance(routes, net_id)
                result["family"] = family_name
                result["seed"]   = seed
                family_rows.append(result)

                if (inst_idx + 1) % 10 == 0:
                    print(f"  [{inst_idx+1:3d}/{n_instances}] "
                          f"  recent regime: {result['regime_at_ref']}"
                          f"  MAC={result['mac_at_ref_eur_t']} €/t"
                          f"  max_feas={result['max_feasible_pct']}%")
            except Exception as e:
                print(f"  [{inst_idx+1:3d}] ERROR: {e}")

        all_rows.extend(family_rows)

    df = pd.DataFrame(all_rows)

    # ---- Aggregate summary per family ----
    summary_rows = []
    for family_name in GENERATORS:
        sub = df[df["family"] == family_name]
        n = len(sub)
        if n == 0:
            continue

        regime_counts = sub["regime_at_ref"].value_counts()
        summary_rows.append({
            "family":                family_name,
            "n_instances":           n,
            "pct_cobenefit":         round(100 * regime_counts.get("co-benefit", 0) / n, 1),
            "pct_nonbinding":        round(100 * (regime_counts.get("non-binding", 0)
                                                  + sub["is_cobenefit"].sum()) / n, 1),
            "pct_shift_preferred":   round(100 * regime_counts.get("shift_preferred", 0) / n, 1),
            "pct_parity":            round(100 * regime_counts.get("parity", 0) / n, 1),
            "pct_allowance_preferred": round(100 * regime_counts.get("allowance_preferred", 0) / n, 1),
            "pct_infeasible_at_ref": round(100 * regime_counts.get("infeasible", 0) / n, 1),
            "median_mac_eur_t":      round(sub["median_mac_eur_t"].dropna().median(), 0)
                                     if sub["median_mac_eur_t"].dropna().size > 0 else None,
            "median_max_feas_pct":   round(sub["max_feasible_pct"].median(), 1),
            "pct_cobenefit_uncon":   round(100 * sub["is_cobenefit"].mean(), 1),
        })

    df_summary = pd.DataFrame(summary_rows)

    # ---- Print publication-ready table ----
    print(f"\n{'='*90}")
    print("GENERATED-NETWORK ROBUSTNESS SUMMARY")
    print(f"Regime classification at {REFERENCE_BUDGET}% budget reduction, EU ETS {ETS_PRICE_EUR_T} €/t")
    print(f"{'='*90}")
    print(f"\n{'Family':<30} {'N':>4}  {'Co-ben%':>7} {'Non-bind%':>10} "
          f"{'Allow%':>7} {'Shift%':>7} {'Infeas%':>8}  {'Med.MAC':>8} {'MaxFeas%':>9}")
    print("-" * 90)
    for _, row in df_summary.iterrows():
        # Co-benefit can come from two sources: regime_at_ref="co-benefit" OR
        # unconstrained already decarbonizes (is_cobenefit).
        # Use pct_nonbinding + pct_cobenefit combined:
        cobenefit_total = row["pct_cobenefit"] + row["pct_nonbinding"]
        print(f"  {row['family']:<28} {row['n_instances']:>4}  "
              f"{cobenefit_total:>7.1f}%  "
              f"{'':>10}  "
              f"{row['pct_allowance_preferred']:>6.1f}%  "
              f"{row['pct_shift_preferred']:>6.1f}%  "
              f"{row['pct_infeasible_at_ref']:>7.1f}%  "
              f"{str(row['median_mac_eur_t']) + ' €/t':>12}  "
              f"{row['median_max_feas_pct']:>6.1f}%")
    print()

    # ---- Print regime distribution detail ----
    print(f"{'='*90}")
    print("REGIME DISTRIBUTION DETAIL (at 20% budget, 65 €/t)")
    print(f"{'='*90}")
    for _, row in df_summary.iterrows():
        print(f"\n  {row['family']} (n={row['n_instances']}):")
        print(f"    Non-binding / co-benefit : {row['pct_cobenefit'] + row['pct_nonbinding']:.1f}%")
        print(f"    Allowance preferred      : {row['pct_allowance_preferred']:.1f}%")
        print(f"    Mode shift preferred     : {row['pct_shift_preferred']:.1f}%")
        print(f"    Parity zone              : {row['pct_parity']:.1f}%")
        print(f"    Infeasible at {REFERENCE_BUDGET}%         : {row['pct_infeasible_at_ref']:.1f}%")
        print(f"    Median MAC across budgets: {row['median_mac_eur_t']} €/t")
        print(f"    Median max feasible abat.: {row['median_max_feas_pct']}%")
        print(f"    Networks w/ unconstrained")
        print(f"      co-benefit (>5% free)  : {row['pct_cobenefit_uncon']:.1f}%")

    # ---- Save results ----
    out_detail = os.path.join(RESULTS_DIR, "generated_network_results.csv")
    out_summary = os.path.join(RESULTS_DIR, "generated_network_summary.csv")
    out_txt     = os.path.join(RESULTS_DIR, "generated_network_summary.txt")

    df.to_csv(out_detail, index=False)
    df_summary.to_csv(out_summary, index=False)

    with open(out_txt, "w") as f:
        f.write(f"GENERATED-NETWORK ROBUSTNESS SUMMARY\n")
        f.write(f"N = {n_instances} instances per archetype\n")
        f.write(f"Reference: {REFERENCE_BUDGET}% budget @ {ETS_PRICE_EUR_T} €/t\n\n")
        f.write(df_summary.to_string(index=False))
        f.write("\n\nDetailed regime distribution:\n")
        for _, row in df_summary.iterrows():
            f.write(f"\n{row['family']}:\n")
            f.write(f"  Co-benefit/non-binding:   {row['pct_cobenefit'] + row['pct_nonbinding']:.1f}%\n")
            f.write(f"  Allowance preferred:       {row['pct_allowance_preferred']:.1f}%\n")
            f.write(f"  Shift preferred:           {row['pct_shift_preferred']:.1f}%\n")
            f.write(f"  Infeasible at {REFERENCE_BUDGET}%:         {row['pct_infeasible_at_ref']:.1f}%\n")
            f.write(f"  Median MAC:                {row['median_mac_eur_t']} €/t\n")
            f.write(f"  Median max feasible:       {row['median_max_feas_pct']}%\n")

    print(f"\nSaved: {out_detail}")
    print(f"Saved: {out_summary}")
    print(f"Saved: {out_txt}")

    return df, df_summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generated-network robustness analysis")
    parser.add_argument("--n", type=int, default=N_INSTANCES,
                        help=f"Instances per archetype family (default: {N_INSTANCES})")
    args = parser.parse_args()
    main(n_instances=args.n)
