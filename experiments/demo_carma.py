"""
CARMA End-to-End Demo
=====================
Demonstrates the full 6-phase CARMA pipeline on a synthetic Iberian
supply-chain network with 12 routes.

Author: Sivalingam Thangavel <th.sivalingam@gmail.com>
Project: CARMA-ALGORITHM v1.0.0

Run with:
    $env:PYTHONIOENCODING="utf-8"; python demo_carma.py
"""

import logging
import sys
import os
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s  %(message)s",
    stream=sys.stdout,
)

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# 1. Build a small synthetic route set
# ---------------------------------------------------------------------------

from algorithm.optimization.nsga3_optimizer import Route as NSGARoute

# (origin, destination, distance_km, weight_tons, mode, temp, cong, slope)
ROUTES = [
    ("Madrid",     "Barcelona",    420,  22.0, "truck",  15, 1.4, 2.0),
    ("Madrid",     "Valencia",     590,   8.0, "rail",   12, 1.1, 0.5),
    ("Bilbao",     "Barcelona",   1100,  35.0, "ship",   18, 1.0, 0.0),
    ("Madrid",     "Toledo",       280,   5.0, "truck",  20, 1.6, 3.5),
    ("Madrid",     "Sevilla",      850,  14.0, "rail",   10, 1.2, 1.0),
    ("Algeciras",  "Genova",      1800,  50.0, "ship",   22, 1.0, 0.0),
    ("Zaragoza",   "Barcelona",    320,   9.0, "truck",  14, 1.8, 4.0),
    ("Barcelona",  "Madrid",       670,  18.0, "truck",  16, 1.3, 1.5),
    ("Valencia",   "Hamburg",     2200,  60.0, "ship",   20, 1.0, 0.0),
    ("Bilbao",     "Madrid",       390,  12.0, "rail",   11, 1.2, 2.0),
    ("Salamanca",  "Barcelona",    510,   7.0, "truck",  17, 1.5, 1.0),
    ("Madrid",     "Guadalajara",  160,   4.0, "truck",  22, 2.1, 0.5),
]

# Give each route a stable id used only in the dynamic-CI section
ROUTE_IDS = [f"R{i+1:03d}" for i in range(len(ROUTES))]


def make_nsga_routes():
    routes = []
    for (orig, dest, dist, weight, mode, temp, cong, slope) in ROUTES:
        r = NSGARoute(
            origin=orig,
            destination=dest,
            distance_km=float(dist),
            weight_tons=float(weight),
            commodity_type="general",
            transport_mode=mode,
            temperature_c=float(temp),
            congestion_factor=float(cong),
            slope_degrees=float(slope),
            weather_condition="clear",
            is_weekend=False,
        )
        routes.append(r)
    return routes


# ---------------------------------------------------------------------------
# 2. Build a small training DataFrame (30 rows minimum for ensemble)
# ---------------------------------------------------------------------------

