"""
CARMA Algorithm — Unified Orchestrator
=======================================
Carbon-Aware Routing with Multi-objective Adaptive ensemble

Author: Sivalingam Thangavel <th.sivalingam@gmail.com>
Project: CARMA-ALGORITHM v1.0.0

This module is the single entry point for the CARMA framework.
It sequences all six components in the correct order and returns
a structured result object containing outputs from each phase.

Algorithm flow (6 phases)
--------------------------

  PHASE 1  Physics-Informed Emission Estimation (PIEM)
           Grubb payload efficiency + COPERT speed curve + HBEFA congestion
           + bidirectional slope (regen braking) + quadratic temperature

  PHASE 2  Adaptive ML Ensemble Calibration
           Train RF + XGBoost base learners on physics-enriched features
           Build Segmented Mixture-of-Experts with per-segment optimal weights
           Build Stacked meta-learner (Ridge on OOF predictions)

  PHASE 3  Carbon-Budget MILP (static, certified optimal)
           min  sum c[r,m] * x[r,m]
           s.t. sum e[r,m] * x[r,m] <= B_carbon
                sum_m x[r,m] = 1  for all r
           Extracts shadow price lambda* = internal carbon abatement cost

  PHASE 4  DCCT-NSGA-III: Dual-Channel Certificate Transfer (Type 6+8 novelty)
           Objectives: f1=cost  f2=ML-predicted-emission  f3=transit-time  f4=CRI
           Channel 1 (CAPS): X*_MILP seeds ⌊N/4⌋ of P₀  → G*(ε) = 0  (Theorem 2)
           Channel 2 (SPRD): λ* biases reference dirs toward f₂  → density ≥ (1+α)×baseline
           Result: Certificate-Anchored Pareto Front PF* (Theorem 1: X*_MILP ∈ PF* always)

  PHASE 5  Dynamic Carbon-Intensity Scheduling
           For electrified modes: find departure hour minimising grid-CI-weighted emission
           CI_avg(h) = integral of CI(t) over transit window [h, h + duration]
           Annual saving = sum of per-route optimal-vs-baseline emission delta x 52 weeks

  PHASE 6  Solution Synthesis
           Combine MILP certificate + NSGA-III Pareto front + dynamic schedule
           Preferred Pareto solution via Tchebycheff scalarisation
           Full comparison table vs baseline

Formal pseudocode (see CARMA_SPEC.md for LaTeX version)
---------------------------------------------------------
  INPUT:  Routes R, demand D, carbon budget B, preference weights w
  OUTPUT: X* (mode assignments), T* (departure schedule), Pareto front PF*,
          lambda* (shadow price), annual_saving (tonnes CO2e)

  1: for r in R, m in M do
  2:   E[r,m] <- PIEM(d_r, w_r, m, theta_r)           // Phase 1 — PIEM
  3: end for
  4: (RF, XGB, MoE) <- fit_ensemble(features(R), E_observed)  // Phase 2
  5: (X*_MILP, lambda*) <- solve_MILP(R, E, B)         // Phase 3 — DCCT source
  6: PF* <- DCCT_NSGA3(R, MoE_predict, X*_MILP, lambda*, ref_dirs, G_max)  // Phase 4
  7: T* <- argmin_h CI_avg(h, h+duration) for elec r   // Phase 5
  8: X*_pref <- Tchebycheff(PF*, w)                    // Phase 6
  9: return (X*_MILP, X*_pref, PF*, T*, lambda*)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class CARMAConfig:
    """
    All tunable parameters for the CARMA algorithm.

    Sensible defaults chosen from experimental validation on
    the Salamanca regional network (Section 4.6 of paper).
    """
    # --- Phase 1: PIEM ---
    grid_ci_g_kwh: float = 255.0
    """Grid carbon intensity for electric traction (g CO2/kWh). EU27 avg 2023."""

    # --- Phase 2: ML Ensemble ---
    ensemble_strategy: str = "segmented"
    """'segmented' | 'soft_moe' | 'stacked' — adaptive ensemble type."""
    ml_random_state: int = 42
    ml_test_size: float = 0.20
    ml_cv_folds: int = 5

    # --- Phase 3: MILP ---
    carbon_budget_reduction_pct: float = 20.0
    """Target emission reduction from baseline (%). Set 0 to disable budget."""
    ets_price_eur_per_tonne: float = 0.0
    """EU ETS carbon price (EUR/tonne CO2e). 0 = no carbon tax in objective."""

    # --- Phase 4: NSGA-III ---
    nsga3_population: int = 84
    """Population size. Recommended: equal to number of reference directions."""
    nsga3_generations: int = 100
    nsga3_partitions: int = 6
    """Simplex divisions p. p=6 -> 84 reference dirs for M=4 objectives."""
    nsga3_crossover_prob: float = 0.75
    nsga3_mutation_prob: float = 0.20

    # --- Phase 5: Dynamic CI ---
    enable_dynamic_ci: bool = True
    """Whether to run departure-time optimization for electrified routes."""
    origin_country: str = "ES"
    """ISO-2 country code for grid CI profile lookup."""
    time_flexibility_hours: float = 8.0
    """Max hours shipper can shift departure from planned time."""

    # --- Phase 6: Synthesis ---
    preference_weights: Dict[str, float] = field(default_factory=lambda: {
        "cost": 0.40, "emissions": 0.40, "time": 0.10, "reliability": 0.10
    })
    """Tchebycheff weights for preferred-solution selection from Pareto front."""

    @property
    def ets_price_eur_per_kg(self) -> float:
        return self.ets_price_eur_per_tonne / 1000.0


# ---------------------------------------------------------------------------
# Result container
# ---------------------------------------------------------------------------

@dataclass
class CARMAResult:
    """
    Full output of one CARMA run — one object per phase plus combined metrics.
    """
    config: CARMAConfig

    # Phase 1
    physics_features_sample: Optional[Dict] = None

    # Phase 2
    ensemble_mape: Optional[float] = None
    ensemble_r2:   Optional[float] = None
    ensemble_type: str = ""
    segment_weights: Optional[pd.DataFrame] = None

    # Phase 3
    milp_status:           str = ""
    milp_cost:             float = 0.0
    milp_emissions_kg:     float = 0.0
    milp_cost_change_pct:  float = 0.0
    milp_emission_pct:     float = 0.0
    milp_shadow_price:     Optional[float] = None
    milp_mode_shifts:      int = 0
    milp_solve_time_s:     float = 0.0
    milp_mode_assignments: Optional[Dict] = None   # route_id → mode (for CAPS)

    # Phase 4
    pareto_front:          List[Dict] = field(default_factory=list)
    nsga3_time_s:          float = 0.0
    n_pareto_solutions:    int = 0
    n_reference_dirs:      int = 0
    preferred_solution:    Optional[Dict] = None

    # Phase 5
    dynamic_ci_saving_kg:       float = 0.0
    dynamic_ci_saving_pct:      float = 0.0
    annual_ci_saving_tonnes:    float = 0.0
    dynamic_schedules:          List[Dict] = field(default_factory=list)

    # Overall
    baseline_cost:         float = 0.0
    baseline_emissions_kg: float = 0.0
    total_wall_time_s:     float = 0.0

    def print_summary(self):
        sep = "=" * 68
        print(f"\n{sep}")
        print("  CARMA — Carbon-Aware Routing with Multi-objective Adaptive ensemble")
        print(f"  Version 1.0.0  |  Wall time: {self.total_wall_time_s:.1f}s")
        print(sep)

        print("\n  [PHASE 1]  Physics-Informed Emission Model (PIEM)")
        print("             Grubb payload + COPERT speed + HBEFA congestion +")
        print("             bidirectional slope + quadratic temperature")

        print(f"\n  [PHASE 2]  Adaptive ML Ensemble  [{self.ensemble_type}]")
        if self.ensemble_mape is not None:
            print(f"             MAPE  = {self.ensemble_mape:.2f}%")
            print(f"             R2    = {self.ensemble_r2:.4f}")
        if self.segment_weights is not None:
            print("             Segment weights:")
            for _, row in self.segment_weights.iterrows():
                print(f"               {row['Segment']:<15}  "
                      f"w_RF={row['w_RF']:.2f}  w_XGB={row['w_XGB']:.2f}")

        print(f"\n  [PHASE 3]  Carbon-Budget MILP  (status: {self.milp_status})")
        print(f"             Solve time  : {self.milp_solve_time_s:.3f}s")
        print(f"             Budget      : {self.config.carbon_budget_reduction_pct:.0f}% reduction")
        print(f"             Optimal cost: EUR {self.milp_cost:>12,.2f}  "
              f"({self.milp_cost_change_pct:+.1f}%)")
        print(f"             Emissions   : {self.milp_emissions_kg:>12,.0f} kg CO2e  "
              f"({self.milp_emission_pct:+.1f}%)")
        if self.milp_shadow_price is not None:
            print(f"             Shadow price: EUR {self.milp_shadow_price*1000:.2f}/tonne CO2e"
                  "  (internal abatement cost)")
        print(f"             Mode shifts : {self.milp_mode_shifts} routes changed")

        print(f"\n  [PHASE 4]  NSGA-III 4-Objective  ({self.nsga3_time_s:.1f}s)")
        print(f"             Reference dirs  : {self.n_reference_dirs}")
        print(f"             Pareto solutions: {self.n_pareto_solutions}")
        if self.preferred_solution:
            ps = self.preferred_solution
            print(f"             Preferred solution (w={self.config.preference_weights}):")
            print(f"               cost={ps['total_cost']:,.0f} EUR  "
                  f"em={ps['total_emissions_kg']:,.0f} kg  "
                  f"time={ps['total_time_hours']:.1f}h  "
                  f"unrel={ps['avg_unreliability']:.3f}")

        print(f"\n  [PHASE 5]  Dynamic CI Scheduling")
        if self.config.enable_dynamic_ci:
            print(f"             Fleet CI saving : {self.dynamic_ci_saving_kg:,.1f} kg CO2e  "
                  f"({self.dynamic_ci_saving_pct:.1f}%)")
            print(f"             Annual saving   : {self.annual_ci_saving_tonnes:.2f} "
                  "metric tonnes CO2e/year")
        else:
            print("             (disabled in config)")

        print(f"\n  [PHASE 6]  Solution Synthesis")
        print(f"             Baseline cost  : EUR {self.baseline_cost:>12,.2f}")
        print(f"             Baseline emis  : {self.baseline_emissions_kg:>12,.0f} kg CO2e")
        print(f"\n  CARMA delivers certified MILP solution + {self.n_pareto_solutions}-point")
        print(f"  Pareto front + {self.annual_ci_saving_tonnes:.1f} t CO2e/yr dynamic scheduling gain")
        print(sep + "\n")

    def to_dict(self) -> Dict:
        return {
            "algorithm":          "CARMA v1.0.0",
            "ensemble_type":      self.ensemble_type,
            "ensemble_mape":      self.ensemble_mape,
            "ensemble_r2":        self.ensemble_r2,
            "milp_status":        self.milp_status,
            "milp_cost":          self.milp_cost,
            "milp_emissions_kg":  self.milp_emissions_kg,
            "milp_cost_change_pct": self.milp_cost_change_pct,
            "milp_emission_pct":  self.milp_emission_pct,
            "milp_shadow_price_eur_tonne": (
                self.milp_shadow_price * 1000 if self.milp_shadow_price else None),
            "milp_mode_shifts":   self.milp_mode_shifts,
            "pareto_front_size":  self.n_pareto_solutions,
            "n_reference_dirs":   self.n_reference_dirs,
            "dynamic_ci_saving_kg":    self.dynamic_ci_saving_kg,
            "annual_ci_saving_tonnes": self.annual_ci_saving_tonnes,
            "baseline_cost":           self.baseline_cost,
            "baseline_emissions_kg":   self.baseline_emissions_kg,
            "total_wall_time_s":       self.total_wall_time_s,
        }


# ---------------------------------------------------------------------------
# Main CARMA class
# ---------------------------------------------------------------------------

class CARMA:
    """
    CARMA — Carbon-Aware Routing with Multi-objective Adaptive ensemble

    Unified orchestrator that sequences all six algorithmic phases and
    returns a CARMAResult containing outputs from each phase.

    Parameters
    ----------
    config : CARMAConfig
        All tunable parameters. Defaults cover the Salamanca case study.

    Usage
    -----
    >>> carma  = CARMA(CARMAConfig(carbon_budget_reduction_pct=20))
    >>> result = carma.run(routes, training_df=df)
    >>> result.print_summary()
    >>> import json; print(json.dumps(result.to_dict(), indent=2))
    """

    def __init__(self, config: Optional[CARMAConfig] = None):
        self.config = config or CARMAConfig()
        self._phys_model    = None
        self._ensemble      = None
        self._ml_models     = None

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def run(
        self,
        routes: List[Any],
        training_df: Optional[pd.DataFrame] = None,
    ) -> CARMAResult:
        """
        Execute the full CARMA 6-phase pipeline.

        Parameters
        ----------
        routes      : list of Route objects (from hybrid_ml_ga or nsga3_optimizer)
        training_df : DataFrame from SyntheticRouteGenerator (used for Phase 2
                      ML training).  If None, Phase 2 is skipped and PIEM
                      is used directly inside GA fitness evaluation.

        Returns
        -------
        CARMAResult
        """
        result = CARMAResult(config=self.config)
        wall_start = time.perf_counter()

        logger.info("=" * 60)
        logger.info("CARMA — Starting 6-phase pipeline")
        logger.info("=" * 60)

        # ── Phase 1: PIEM ────────────────────────────────────────────
        logger.info("[Phase 1] Physics-Informed Emission Model (PIEM)")
        result = self._phase1_physics(routes, result)

        # ── Phase 2: Adaptive ML Ensemble ───────────────────────────
        logger.info("[Phase 2] Adaptive ML Ensemble calibration")
        result = self._phase2_ensemble(training_df, result)

        # ── Phase 3: MILP ────────────────────────────────────────────
        logger.info("[Phase 3] Carbon-Budget MILP")
        result = self._phase3_milp(routes, result)

        # ── Phase 4: NSGA-III ────────────────────────────────────────
        logger.info("[Phase 4] NSGA-III 4-Objective")
        result = self._phase4_nsga3(routes, result)

        # ── Phase 5: Dynamic CI ──────────────────────────────────────
        logger.info("[Phase 5] Dynamic Carbon-Intensity Scheduling")
        result = self._phase5_dynamic_ci(routes, result)

        # ── Phase 6: Synthesis ───────────────────────────────────────
        logger.info("[Phase 6] Solution Synthesis")
        result = self._phase6_synthesis(routes, result)

        result.total_wall_time_s = round(time.perf_counter() - wall_start, 2)
        logger.info(f"CARMA complete — {result.total_wall_time_s}s")
        return result

    # ------------------------------------------------------------------
    # Phase 1 — PIEM
    # ------------------------------------------------------------------

    def _phase1_physics(self, routes: List[Any], result: CARMAResult) -> CARMAResult:
        try:
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
            from algorithm.physics.emission_model import EmissionModelV2, RouteEmissionInput

            self._phys_model = EmissionModelV2(
                grid_carbon_intensity_g_kwh=self.config.grid_ci_g_kwh
            )

            # Sample features from first route for diagnostics
            if routes:
                r = routes[0]
                inp = RouteEmissionInput(
                    distance_km=r.distance_km,
                    weight_tons=r.weight_tons,
                    transport_mode=r.transport_mode,
                    temperature_c=getattr(r, "temperature_c", 20.0),
                    congestion_factor=getattr(r, "congestion_factor", 1.0),
                    slope_degrees=getattr(r, "slope_degrees", 0.0),
                )
                result.physics_features_sample = self._phys_model.get_physics_features(inp)
            logger.info(f"  PIEM ready — {len(result.physics_features_sample or {})} features")
        except Exception as exc:
            logger.warning(f"  PIEM init failed ({exc})")
        return result

    # ------------------------------------------------------------------
    # Phase 2 — Adaptive Ensemble
    # ------------------------------------------------------------------

    def _phase2_ensemble(
        self,
        training_df: Optional[pd.DataFrame],
        result: CARMAResult,
    ) -> CARMAResult:
        if training_df is None or len(training_df) < 50:
            logger.info("  No training data — PIEM used as emission oracle in GA")
            result.ensemble_type = "piem_oracle"
            return result

        try:
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_absolute_percentage_error, r2_score
            from algorithm.ml_models.emission_predictors import EmissionPredictionModels
            from algorithm.ml_models.adaptive_ensemble import build_adaptive_ensemble

            epm = EmissionPredictionModels(random_state=self.config.ml_random_state)
            X, y = epm.prepare_features(training_df)
            X_tr, X_te, y_tr, y_te = train_test_split(
                X, y,
                test_size=self.config.ml_test_size,
                random_state=self.config.ml_random_state,
            )
            df_tr = training_df.iloc[:len(X_tr)].reset_index(drop=True)
            df_te = training_df.iloc[len(X_tr):].reset_index(drop=True)

            # Train base learners
            epm.models["random_forest"].fit(X_tr, y_tr)
            epm.models["xgboost"].fit(X_tr, y_tr)
            base_models = {
                "random_forest": epm.models["random_forest"],
                "xgboost":       epm.models["xgboost"],
            }

            # Build adaptive ensemble
            ens = build_adaptive_ensemble(
                base_models, X_tr, y_tr, df_tr,
                strategy=self.config.ensemble_strategy,
            )
            self._ensemble = ens
            self._ml_models = epm
            epm._ensemble_adaptive = ens

            # Evaluate on test set
            if hasattr(ens, "predict"):
                pred = ens.predict(X_te, df_te)
                result.ensemble_mape = round(
                    mean_absolute_percentage_error(y_te, pred) * 100, 4)
                result.ensemble_r2   = round(r2_score(y_te, pred), 6)
            result.ensemble_type = self.config.ensemble_strategy

            # Capture segment weights if available
            if hasattr(ens, "weights_table"):
                result.segment_weights = ens.weights_table()

            logger.info(f"  {self.config.ensemble_strategy} ensemble — "
                        f"MAPE={result.ensemble_mape:.2f}%  R2={result.ensemble_r2:.4f}")
        except Exception as exc:
            logger.warning(f"  Phase 2 failed ({exc}); fallback to PIEM")
            result.ensemble_type = "piem_fallback"
        return result

    # ------------------------------------------------------------------
    # Phase 3 — MILP
    # ------------------------------------------------------------------

    def _phase3_milp(self, routes: List[Any], result: CARMAResult) -> CARMAResult:
        try:
            from algorithm.optimization.carbon_milp import (
                CarbonBudgetMILP, routes_to_milp
            )
            milp_routes = routes_to_milp(routes)
            solver = CarbonBudgetMILP(
                emission_model=self._phys_model,
                ets_price_eur_per_kg=self.config.ets_price_eur_per_kg,
            )
            res = solver.optimise(
                milp_routes,
                budget_reduction_pct=self.config.carbon_budget_reduction_pct,
            )
            result.milp_status          = res.status
            result.milp_cost            = res.total_cost
            result.milp_emissions_kg    = res.total_emissions_kg
            result.milp_cost_change_pct = res.cost_change_pct
            result.milp_emission_pct    = res.emission_change_pct
            result.milp_shadow_price    = res.shadow_price_eur_per_kg
            result.milp_mode_shifts     = len(res.mode_shifts)
            result.milp_solve_time_s    = res.solve_time_s
            result.milp_mode_assignments = res.mode_assignments   # for CAPS
            result.baseline_cost        = res.baseline_cost
            result.baseline_emissions_kg = res.baseline_emissions
            logger.info(f"  MILP {res.status} — cost {res.cost_change_pct:+.1f}%  "
                        f"em {res.emission_change_pct:+.1f}%  "
                        f"({res.solve_time_s:.3f}s)")
        except Exception as exc:
            logger.warning(f"  Phase 3 MILP failed ({exc})")
            result.milp_status = f"Error: {exc}"
        return result

    # ------------------------------------------------------------------
    # Phase 4 — NSGA-III
    # ------------------------------------------------------------------

    def _phase4_nsga3(self, routes: List[Any], result: CARMAResult) -> CARMAResult:
        try:
            from algorithm.optimization.nsga3_optimizer import NSGA3Optimizer

            # SPRD: prefer MILP dual variable λ*; fall back to ETS price when
            # CBC returns null (MIP dual variables require LP relaxation solve)
            shadow_price = (
                result.milp_shadow_price          # exact λ* when available
                or self.config.ets_price_eur_per_kg   # ETS price as proxy
                or 0.0
            )

            optimizer = NSGA3Optimizer(
                ml_predictor=self._ml_models,
                population_size=self.config.nsga3_population,
                n_partitions=self.config.nsga3_partitions,
                shadow_price=shadow_price,
            )
            optimizer.crossover_prob = self.config.nsga3_crossover_prob
            optimizer.mutation_prob  = self.config.nsga3_mutation_prob

            # CAPS: pass MILP mode assignments to seed the initial population
            res = optimizer.optimize_routes(
                routes,
                n_generations=self.config.nsga3_generations,
                milp_assignments=result.milp_mode_assignments,
                shadow_price=shadow_price,
            )
            result.pareto_front       = res["pareto_front"]
            result.nsga3_time_s       = res["optimization_time"]
            result.n_pareto_solutions = len(res["pareto_front"])
            result.n_reference_dirs   = res["n_reference_dirs"]

            w = self.config.preference_weights
            result.preferred_solution = optimizer.get_preferred_solution(
                weight_cost=w.get("cost", 0.4),
                weight_em=w.get("emissions", 0.4),
                weight_time=w.get("time", 0.1),
                weight_rel=w.get("reliability", 0.1),
            )
            logger.info(f"  NSGA-III done — {result.n_pareto_solutions} Pareto solutions  "
                        f"({result.nsga3_time_s:.1f}s)")
        except Exception as exc:
            logger.warning(f"  Phase 4 NSGA-III failed ({exc})")
        return result

    # ------------------------------------------------------------------
    # Phase 5 — Dynamic CI Scheduling
    # ------------------------------------------------------------------

    def _phase5_dynamic_ci(self, routes: List[Any], result: CARMAResult) -> CARMAResult:
        if not self.config.enable_dynamic_ci:
            return result
        try:
            from algorithm.optimization.dynamic_carbon_routing import (
                DynamicCarbonRouter, DynamicRouteInput
            )
            router = DynamicCarbonRouter()
            di_routes = []
            for i, r in enumerate(routes):
                di_routes.append(DynamicRouteInput(
                    route_id            = getattr(r, "route_id", f"R{i:04d}"),
                    distance_km         = r.distance_km,
                    weight_tons         = r.weight_tons,
                    transport_mode      = r.transport_mode,
                    origin_country      = self.config.origin_country,
                    destination_country = self.config.origin_country,
                    time_flexibility_h  = self.config.time_flexibility_hours,
                    baseline_departure_h = 8,
                ))
            schedules = router.optimise_schedule(di_routes)
            summary   = router.fleet_summary(schedules)

            result.dynamic_ci_saving_kg    = summary.get("total_saving_kg", 0.0)
            result.dynamic_ci_saving_pct   = summary.get("total_saving_pct", 0.0)
            result.annual_ci_saving_tonnes = summary.get("annual_saving_tons_co2e", 0.0)
            result.dynamic_schedules = [
                {
                    "route_id":          s.route_id,
                    "mode":              s.transport_mode,
                    "is_electric":       s.is_electric,
                    "baseline_dep":      s.baseline_departure_h,
                    "optimal_dep":       s.optimal_departure_h,
                    "saving_kg":         s.emission_saving_kg,
                    "saving_pct":        s.emission_saving_pct,
                }
                for s in schedules
            ]
            logger.info(f"  Dynamic CI — saving {result.dynamic_ci_saving_kg:.1f} kg  "
                        f"({result.dynamic_ci_saving_pct:.1f}%)  "
                        f"annual={result.annual_ci_saving_tonnes:.2f} t CO2e/yr")
        except Exception as exc:
            logger.warning(f"  Phase 5 Dynamic CI failed ({exc})")
        return result

    # ------------------------------------------------------------------
    # Phase 6 — Synthesis (fill any remaining baseline gaps)
    # ------------------------------------------------------------------

    def _phase6_synthesis(self, routes: List[Any], result: CARMAResult) -> CARMAResult:
        # Compute baseline if MILP phase didn't populate it
        if result.baseline_cost == 0.0:
            _cost_map = {"truck": 1.5, "rail": 0.8, "ship": 0.3, "air": 12.0}
            result.baseline_cost = sum(
                r.distance_km * _cost_map.get(r.transport_mode, 1.5)
                for r in routes
            )
        if result.baseline_emissions_kg == 0.0 and self._phys_model is not None:
            try:
                from algorithm.physics.emission_model import RouteEmissionInput
                result.baseline_emissions_kg = sum(
                    self._phys_model.compute(RouteEmissionInput(
                        distance_km=r.distance_km,
                        weight_tons=r.weight_tons,
                        transport_mode=r.transport_mode,
                    )).total_emission_kg
                    for r in routes
                )
            except Exception:
                pass
        logger.info(f"  Baseline: cost=EUR {result.baseline_cost:,.0f}  "
                    f"em={result.baseline_emissions_kg:,.0f} kg")
        return result
