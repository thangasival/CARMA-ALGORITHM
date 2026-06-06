"""
USA Case Study: Los Angeles National Distribution Hub
======================================================
Quasi-real case study demonstrating the CARMA pipeline on a US West Coast
distribution hub (Port of Los Angeles) with freight routes to 14 major US
cities across all transport modes.

Data Sources:
- Distances:      US highway network (OpenStreetMap, BTS freight atlas)
- Freight costs:  BTS Commodity Flow Survey 2022 (USD/ton-km)
- Emission factors: EPA Supply Chain GHG Emission Factors v1.3 (2024)
- Grid CI:        EPA eGRID 2022 — national average + CA, TX regional profiles
- Rail corridors: BNSF / Union Pacific intermodal (LA->Chicago: 3 days)
- Maritime:       US coastwise trade (Jones Act carriers: Pacific -> Gulf/Atlantic)

Author: Sivalingam Thangavel <th.sivalingam@gmail.com>
Project: CARMA-ALGORITHM v1.0.0
"""

import sys
import os
import warnings
import logging
import json
import time

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
logging.basicConfig(level=logging.WARNING, format="%(levelname)s  %(message)s")

from algorithm.optimization.nsga3_optimizer import Route as NSGARoute
from algorithm.carma import CARMA, CARMAConfig

# ---------------------------------------------------------------------------
# Network definition — Port of Los Angeles hub -> 14 US cities
# ---------------------------------------------------------------------------
# Columns: destination, dist_km, demand_tons, preferred_mode,
#          temp_c, congestion, slope_deg, weather, egrid_region
US_NETWORK = [
    # -- Southwest corridor --------------------------------------------------
    ("Phoenix AZ",        597,   85, "truck", 32.0, 1.2, 0.5, "clear", "WECC_SW"),
    ("Las Vegas NV",      435,   60, "truck", 28.0, 1.3, 0.3, "clear", "WECC_SW"),
    # -- Pacific Coast -------------------------------------------------------
    ("San Francisco CA",  559,   90, "truck", 18.0, 1.5, 1.5, "clear", "WECC_CA"),
    ("Portland OR",      1769,   70, "rail",  14.0, 1.1, 2.0, "rain",  "WECC_NW"),
    ("Seattle WA",       1946,   80, "ship",  12.0, 1.1, 0.0, "rain",  "WECC_NW"),
    # -- Mountain / Interior -------------------------------------------------
    ("Salt Lake City UT", 1067,  55, "truck",  8.0, 1.1, 3.5, "clear", "WECC_SW"),
    ("Denver CO",        1739,   65, "rail",  10.0, 1.1, 4.0, "clear", "WECC_SW"),
    # -- South / Gulf Coast --------------------------------------------------
    ("Dallas TX",        2298,   95, "truck", 22.0, 1.4, 0.5, "clear", "ERCOT"),
    ("Houston TX",       2525,  110, "ship",  24.0, 1.0, 0.0, "clear", "ERCOT"),
    # -- Midwest -------------------------------------------------------------
    ("Chicago IL",       3214,  130, "rail",  16.0, 1.6, 0.5, "rain",  "MRO"),
    ("Kansas City MO",   2636,   75, "rail",  18.0, 1.3, 0.5, "clear", "MRO"),
    # -- Southeast -----------------------------------------------------------
    ("Atlanta GA",       3474,   85, "truck", 22.0, 1.4, 0.5, "rain",  "SERC"),
    # -- East Coast ----------------------------------------------------------
    ("New York NY",      4490,   70, "ship",  15.0, 1.8, 0.5, "rain",  "NPCC"),
    ("Miami FL",         4356,   60, "ship",  30.0, 1.0, 0.0, "clear", "FRCC"),
]

# EPA eGRID 2022 average CO2 intensity by NERC region (g CO2/kWh)
EGRID_REGIONS = {
    "WECC_CA": ("California",       205, "High solar/wind (duck curve)"),
    "WECC_NW": ("Pacific NW",       103, "Hydro-dominant — cleanest US grid"),
    "WECC_SW": ("Southwest",        435, "Gas peakers, high summer AC load"),
    "ERCOT":   ("Texas",            393, "Gas + growing wind capacity"),
    "MRO":     ("Upper Midwest",    528, "Coal transitioning to wind"),
    "SERC":    ("Southeast",        381, "Gas + nuclear mix"),
    "NPCC":    ("Northeast",        213, "Nuclear + hydro base"),
    "FRCC":    ("Florida",          481, "Gas-heavy, peak AC demand"),
}

