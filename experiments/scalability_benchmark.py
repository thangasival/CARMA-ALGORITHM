"""
DCCT Scalability and Ablation Benchmark
=========================================
Runs a systematic comparison of 5 optimizer variants across 5 instance sizes
and a budget-tightness sweep to address three specific reviewer concerns:

1. Analytical novelty: Ablation isolates CAPS and SPRD channels independently,
   proving DCCT's benefit is not just warm-starting (CAPS-only) or just
   reference-dir augmentation (SPRD-only).

2. Scalability: 5 instance sizes (12 → 250 routes) with runtime curves and
   Pareto quality metrics (HV, IGD, Spread) per size.

3. Benchmarking: MOEA/D (Zhang & Li 2007) as external decomposition baseline,
   alongside NSGA-III ablation variants.

Optimizer variants compared
----------------------------
  V1  MOEA/D            — decomposition baseline (Zhang & Li 2007)
  V2  NSGA3-Random      — NSGA-III, random init, no SPRD  (no DCCT)
  V3  NSGA3-CAPS        — NSGA-III + Channel 1 only       (CAPS alone)
  V4  NSGA3-SPRD        — NSGA-III + Channel 2 only       (SPRD alone)
  V5  NSGA3-DCCT        — NSGA-III + both channels        (full DCCT, proposed)

Instance sizes
--------------
  n ∈ {12, 25, 50, 100, 250} routes
  Each instance generated from a fixed seed for reproducibility.

Budget tightness sweep
----------------------
  Fixed n=12; reduction% ∈ {10, 20, 30, 40} relative to baseline emissions.
  Shows how DCCT advantage (λ*-driven SPRD) strengthens with tighter budgets.

Output
------
  Printed tables + CSV files in experiments/results/
  - scalability_results.csv    — HV/IGD/Spread/time per variant×size
  - budget_sweep_results.csv   — HV/time per variant×tightness
  - summary_table.csv          — publication-ready comparison table

Usage
-----
  python experiments/scalability_benchmark.py
  python experiments/scalability_benchmark.py --quick   # n=80 generations
  python experiments/scalability_benchmark.py --sizes 12,25,50  # subset
"""
from __future__ import annotations

import argparse
import logging
import os
import random
import sys
import time
import warnings
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=RuntimeWarning)
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

from algorithm.optimization.nsga3_optimizer import NSGA3Optimizer, Route
from algorithm.optimization.moeaD_optimizer import MOEADOptimizer
from algorithm.optimization.carbon_milp import CarbonBudgetMILP, MILPRoute
from algorithm.utils.pareto_metrics import (
    compute_all_metrics,
    build_reference_front,
    pareto_fitnesses,
    igd as igd_fn,
)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Instance generation
# ---------------------------------------------------------------------------

