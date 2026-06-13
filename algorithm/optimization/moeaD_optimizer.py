"""
MOEA/D — Multi-Objective Evolutionary Algorithm Based on Decomposition
=======================================================================
Baseline optimizer for benchmarking against DCCT-NSGA-III.

Implements Tchebycheff decomposition (Zhang & Li 2007) with:
  - Das-Dennis weight vectors (same as NSGA-III reference directions)
  - Neighbourhood-based update (T nearest weight vectors)
  - Same 4-objective fitness evaluation as NSGA-III (cost, emissions, time, CRI)
  - No warm-start or dual-variable conditioning (pure decomposition baseline)

Used in the DCCT ablation study to show that DCCT's benefit comes from
the primal+dual certificate transfer, not just from having more reference
structure than NSGA-II.

Reference
---------
Zhang, Q. & Li, H. (2007). MOEA/D: A multiobjective evolutionary algorithm
based on decomposition. IEEE Transactions on Evolutionary Computation, 11(6),
712-731. DOI: 10.1109/TEVC.2007.892759.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from algorithm.optimization.nsga3_optimizer import (
    TRANSPORT_MODES,
    Route,
    _MODE_COST_PER_KM,
    _MODE_SPEED_KMH,
    compute_cri,
    generate_reference_directions,
)

logger = logging.getLogger(__name__)


class MOEADOptimizer:
    """
    MOEA/D with Tchebycheff decomposition.

    Decomposes the 4-objective problem into H scalar subproblems, each
    defined by a weight vector w_j. Each subproblem maintains one solution
    and updates it using information from T neighbouring subproblems.

    Parameters
    ----------
    population_size : number of subproblems H (≈ Das-Dennis H for fair comparison)
    n_partitions    : simplex divisions p (same as NSGA-III's p for same H)
    n_neighbors     : neighbourhood size T (typically 0.1 × H)
    """

    def __init__(
        self,
        ml_predictor=None,
        population_size: int = 84,
        n_partitions: int = 6,
        n_neighbors: int = 10,
    ):
        self.ml_predictor    = ml_predictor
        self.pop_size        = population_size
        self.n_obj           = 4
        self.T               = n_neighbors
        self.crossover_prob  = 0.75
        self.mutation_prob   = 0.20
        self.n_generations   = 100

        # Weight vectors (same generation as NSGA-III reference dirs)
        self.weights = generate_reference_directions(self.n_obj, n_partitions)
        self.pop_size = len(self.weights)  # use exact H not approximate

        # Precompute T-nearest neighbours for each weight vector
        dists = np.linalg.norm(
            self.weights[:, np.newaxis, :] - self.weights[np.newaxis, :, :], axis=2
        )
        self.neighbors = np.argsort(dists, axis=1)[:, :self.T]

        self._phys_model = None
        self.original_routes: List[Route] = []
        self.history: List[Dict] = []

    # ------------------------------------------------------------------
    # Public API (mirrors NSGA3Optimizer.optimize_routes)
    # ------------------------------------------------------------------

    def optimize_routes(
        self,
        routes: List[Route],
        n_generations: int = None,
        milp_assignments: Optional[Dict[str, str]] = None,  # ignored — no warm-start
        shadow_price: Optional[float] = None,               # ignored — no dual channel
    ) -> Dict[str, Any]:
        """
        Run MOEA/D on the 4-objective routing problem.

        milp_assignments and shadow_price are accepted but ignored, so the
        same call signature works in benchmarking code that also calls NSGA-III.

        Returns
        -------
        dict: pareto_front, optimization_time, n_generations, improvement_metrics
        """
        if n_generations:
            self.n_generations = n_generations
        self.original_routes = routes

        if self.ml_predictor is None:
            self._init_phys_fallback()

        logger.info(f"MOEA/D[Tchebycheff]: {len(routes)} routes  "
                    f"H={self.pop_size}  T={self.T}  gen={self.n_generations}")

        start = time.perf_counter()
        import random

        # Initialise population (random feasible)
        population = self._init_population(routes)
        fitnesses  = self._eval_all(population, routes)

        # Ideal point z* (minimise all)
        z_star = fitnesses.min(axis=0).copy()

        for gen in range(self.n_generations):
            t       = gen / max(1, self.n_generations - 1)
            mut_rate = self.mutation_prob * (1 - t) + 0.05 * t

            for i in range(self.pop_size):
                # Select two parents from neighbourhood
                nbrs = self.neighbors[i]
                p1_idx, p2_idx = np.random.choice(nbrs, 2, replace=False)
                child = self._crossover(population[p1_idx], population[p2_idx], routes)
                child = self._mutate(child, routes, rate=mut_rate)
                child_fit = self._eval_one(child, routes)

                # Update ideal point
                z_star = np.minimum(z_star, child_fit)

                # Update neighbourhood solutions if child is better
                for nb_idx in nbrs:
                    w = self.weights[nb_idx]
                    if _tchebycheff(child_fit, w, z_star) <= \
                       _tchebycheff(fitnesses[nb_idx], w, z_star):
                        population[nb_idx] = child[:]
                        fitnesses[nb_idx]  = child_fit

            self._record(gen, fitnesses, mut_rate)

        # Extract non-dominated front from final population
        pareto_front = _extract_pareto(population, fitnesses)
        elapsed = time.perf_counter() - start

        return {
            "pareto_front":        self._decode_pareto(pareto_front, routes),
            "optimization_time":   round(elapsed, 2),
            "n_generations":       self.n_generations,
            "population_size":     self.pop_size,
            "n_reference_dirs":    self.pop_size,
            "history":             self.history,
            "improvement_metrics": self._improvements(pareto_front, fitnesses, routes),
        }

    def get_pareto_fitnesses(self) -> np.ndarray:
        """Return (n, 4) objective matrix of last Pareto front individuals."""
        if not hasattr(self, '_last_pareto_fits'):
            return np.empty((0, 4))
        return self._last_pareto_fits

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _init_population(self, routes: List[Route]) -> List[List]:
        import random
        pop = []
        for _ in range(self.pop_size):
            genes = []
            for r in routes:
                feasible = self._feasible_modes(r)
                genes.extend([
                    TRANSPORT_MODES.index(random.choice(feasible)),
                    random.uniform(0.90, 1.10),
                    random.randint(0, 1),
                ])
            pop.append(genes)
        return pop

    def _feasible_modes(self, r: Route) -> List[str]:
        from algorithm.optimization.hybrid_ml_ga import _MODE_MIN_DIST as _MD
        return [m for m in TRANSPORT_MODES if r.distance_km >= _MD.get(m, 0.0)]

    # ------------------------------------------------------------------
    # Fitness evaluation
    # ------------------------------------------------------------------

    def _eval_all(self, population: List[List], routes: List[Route]) -> np.ndarray:
        return np.array([self._eval_one(ind, routes) for ind in population])

    def _eval_one(self, ind: List, routes: List[Route]) -> np.ndarray:
        import pandas as pd
        rows = []
        for j, r in enumerate(routes):
            mode_idx = max(0, min(3, int(round(ind[j * 3]))))
            dist     = r.distance_km * max(0.85, min(1.15, float(ind[j * 3 + 1])))
            ap       = bool(round(ind[j * 3 + 2]))
            mode     = TRANSPORT_MODES[mode_idx]
            from algorithm.optimization.hybrid_ml_ga import _MODE_MIN_DIST
            if r.distance_km < _MODE_MIN_DIST.get(mode, 0.0):
                mode = "truck"
            rows.append({
                "distance_km": dist, "weight_tons": r.weight_tons,
                "transport_mode": mode, "commodity_type": r.commodity_type,
                "temperature_c": r.temperature_c, "congestion_factor": r.congestion_factor,
                "slope_degrees": r.slope_degrees, "is_uphill": getattr(r, "is_uphill", True),
                "weather_condition": r.weather_condition,
                "is_peak_hour": r.is_peak_hour and not ap, "is_weekend": r.is_weekend,
            })

        df  = pd.DataFrame(rows)
        ems = self._phys_batch(df)

        cost = unrel = time_h = 0.0
        n = len(routes)
        for k, row in enumerate(rows):
            m = row["transport_mode"]
            d = row["distance_km"]
            c = d * _MODE_COST_PER_KM.get(m, 1.5)
            if row["is_peak_hour"]:
                c *= 1.15
            c *= row["congestion_factor"]
            cost  += c
            time_h += d / max(1.0, _MODE_SPEED_KMH.get(m, 80.0))
            unrel += compute_cri(m, row["weather_condition"], row["congestion_factor"]) / n

        em = float(ems.sum())
        return np.array([cost, em, time_h, unrel])

    # ------------------------------------------------------------------
    # Genetic operators
    # ------------------------------------------------------------------

    def _crossover(self, p1: List, p2: List, routes: List[Route]) -> List:
        import random
        n = len(routes)
        if n < 2:
            return p1[:]
        pt1, pt2 = sorted(random.sample(range(1, n), 2))
        child = p1[:]
        child[pt1*3 : pt2*3] = p2[pt1*3 : pt2*3]
        return child

    def _mutate(self, ind: List, routes: List[Route], rate: float = 0.10) -> List:
        import random
        child = ind[:]
        for i in range(len(routes)):
            b = i * 3
            if random.random() < rate:
                child[b] = random.randint(0, 3)
            if random.random() < rate:
                child[b+1] = max(0.85, min(1.15, child[b+1] + np.random.normal(0, 0.03)))
            if random.random() < rate:
                child[b+2] = 1 - int(round(child[b+2]))
        return child

    # ------------------------------------------------------------------
    # PIEM fallback
    # ------------------------------------------------------------------

    def _init_phys_fallback(self):
        try:
            from algorithm.physics.emission_model import EmissionModelV2
            self._phys_model = EmissionModelV2()
        except Exception as exc:
            logger.warning(f"PIEM unavailable ({exc})")

    def _phys_batch(self, df) -> np.ndarray:
        if self._phys_model is not None:
            try:
                from algorithm.physics.emission_model import RouteEmissionInput
                return np.array([
                    self._phys_model.compute(RouteEmissionInput(
                        distance_km=float(row["distance_km"]),
                        weight_tons=float(row["weight_tons"]),
                        transport_mode=row["transport_mode"],
                        temperature_c=float(row.get("temperature_c", 20)),
                        congestion_factor=float(row.get("congestion_factor", 1.0)),
                        slope_degrees=float(row.get("slope_degrees", 0.0)),
                        is_uphill=bool(row.get("is_uphill", True)),
                        weather_condition=row.get("weather_condition", "clear"),
                        is_peak_hour=bool(row.get("is_peak_hour", False)),
                        is_weekend=bool(row.get("is_weekend", False)),
                    )).total_emission_kg
                    for _, row in df.iterrows()
                ], dtype=np.float64)
            except Exception:
                pass
        ef = {"truck": 0.161, "rail": 0.041, "ship": 0.015, "air": 0.602}
        return np.array([
            row["distance_km"] * row["weight_tons"] * ef.get(row["transport_mode"], 0.161)
            for _, row in df.iterrows()
        ], dtype=np.float64)

    # ------------------------------------------------------------------
    # Decode / output
    # ------------------------------------------------------------------

    def _decode_pareto(self, pareto: List[Tuple], routes: List[Route]) -> List[Dict]:
        solutions = []
        n = max(1, len(routes))
        for ind, fit in pareto:
            c, em, hrs, unrel = fit
            modes = []
            for j, r in enumerate(routes):
                mode_idx = max(0, min(3, int(round(ind[j*3]))))
                mode = TRANSPORT_MODES[mode_idx]
                modes.append(mode)
            solutions.append({
                "total_cost": round(c, 2), "total_emissions_kg": round(em, 2),
                "total_time_hours": round(hrs, 2), "avg_unreliability": round(unrel, 4),
                "cost_per_route": round(c/n, 2), "emissions_per_route": round(em/n, 2),
                "mode_assignments": modes,
            })
        self._last_pareto_fits = np.array([f for _, f in pareto]) if pareto else np.empty((0,4))
        return sorted(solutions, key=lambda s: s["total_emissions_kg"])

    def _record(self, gen: int, fitnesses: np.ndarray, mut_rate: float):
        self.history.append({
            "generation": gen,
            "min_cost": float(fitnesses[:, 0].min()),
            "min_emissions": float(fitnesses[:, 1].min()),
            "min_time_hours": float(fitnesses[:, 2].min()),
            "min_unreliability": float(fitnesses[:, 3].min()),
            "mut_rate": round(mut_rate, 4),
        })

    def _improvements(self, pareto, fitnesses, routes) -> Dict:
        ef = {"truck": 0.161, "rail": 0.041, "ship": 0.015, "air": 0.602}
        bc = sum(r.distance_km * _MODE_COST_PER_KM.get(r.transport_mode, 1.5) for r in routes)
        be = sum(r.distance_km * r.weight_tons * ef.get(r.transport_mode, 0.161) for r in routes)
        if not pareto:
            return {"baseline_cost": round(bc,2), "baseline_emissions_kg": round(be,2)}
        fits = np.array([f for _, f in pareto])
        return {
            "baseline_cost": round(bc, 2),
            "baseline_emissions_kg": round(be, 2),
            "best_cost": round(fits[:, 0].min(), 2),
            "best_emissions_kg": round(fits[:, 1].min(), 2),
            "cost_improvement_pct": round((bc - fits[:,0].min())/bc*100, 2),
            "emission_improvement_pct": round((be - fits[:,1].min())/be*100, 2),
            "pareto_front_size": len(pareto),
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tchebycheff(fit: np.ndarray, w: np.ndarray, z_star: np.ndarray) -> float:
    """Tchebycheff scalarization: max_i { w_i × |f_i - z*_i| }."""
    return float(np.max(w * np.abs(fit - z_star)))


def _extract_pareto(
    population: List[List], fitnesses: np.ndarray
) -> List[Tuple[List, np.ndarray]]:
    """Extract non-dominated front from population."""
    n = len(population)
    dominated = np.zeros(n, dtype=bool)
    for i in range(n):
        for j in range(n):
            if i != j and not dominated[j]:
                if np.all(fitnesses[j] <= fitnesses[i]) and np.any(fitnesses[j] < fitnesses[i]):
                    dominated[i] = True
                    break
    return [(population[i], fitnesses[i]) for i in range(n) if not dominated[i]]