# BTS 2022 US freight costs (USD/ton-km) and EPA emission factors (kg CO2e/ton-km)
MODE_DATA = {
    "truck": {"cost": 0.122, "ef": 0.097, "speed": 90},
    "rail":  {"cost": 0.058, "ef": 0.027, "speed": 55},
    "ship":  {"cost": 0.029, "ef": 0.011, "speed": 22},
    "air":   {"cost": 14.20, "ef": 0.680, "speed": 900},
}


# ---------------------------------------------------------------------------
# Training data — US freight profile (EPA emission factors)
# ---------------------------------------------------------------------------

def make_us_training_df(seed: int = 42) -> pd.DataFrame:
    np.random.seed(seed)
    n = 140
    modes = ["truck"] * 65 + ["rail"] * 40 + ["ship"] * 25 + ["air"] * 10
    np.random.shuffle(modes)

    rows = []
    for i in range(n):
        mode  = modes[i]
        m     = MODE_DATA[mode]
        dist  = np.random.uniform(200, 5000)
        wt    = np.random.uniform(1, 130)
        em    = dist * wt * m["ef"] * np.random.uniform(0.85, 1.15)
        speed = m["speed"]
        cong  = round(np.random.uniform(1.0, 2.3), 2)
        temp  = round(np.random.uniform(-15, 42), 1)
        slope = round(np.random.uniform(0.0, 5.0), 2)
        load  = round(np.random.uniform(0.3, 1.0), 2)
        spd   = round(speed * np.random.uniform(0.7, 1.1), 1)
        rows.append({
            "route_id":                  f"US{i:04d}",
            "transport_mode":            mode,
            "distance_km":               round(dist, 1),
            "weight_tons":               round(wt, 2),
            "total_emission_kg":         round(em, 2),
            "adjusted_emissions_kg_co2e": round(em, 2),
            "fuel_cost_eur":             round(dist * m["cost"] * wt, 1),
            "transit_time_hours":        round(dist / speed, 2),
            "cargo_type":                "general",
            "commodity_type":            "general",
            "is_hazardous":              False,
            "is_weekend":                bool(np.random.rand() > 0.8),
            "is_peak_hour":              bool(np.random.rand() > 0.7),
            "temperature_c":             temp,
            "congestion_factor":         cong,
            "slope_degrees":             slope,
            "is_uphill":                 bool(np.random.rand() > 0.5),
            "weather_condition":         np.random.choice(
                                             ["clear", "rain", "snow"],
                                             p=[0.60, 0.28, 0.12]),
            "load_factor":               load,
            "speed_kmh":                 spd,
            "actual_speed_kmh":          spd,
            "optimal_speed_kmh":         speed,
            "speed_ratio":               round(spd / speed, 3),
            "payload_efficiency":        load,
            "distance_category":         ("short" if dist < 500
                                          else "medium" if dist < 1800
                                          else "long"),
            "env_efficiency_simple":         round(em / (dist * wt + 1e-6), 6),
            "physics_emission_simple":       round(em * 0.95, 2),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Build NSGARoute objects
# ---------------------------------------------------------------------------

def make_nsga_routes() -> list:
    routes = []
    for (dest, dist, wt, mode, temp, cong, slope, weather, _egrid) in US_NETWORK:
        r = NSGARoute(
            origin="Los Angeles CA",
            destination=dest,
            distance_km=float(dist),
            weight_tons=float(wt),
            commodity_type="general",
            transport_mode=mode,
            temperature_c=float(temp),
            congestion_factor=float(cong),
            slope_degrees=float(slope),
            weather_condition=weather,
            is_weekend=False,
        )
        routes.append(r)
    return routes


# ---------------------------------------------------------------------------
# Baseline: truck-only (no optimization)
# ---------------------------------------------------------------------------

def compute_baseline() -> tuple:
    """Truck-only baseline cost and emissions."""
    total_cost = total_em = 0.0
    rows = []
    for (dest, dist, wt, _, *_rest) in US_NETWORK:
        cost = dist * wt * MODE_DATA["truck"]["cost"]
        em   = dist * wt * MODE_DATA["truck"]["ef"]
        total_cost += cost
        total_em   += em
        rows.append({"destination": dest, "dist_km": dist, "demand_t": wt,
                     "mode": "truck", "cost_usd": cost, "em_kg": em})
    return total_cost, total_em, pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def banner(title: str):
    print("\n" + "=" * 72)
    print(f"  {title}")
    print("=" * 72)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    banner("CARMA-ALGORITHM — USA Case Study")
    print(f"""
  Origin hub   : Port of Los Angeles, CA
                 (Largest US container port — 9.9M TEU/year, 2022)
  Destinations : {len(US_NETWORK)} major US cities across all NERC regions
  Modes        : Truck (highway), Rail (BNSF/UP intermodal), Maritime (Jones Act)
  Budget       : 20% CO2e reduction vs truck-only baseline
  Currency     : USD (BTS 2022 freight cost data)
  Grid CI      : EPA eGRID 2022 — US national + CA/TX regional profiles
  Carbon price : US Social Cost of Carbon — $51/tonne (EPA 2023 central estimate)
    """)

    # --- Inputs ---
    routes      = make_nsga_routes()
    training_df = make_us_training_df()
    b_cost, b_em, b_df = compute_baseline()

    print(f"  Routes        : {len(routes)}")
    print(f"  Training rows : {len(training_df)}")
    print(f"  Mode mix      : {training_df['transport_mode'].value_counts().to_dict()}")
    print(f"\n  Truck-only baseline:")
    print(f"    Total cost     : ${b_cost:>12,.0f}")
    print(f"    Total emissions: {b_em:>12,.0f} kg CO2e")

    # --- CARMA config ---
    config = CARMAConfig(
        grid_ci_g_kwh               = 205.0,   # CA eGRID departure-origin grid
        ensemble_strategy           = "segmented",
        ml_test_size                = 0.20,
        carbon_budget_reduction_pct = 20.0,
        ets_price_eur_per_tonne     = 51.0,    # US SCC $51/tonne (EPA 2023)
        nsga3_population            = 92,
        nsga3_generations           = 100,
        nsga3_partitions            = 6,
        enable_dynamic_ci           = True,
        origin_country              = "US",    # EPA eGRID 2022 US national profile
        time_flexibility_hours      = 10.0,
        preference_weights          = {
            "cost":        0.35,
            "emissions":   0.45,
            "time":        0.10,
            "reliability": 0.10,
        },
    )

    # --- Run CARMA ---
    banner("Running CARMA 6-Phase Pipeline")
    t0     = time.time()
    result = CARMA(config).run(routes, training_df=training_df)
    elapsed = time.time() - t0
    result.print_summary()

    # --- Route-level comparison table ---
    banner("Route-Level Comparison: Truck-Only Baseline vs CARMA MILP")
    print(f"\n  {'Route':<26} {'km':>5} {'t':>4} "
          f"{'Bsl mode':>9} {'Bsl em':>9} "
          f"{'Opt mode':>9} {'Opt em':>9} {'Save%':>7}")
    print("  " + "-" * 82)

    milp_assignments = result.milp_mode_assignments or {}
    total_b_em = total_o_em = total_b_cost = total_o_cost = 0.0
    for (dest, dist, wt, def_mode, *_rest) in US_NETWORK:
        b_m  = "truck"
        o_m  = milp_assignments.get(dest, def_mode)
        b_em = dist * wt * MODE_DATA["truck"]["ef"]
        o_em = dist * wt * MODE_DATA.get(o_m, MODE_DATA["truck"])["ef"]
        b_c  = dist * wt * MODE_DATA["truck"]["cost"]
        o_c  = dist * wt * MODE_DATA.get(o_m, MODE_DATA["truck"])["cost"]
        save = (b_em - o_em) / b_em * 100 if b_em > 0 else 0.0
        flag = " <" if b_m != o_m else ""
        print(f"  LA->{dest:<23} {dist:>5,.0f} {wt:>4.0f} "
              f"{b_m:>9} {b_em:>9,.0f} "
              f"{o_m:>9} {o_em:>9,.0f} {save:>6.1f}%{flag}")
        total_b_em   += b_em;  total_o_em   += o_em
        total_b_cost += b_c;   total_o_cost += o_c

    print("  " + "-" * 82)
    tot_em_save = (total_b_em - total_o_em) / total_b_em * 100
    tot_c_chg   = (total_o_cost - total_b_cost) / total_b_cost * 100
    print(f"  {'TOTAL NETWORK':<26} "
          f"{'':>5} {'':>4} {'truck':>9} {total_b_em:>9,.0f} "
          f"{'CARMA':>9} {total_o_em:>9,.0f} {tot_em_save:>6.1f}%")
    print(f"\n  Cost change vs truck-only: {tot_c_chg:+.1f}%  "
          f"(CARMA premium for 20% emission reduction)")

    # --- eGRID regional context ---
    banner("US Regional Grid Carbon Intensity — EPA eGRID 2022")
    print(f"\n  {'Region':<16} {'NERC':<10} {'g CO2/kWh':>10}   Profile")
    print("  " + "-" * 70)
    for code, (name, ci, note) in EGRID_REGIONS.items():
        bar = "#" * (ci // 55)
        print(f"  {name:<16} {code:<10} {ci:>10}   {bar}  {note}")

    # --- Pareto front ---
    if result.pareto_front:
        banner(f"DCCT-NSGA-III — Certificate-Anchored Pareto Front "
               f"({result.n_pareto_solutions} solutions)")
        print(f"\n  {'#':>3}  {'Cost (USD)':>12}  {'Emissions (kg)':>14}  "
              f"{'Time (h)':>10}  {'Disruption':>11}")
        print("  " + "-" * 58)
        for i, sol in enumerate(result.pareto_front[:10]):
            print(f"  {i+1:>3}  {sol['total_cost']:>12,.0f}  "
                  f"{sol['total_emissions_kg']:>14,.0f}  "
                  f"{sol['total_time_hours']:>10.1f}  "
                  f"{sol['avg_unreliability']:>11.3f}")

    # --- Dynamic CI schedule ---
    if result.dynamic_schedules:
        banner("Dynamic CI Departure Schedule (EPA eGRID 2022 US national profile)")
        print(f"\n  {'Route ID':<14} {'Mode':<8} {'Elec?':<6} "
              f"{'Base h':>7} {'Opt h':>6} {'Save kg':>9} {'%':>6}")
        print("  " + "-" * 60)
        for s in result.dynamic_schedules:
            elec = "yes" if s["is_electric"] else "no"
            print(f"  {s['route_id']:<14} {s['mode']:<8} {elec:<6} "
                  f"  {int(s['baseline_dep']):02d}:00  "
                  f"{int(s['optimal_dep']):02d}:00  "
                  f"{s['saving_kg']:>9.1f}  {s['saving_pct']:>5.1f}%")

    # --- US Social Cost of Carbon analysis ---
    banner("US Social Cost of Carbon Analysis (EPA 2023)")
    milp_em_save_kg   = abs(result.milp_emission_pct) / 100 * b_em
    annual_em_save_t  = milp_em_save_kg * 52 / 1000
    annual_ci_save_t  = result.dynamic_ci_saving_kg * 52 / 1000
    total_annual_save_t = annual_em_save_t + annual_ci_save_t

    print(f"""
  Annual MILP emission saving  : {annual_em_save_t:>8.1f} t CO2e/year
  Annual Dynamic CI saving     : {annual_ci_save_t:>8.1f} t CO2e/year
  Combined annual saving       : {total_annual_save_t:>8.1f} t CO2e/year

  Monetary value at US SCC estimates:
    $51/t  (EPA 2023 central):   ${total_annual_save_t * 51:>10,.0f}/year
    $190/t (IWG 2021 revised):   ${total_annual_save_t * 190:>10,.0f}/year
    $340/t (high-end academic):  ${total_annual_save_t * 340:>10,.0f}/year
    """)

    # --- Summary ---
    banner("Pipeline Summary")
    print(f"""
  Wall time            : {elapsed:.1f}s  (DCCT-NSGA-III + 14 routes)
  Pareto solutions     : {result.n_pareto_solutions}
  MILP cost change     : {result.milp_cost_change_pct:+.1f}%
  MILP emission change : {result.milp_emission_pct:+.1f}%
  Dynamic CI saving    : {result.dynamic_ci_saving_kg:.0f} kg CO2e/run
  Annual CI saving     : {result.dynamic_ci_saving_kg * 52 / 1000:.1f} t CO2e/year
    """)

    # --- Save results ---
    out_dir = os.path.join(
        os.path.dirname(__file__), "..", "data", "processed", "optimization_results"
    )
    os.makedirs(out_dir, exist_ok=True)

    summary = {
        "case_study":                "LA National Distribution Hub — USA",
        "origin":                    "Los Angeles, CA",
        "n_routes":                  len(US_NETWORK),
        "pipeline_wall_time_s":      round(elapsed, 1),
        "milp_cost_change_pct":      round(result.milp_cost_change_pct, 2),
        "milp_emission_change_pct":  round(result.milp_emission_pct, 2),
        "pareto_solutions":          result.n_pareto_solutions,
        "dynamic_ci_saving_kg":      round(result.dynamic_ci_saving_kg, 1),
        "annual_total_saving_t":     round(total_annual_save_t, 1),
        "egrid_regions":             {k: v[1] for k, v in EGRID_REGIONS.items()},
        "data_sources": {
            "distances":  "OpenStreetMap / BTS Freight Atlas 2022",
            "costs":      "BTS Commodity Flow Survey 2022 (USD/ton-km)",
            "emissions":  "EPA Supply Chain GHG Emission Factors v1.3",
            "grid_ci":    "EPA eGRID 2022 national + CA/TX regional profiles",
        },
    }

    out_path = os.path.join(out_dir, "usa_case_study_summary.json")
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"  Results -> {out_path}")
    banner("USA CASE STUDY COMPLETE")


if __name__ == "__main__":
    main()