def generate_routes(n: int, seed: int = 42) -> List[Route]:
    """
    Generate n synthetic Route objects for NSGA-III / MOEA-D.

    Uses a fixed seed so all variants see the same instance.
    Distances are drawn to ensure all 4 modes are feasible for at least
    some routes (rail ≥ 200 km, ship ≥ 500 km, air ≥ 1000 km).
    """
    rng = np.random.default_rng(seed)
    cities = [
        "Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao",
        "Zaragoza", "Málaga", "Murcia", "Valladolid", "Vigo",
        "Lisbon", "Porto", "Lyon", "Marseille", "Bordeaux",
        "Hamburg", "Frankfurt", "Amsterdam", "Brussels", "Paris",
    ]
    commodities = ["electronics", "food", "machinery", "textiles", "chemicals", "raw_materials"]
    weather     = ["clear", "rain", "fog", "snow"]

    routes = []
    for i in range(n):
        dist     = float(rng.uniform(100, 2500))
        weight   = float(rng.uniform(1, 60))
        temp     = float(rng.uniform(-5, 35))
        cong     = float(rng.uniform(0.9, 2.2))
        slope    = float(rng.uniform(0, 12))
        is_up    = bool(rng.integers(0, 2))
        is_peak  = bool(rng.integers(0, 2))
        is_wknd  = bool(rng.integers(0, 2))
        orig     = cities[int(rng.integers(0, len(cities)))]
        dest_idx = int(rng.integers(0, len(cities)))
        while cities[dest_idx] == orig:
            dest_idx = int(rng.integers(0, len(cities)))

        # Assign a realistic mode
        if dist < 200:
            mode = "truck"
        elif dist < 500:
            mode = rng.choice(["truck", "rail"])
        elif dist < 1200:
            mode = rng.choice(["truck", "rail", "ship"])
        else:
            mode = rng.choice(["rail", "ship"])

        r = Route(
            origin=orig,
            destination=cities[dest_idx],
            distance_km=round(dist, 1),
            weight_tons=round(weight, 1),
            commodity_type=str(commodities[int(rng.integers(0, len(commodities)))]),
            transport_mode=str(mode),
            temperature_c=round(temp, 1),
            congestion_factor=round(cong, 2),
            slope_degrees=round(slope, 1),
            is_uphill=is_up,
            is_peak_hour=is_peak,
            is_weekend=is_wknd,
            weather_condition=str(weather[int(rng.integers(0, len(weather)))]),
        )
        # Attach route_id used by MILP
        r.route_id = f"R{i+1:04d}"
        routes.append(r)
    return routes


def compute_baseline_emissions(routes: List[Route]) -> float:
    """Flat-EF baseline total emissions (kg CO2e) before mode optimisation."""
    ef = {"truck": 0.161, "rail": 0.041, "ship": 0.015, "air": 0.602}
    return sum(r.distance_km * r.weight_tons * ef.get(r.transport_mode, 0.161) for r in routes)


def run_milp(routes: List[Route], budget_fraction: float = 0.80) -> Tuple[Dict, float, float]:
    """
    Run MILP phase to get X*_MILP, λ*, and the carbon budget B.

    Returns (milp_assignments, shadow_price, budget_kg)
    """
    try:
        milp = CarbonBudgetMILP()
        baseline_em = compute_baseline_emissions(routes)
        budget = baseline_em * budget_fraction

        milp_routes = [
            MILPRoute(
                route_id=getattr(r, "route_id", f"R{i:04d}"),
                origin=r.origin,
                destination=r.destination,
                distance_km=r.distance_km,
                weight_tons=r.weight_tons,
                commodity_type=r.commodity_type,
                current_mode=r.transport_mode,
            )
            for i, r in enumerate(routes)
        ]

        result = milp.optimise(milp_routes, carbon_budget_kg=budget)
        assignments = result.mode_assignments or {}
        shadow = result.shadow_price_eur_per_kg or 0.065
        return assignments, float(shadow), float(budget)

    except Exception as exc:
        logger.warning(f"MILP failed ({exc}); using empty assignments, ETS shadow price")
        return {}, 0.065, compute_baseline_emissions(routes) * budget_fraction


# ---------------------------------------------------------------------------
# Single variant run
# ---------------------------------------------------------------------------

@dataclass
class RunResult:
    variant:       str
    n_routes:      int
    budget_pct:    float   # budget as % of baseline (e.g. 0.80 = 20% reduction)
    time_s:        float
    n_pareto:      int
    hv:            float
    igd:           float   # relative to shared reference front
    spread:        float
    speedup_vs_random: float = 1.0
    shadow_price:  float = 0.0