def make_training_df():
    """
    Thin synthetic training dataset.
    SyntheticRouteGenerator normally builds 30 rows; we replicate
    the minimal schema needed by EmissionPredictionModels.prepare_features().
    """
    np.random.seed(42)
    n = 80
    modes = ["truck"] * 40 + ["rail"] * 20 + ["ship"] * 15 + ["air"] * 5
    np.random.shuffle(modes)

    ef_map = {"truck": 0.062, "rail": 0.028, "ship": 0.008, "air": 0.600}

    rows = []
    for i in range(n):
        mode  = modes[i]
        dist  = np.random.uniform(100, 2500)
        wt    = np.random.uniform(1, 60)
        ef    = ef_map[mode]
        em    = dist * wt * ef * np.random.uniform(0.85, 1.15)
        speed = {"truck": 75, "rail": 120, "ship": 25, "air": 800}[mode]
        cong = round(np.random.uniform(1.0, 2.2), 2)
        temp_c = round(np.random.uniform(-5, 35), 1)
        slope  = round(np.random.uniform(0.0, 5.0), 2)
        load_f = round(np.random.uniform(0.3, 1.0), 2)
        spd    = round(speed * np.random.uniform(0.7, 1.1), 1)
        rows.append({
            "route_id":           f"TR{i:04d}",
            "transport_mode":     mode,
            "distance_km":        round(dist, 1),
            "weight_tons":        round(wt, 2),
            "total_emission_kg":              round(em, 2),
            "adjusted_emissions_kg_co2e":     round(em, 2),
            "fuel_cost_eur":      round(dist * {"truck":1.5,"rail":0.8,"ship":0.3,"air":12}[mode], 1),
            "transit_time_hours": round(dist / speed, 2),
            "cargo_type":         "general",
            "commodity_type":     "general",
            "is_hazardous":       False,
            "is_weekend":         bool(np.random.rand() > 0.8),
            "is_peak_hour":       bool(np.random.rand() > 0.7),
            "temperature_c":      temp_c,
            "congestion_factor":  cong,
            "slope_degrees":      slope,
            "is_uphill":          bool(np.random.rand() > 0.5),
            "weather_condition":  np.random.choice(["clear","rain","snow"], p=[0.7,0.2,0.1]),
            "load_factor":        load_f,
            "speed_kmh":          spd,
            "actual_speed_kmh":   spd,
            "optimal_speed_kmh":  speed,
            "speed_ratio":        round(spd / speed, 3),
            "payload_efficiency": load_f,
            "distance_category":  ("short" if dist < 300 else "medium" if dist < 800 else "long"),
            "env_efficiency_simple":  round(em / (dist * wt + 1e-6), 6),
            "physics_emission_simple": round(em * 0.95, 2),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 3. Run CARMA
# ---------------------------------------------------------------------------

def main():
    print("\n" + "="*68)
    print("  CARMA — Carbon-Aware Routing with Multi-objective Adaptive ensemble")
    print("  End-to-End Demo  |  12 routes  |  Iberian supply-chain network")
    print("="*68 + "\n")

    routes      = make_nsga_routes()
    training_df = make_training_df()

    print(f"  Routes       : {len(routes)}")
    print(f"  Training rows: {len(training_df)}")
    print(f"  Modes in data: {training_df['transport_mode'].value_counts().to_dict()}")
    print()

    from algorithm.carma import CARMA, CARMAConfig

    config = CARMAConfig(
        # Phase 1 — Physics
        grid_ci_g_kwh=255.0,
        # Phase 2 — Ensemble
        ensemble_strategy="segmented",
        ml_test_size=0.20,
        # Phase 3 — MILP  (20% carbon budget reduction)
        carbon_budget_reduction_pct=20.0,
        ets_price_eur_per_tonne=65.0,    # EUR ETS ~ EUR 65/tonne
        # Phase 4 — NSGA-III
        nsga3_population=84,
        nsga3_generations=80,
        nsga3_partitions=6,
        # Phase 5 — Dynamic CI
        enable_dynamic_ci=True,
        origin_country="ES",
        time_flexibility_hours=8.0,
        # Phase 6 — Synthesis
        preference_weights={"cost": 0.40, "emissions": 0.40, "time": 0.10, "reliability": 0.10},
    )

    carma  = CARMA(config)
    result = carma.run(routes, training_df=training_df)

    # --- Main summary ---
    result.print_summary()

    # --- JSON export ---
    import json
    d = result.to_dict()
    print("\n  JSON summary (to_dict):")
    print(json.dumps(d, indent=4, default=str))

    # --- Dynamic schedule table ---
    if result.dynamic_schedules:
        print("\n  Dynamic CI departure schedule:")
        print(f"  {'Route':<8} {'Mode':<8} {'Elec?':<6} "
              f"{'Base dep':<10} {'Opt dep':<10} {'Saving kg':<12} {'Saving %'}")
        print("  " + "-"*68)
        for s in result.dynamic_schedules:
            elec = "yes" if s["is_electric"] else "no"
            print(f"  {s['route_id']:<8} {s['mode']:<8} {elec:<6} "
                  f"  {int(s['baseline_dep']):02d}:00     "
                  f"  {int(s['optimal_dep']):02d}:00     "
                  f"{s['saving_kg']:>10.1f}    {s['saving_pct']:>6.1f}%")

    # --- Pareto front (first 5) ---
    if result.pareto_front:
        print(f"\n  NSGA-III Pareto front (first 5 of {result.n_pareto_solutions}):")
        print(f"  {'cost (EUR)':>12}  {'em (kg)':>12}  {'time (h)':>10}  {'unrel':>8}")
        print("  " + "-"*48)
        for sol in result.pareto_front[:5]:
            print(f"  {sol['total_cost']:>12,.0f}  "
                  f"{sol['total_emissions_kg']:>12,.0f}  "
                  f"{sol['total_time_hours']:>10.1f}  "
                  f"{sol['avg_unreliability']:>8.3f}")

    print("\n  Demo complete.\n")
    return result


if __name__ == "__main__":
    main()