def run_variant(
    name: str,
    routes: List[Route],
    milp_assignments: Dict,
    shadow_price: float,
    n_gen: int,
    ref_front: Optional[np.ndarray] = None,
    ref_point: Optional[np.ndarray] = None,
    budget_fraction: float = 0.80,
) -> Tuple[RunResult, np.ndarray]:
    """
    Run one optimizer variant and return (RunResult, pareto_fitness_matrix).
    """
    n = len(routes)

    # Build optimizer
    if name == "MOEA/D":
        opt = MOEADOptimizer(population_size=84, n_partitions=6, n_neighbors=10)
        result = opt.optimize_routes(routes, n_generations=n_gen)
        # Extract fitness matrix from decoded solutions
        pf_fits = _decode_to_matrix(result["pareto_front"])

    else:
        use_caps = "CAPS" in name or "DCCT" in name
        use_sprd = "SPRD" in name or "DCCT" in name
        sp       = shadow_price if use_sprd else 0.0
        ma       = milp_assignments if use_caps else None

        opt = NSGA3Optimizer(
            population_size=84,
            n_partitions=6,
            shadow_price=sp,
            use_caps=use_caps,
            use_sprd=use_sprd,
        )
        result = opt.optimize_routes(routes, n_generations=n_gen,
                                     milp_assignments=ma, shadow_price=sp)
        # Extract from DEAP individuals
        pf_fits = pareto_fitnesses(opt.pareto_front)

    elapsed  = result["optimization_time"]
    n_pareto = len(result["pareto_front"])

    # Compute Pareto quality metrics
    metrics = compute_all_metrics(
        pareto_approx=pf_fits,
        reference_front=ref_front,
        ref_point=ref_point,
        hv_samples=100_000,
    )

    run = RunResult(
        variant=name, n_routes=n, budget_pct=budget_fraction,
        time_s=elapsed, n_pareto=n_pareto,
        hv=metrics.get("hv", 0.0),
        igd=metrics.get("igd", np.inf),
        spread=metrics.get("spread", 0.0),
        shadow_price=shadow_price,
    )
    return run, pf_fits


def _decode_to_matrix(pareto_solutions: List[Dict]) -> np.ndarray:
    """Convert decoded solution dicts to (n,4) fitness matrix."""
    if not pareto_solutions:
        return np.empty((0, 4))
    return np.array([
        [s["total_cost"], s["total_emissions_kg"],
         s["total_time_hours"], s["avg_unreliability"]]
        for s in pareto_solutions
    ])


# ---------------------------------------------------------------------------
# Main benchmark loops
# ---------------------------------------------------------------------------

VARIANT_NAMES = ["MOEA/D", "NSGA3-Random", "NSGA3-CAPS", "NSGA3-SPRD", "NSGA3-DCCT"]


def run_scalability_experiment(
    sizes: List[int],
    n_gen: int = 80,
    budget_fraction: float = 0.80,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Run all 5 variants on each instance size.

    For each size: first build a shared reference front (pool of all variant
    fronts), then recompute IGD for each variant against that shared reference.
    """
    all_rows = []

    for n in sizes:
        logger.info(f"\n{'='*60}")
        logger.info(f"  Instance: n={n} routes  gen={n_gen}  budget={1-budget_fraction:.0%} reduction")
        logger.info(f"{'='*60}")

        routes = generate_routes(n, seed=seed)
        milp_assignments, shadow_price, _budget = run_milp(routes, budget_fraction)

        # Pass 1: collect all Pareto fronts without IGD (ref front not yet known)
        fronts: Dict[str, np.ndarray] = {}
        times:  Dict[str, float] = {}
        n_pars: Dict[str, int] = {}
        hvs:    Dict[str, float] = {}
        sprds:  Dict[str, float] = {}

        for variant in VARIANT_NAMES:
            logger.info(f"  Running {variant}...")
            run, pf_fits = run_variant(
                variant, routes, milp_assignments, shadow_price,
                n_gen=n_gen, budget_fraction=budget_fraction,
            )
            fronts[variant] = pf_fits
            times[variant]  = run.time_s
            n_pars[variant] = run.n_pareto
            hvs[variant]    = run.hv
            sprds[variant]  = run.spread

        # Build shared reference front from all variants
        ref_front = build_reference_front(list(fronts.values()))
        ref_point = ref_front.max(axis=0) * 1.1 if len(ref_front) > 0 else None

        # Pass 2: compute IGD against shared reference
        random_time = times.get("NSGA3-Random", 1.0)

        for variant in VARIANT_NAMES:
            pf = fronts[variant]
            igd_val = igd_fn(pf, ref_front) if len(pf) > 0 and len(ref_front) > 0 else np.inf
            speedup = random_time / times[variant] if times[variant] > 0 else 1.0

            all_rows.append({
                "n_routes":    n,
                "variant":     variant,
                "budget_pct":  budget_fraction,
                "time_s":      round(times[variant], 2),
                "n_pareto":    n_pars[variant],
                "hv":          round(hvs[variant], 4),
                "igd":         round(igd_val, 6),
                "spread":      round(sprds[variant], 4),
                "speedup":     round(speedup, 2),
                "shadow_price": round(shadow_price, 4),
            })
            logger.info(
                f"  {variant:<16} time={times[variant]:.1f}s  "
                f"PF={n_pars[variant]:>3}  HV={hvs[variant]:.4f}  "
                f"IGD={igd_val:.4f}  Δ={sprds[variant]:.3f}  "
                f"speedup={speedup:.2f}×"
            )

    return pd.DataFrame(all_rows)


def run_budget_sweep(
    n_routes: int = 12,
    budget_fractions: Optional[List[float]] = None,
    n_gen: int = 80,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Run all 5 variants with varying carbon budget tightness.

    Budget fraction = remaining emissions allowed / baseline.
    0.90 = 10% reduction required, 0.60 = 40% reduction required.
    Tighter budget → higher λ* → SPRD concentrates more dirs → DCCT more effective.
    """
    if budget_fractions is None:
        budget_fractions = [0.90, 0.80, 0.70, 0.60]

    routes = generate_routes(n_routes, seed=seed)
    all_rows = []

    for bf in budget_fractions:
        pct_label = f"{(1-bf)*100:.0f}% reduction"
        logger.info(f"\n--- Budget sweep: {pct_label} (fraction={bf}) ---")

        milp_assignments, shadow_price, _budget = run_milp(routes, bf)
        logger.info(f"    λ* = {shadow_price:.4f} €/kg CO₂e")

        fronts: Dict[str, np.ndarray] = {}
        times:  Dict[str, float] = {}
        hvs:    Dict[str, float] = {}

        for variant in VARIANT_NAMES:
            run, pf_fits = run_variant(
                variant, routes, milp_assignments, shadow_price,
                n_gen=n_gen, budget_fraction=bf,
            )
            fronts[variant] = pf_fits
            times[variant]  = run.time_s
            hvs[variant]    = run.hv

        ref_front = build_reference_front(list(fronts.values()))
        random_time = times.get("NSGA3-Random", 1.0)

        for variant in VARIANT_NAMES:
            pf  = fronts[variant]
            igd_val = igd_fn(pf, ref_front) if len(pf) > 0 and len(ref_front) > 0 else np.inf
            speedup = random_time / times[variant] if times[variant] > 0 else 1.0

            all_rows.append({
                "n_routes":    n_routes,
                "budget_pct":  bf,
                "reduction_pct": round((1 - bf) * 100, 0),
                "variant":     variant,
                "time_s":      round(times[variant], 2),
                "hv":          round(hvs[variant], 4),
                "igd":         round(igd_val, 6),
                "speedup":     round(speedup, 2),
                "shadow_price": round(shadow_price, 4),
            })
            logger.info(
                f"  {variant:<16} λ*={shadow_price:.3f}  time={times[variant]:.1f}s  "
                f"HV={hvs[variant]:.4f}  speedup={speedup:.2f}×"
            )

    return pd.DataFrame(all_rows)


# ---------------------------------------------------------------------------
# Summary tables
# ---------------------------------------------------------------------------

def print_scalability_table(df: pd.DataFrame):
    """Print publication-ready scalability table."""
    print("\n" + "="*90)
    print("SCALABILITY RESULTS — HV / IGD / Spread / Runtime (seconds)")
    print("="*90)

    pivot_hv   = df.pivot(index="n_routes", columns="variant", values="hv")
    pivot_time = df.pivot(index="n_routes", columns="variant", values="time_s")
    pivot_spd  = df.pivot(index="n_routes", columns="variant", values="speedup")

    print("\nHypervolume (higher is better):")
    print(pivot_hv.to_string(float_format="{:.4f}".format))

    print("\nRuntime (seconds):")
    print(pivot_time.to_string(float_format="{:.1f}".format))

    print("\nSpeedup vs NSGA3-Random:")
    print(pivot_spd.to_string(float_format="{:.2f}".format))


def print_budget_table(df: pd.DataFrame):
    """Print budget-tightness sweep table."""
    print("\n" + "="*90)
    print("BUDGET TIGHTNESS SWEEP -- Effect of lambda* on DCCT advantage")
    print("="*90)

    for variant in VARIANT_NAMES:
        sub = df[df["variant"] == variant][
            ["reduction_pct", "shadow_price", "hv", "time_s", "speedup"]
        ].set_index("reduction_pct")
        print(f"\n  {variant}:")
        print(sub.to_string())


def make_summary_table(df_scale: pd.DataFrame) -> pd.DataFrame:
    """
    Build one publication-ready comparison table at the reference instance size.
    Uses the largest available instance.
    """
    n_max = df_scale["n_routes"].max()
    sub = df_scale[df_scale["n_routes"] == n_max].copy()

    # Rank by HV (higher better) then by time (lower better)
    sub["hv_rank"]   = sub["hv"].rank(ascending=False).astype(int)
    sub["time_rank"] = sub["time_s"].rank(ascending=True).astype(int)

    cols = ["variant", "n_pareto", "hv", "igd", "spread", "time_s", "speedup"]
    return sub[cols].sort_values("hv", ascending=False).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="DCCT scalability and ablation benchmark")
    parser.add_argument("--quick",   action="store_true",
                        help="Use 40 generations for a fast sanity-check run")
    parser.add_argument("--sizes",   type=str, default="12,25,50,100,250",
                        help="Comma-separated list of instance sizes")
    parser.add_argument("--budget",  type=float, default=0.80,
                        help="Carbon budget fraction for scalability run (0.80 = 20% reduction)")
    parser.add_argument("--seed",    type=int, default=42)
    args = parser.parse_args()

    np.random.seed(args.seed)
    random.seed(args.seed)

    n_gen  = 40 if args.quick else 80
    sizes  = [int(s) for s in args.sizes.split(",")]
    budget = args.budget

    logger.info(f"DCCT Benchmark: sizes={sizes}  gen={n_gen}  budget={budget}")

    # ── Scalability experiment ──────────────────────────────────────────────
    logger.info("\n[1/2] Scalability experiment")
    df_scale = run_scalability_experiment(
        sizes=sizes, n_gen=n_gen, budget_fraction=budget, seed=args.seed
    )
    scale_path = os.path.join(RESULTS_DIR, "scalability_results.csv")
    df_scale.to_csv(scale_path, index=False)
    logger.info(f"Saved: {scale_path}")
    print_scalability_table(df_scale)

    # ── Budget tightness sweep ──────────────────────────────────────────────
    logger.info("\n[2/2] Budget tightness sweep")
    df_budget = run_budget_sweep(
        n_routes=12, n_gen=n_gen, seed=args.seed
    )
    budget_path = os.path.join(RESULTS_DIR, "budget_sweep_results.csv")
    df_budget.to_csv(budget_path, index=False)
    logger.info(f"Saved: {budget_path}")
    print_budget_table(df_budget)

    # ── Summary table ───────────────────────────────────────────────────────
    summary = make_summary_table(df_scale)
    summary_path = os.path.join(RESULTS_DIR, "summary_table.csv")
    summary.to_csv(summary_path, index=False)

    print("\n" + "="*90)
    print("SUMMARY TABLE (largest instance)")
    print("="*90)
    print(summary.to_string(index=False))
    print(f"\nAll results written to: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
