"""
Carbon-Budget Constrained MILP Optimizer
==========================================
Formulates the transport mode assignment problem as a Mixed-Integer Linear
Program (MILP) with a hard carbon budget constraint.

This replaces the Genetic Algorithm for the *static* routing case and:
  - Returns a certified optimal solution (not a heuristic approximation)
  - Directly answers "minimum cost to achieve X% emission reduction"
  - Solves networks of 10 000+ routes in seconds (via PuLP + CBC/GLPK)
  - Provides shadow prices (dual variables) showing the economic cost of
    tightening the carbon budget — the "internal carbon price"

Mathematical formulation
------------------------
Decision variable:
  x[r, m] ∈ {0, 1}   = 1 if route r uses transport mode m

Objective (primary):
  min  Σ_{r,m}  c[r,m] × x[r,m]       (minimise total logistics cost)

Alternatively (secondary), or as weighted scalarisation:
  min  Σ_{r,m}  (c[r,m] + λ_carbon × e[r,m]) × x[r,m]

Constraints:
  (1) Σ_m  x[r,m] = 1          ∀ r   (exactly one mode per route)
  (2) Σ_{r,m}  e[r,m] × x[r,m] ≤ B   (hard carbon budget)
  (3) x[r,m] = 0  if mode m infeasible for route r
  (4) x[r,m] ∈ {0, 1}

Where:
  c[r,m] = cost of route r with mode m   (€)
  e[r,m] = emission of route r with mode m  (kg CO2e, from PIEM or ML)
  B      = carbon budget (kg CO2e) — typically set as fraction of baseline

Shadow price interpretation:
  λ* = dual variable on constraint (2)
  λ* represents the implicit carbon price at which the transition to lower-
  emission modes becomes cost-neutral — the "internal carbon abatement cost"
  in €/kg CO2e.

Reference:
  Williams (2013) "Model Building in Mathematical Programming", Wiley.
  Dekker et al. (2012) "A framework for sustainable supply chain management",
    European Journal of Operational Research.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mode tables (must match hybrid_ml_ga.py)
# ---------------------------------------------------------------------------

TRANSPORT_MODES = ["truck", "rail", "ship", "air"]

_MODE_COST_PER_KM: Dict[str, float] = {
    "truck": 1.50,
    "rail":  0.80,
    "ship":  0.30,
    "air":   12.0,
}

_MODE_MIN_DIST_KM: Dict[str, float] = {
    "truck": 0.0,
    "rail":  50.0,
    "ship":  300.0,
    "air":   0.0,
}

# Transfer / terminal costs added when switching from truck to another mode (€)
_TRANSFER_COST: Dict[str, float] = {
    "truck": 0.0,
    "rail":  680.0,
    "ship":  750.0,
    "air":   350.0,
}


# ---------------------------------------------------------------------------
# Route input for MILP
# ---------------------------------------------------------------------------

@dataclass
class MILPRoute:
    """
    A route in the MILP network.

    All cost and emission values per mode are pre-computed before solving;
    the solver only handles the binary assignment.
    """
    route_id:          str
    origin:            str
    destination:       str
    distance_km:       float
    weight_tons:       float
    commodity_type:    str
    current_mode:      str            # baseline mode (before optimisation)
    # Pre-computed per-mode cost and emission arrays (indexed by TRANSPORT_MODES)
    cost_per_mode:     Dict[str, float] = field(default_factory=dict)
    emission_per_mode: Dict[str, float] = field(default_factory=dict)
    feasible_modes:    List[str]        = field(default_factory=list)

    def __post_init__(self):
        if not self.feasible_modes:
            self.feasible_modes = [
                m for m in TRANSPORT_MODES
                if self.distance_km >= _MODE_MIN_DIST_KM[m]
            ]


# ---------------------------------------------------------------------------
# Results dataclass
# ---------------------------------------------------------------------------

@dataclass
class MILPResult:
    """
    Full result from one MILP optimisation run.
    """
    status:              str           # 'Optimal', 'Infeasible', etc.
    total_cost:          float
    total_emissions_kg:  float
    baseline_cost:       float
    baseline_emissions:  float
    cost_change_pct:     float
    emission_change_pct: float
    carbon_budget_kg:    float
    shadow_price_eur_per_kg: Optional[float]  # internal carbon abatement cost
    mode_assignments:    Dict[str, str]       # route_id → assigned mode
    mode_shifts:         List[Dict]           # routes where mode changed
    solve_time_s:        float
    solver_used:         str

    def print_summary(self):
        print("\n" + "=" * 65)
        print("MILP CARBON-BUDGET OPTIMISATION RESULTS")
        print("=" * 65)
        print(f"  Status          : {self.status}")
        print(f"  Solver          : {self.solver_used}")
        print(f"  Solve time      : {self.solve_time_s:.3f}s")
        print(f"  Carbon budget   : {self.carbon_budget_kg:,.0f} kg CO2e")
        print()
        print(f"  Baseline cost   : €{self.baseline_cost:>12,.2f}")
        print(f"  Optimal cost    : €{self.total_cost:>12,.2f}  "
              f"({self.cost_change_pct:+.1f}%)")
        print()
        print(f"  Baseline emis   : {self.baseline_emissions:>12,.0f} kg CO2e")
        print(f"  Optimal emis    : {self.total_emissions_kg:>12,.0f} kg CO2e  "
              f"({self.emission_change_pct:+.1f}%)")
        if self.shadow_price_eur_per_kg is not None:
            print(f"\n  Shadow price    : €{self.shadow_price_eur_per_kg:.4f}/kg CO2e "
                  f"(= €{self.shadow_price_eur_per_kg*1000:.2f}/tonne CO2e)")
            print("  (This is the marginal abatement cost at the given budget)")
        print(f"\n  Mode shifts     : {len(self.mode_shifts)} routes changed")
        for shift in self.mode_shifts[:8]:
            print(f"    {shift['route_id']:<20}  "
                  f"{shift['from_mode']} -> {shift['to_mode']}  "
                  f"cost {shift['cost_delta']:+,.0f} EUR  "
                  f"em {shift['emission_delta']:+,.0f} kg")
        if len(self.mode_shifts) > 8:
            print(f"    ... and {len(self.mode_shifts) - 8} more")
        print("=" * 65)


# ---------------------------------------------------------------------------
# Main MILP solver
# ---------------------------------------------------------------------------

class CarbonBudgetMILP:
    """
    Carbon-Budget Constrained MILP Optimizer.

    Finds the minimum-cost mode assignment for all routes subject to a hard
    upper bound on total network CO2e emissions.

    Parameters
    ----------
    emission_model : EmissionModelV2 instance (or None → use cost table EF)
    ets_price_eur_per_kg : EU ETS carbon price (€/kg CO2e).
        If > 0, the carbon cost is added to the logistics cost in the
        objective, making the MILP internally price carbon.
        Default 0.0 (pure logistics cost minimisation with hard budget).
    """

    def __init__(
        self,
        emission_model=None,
        ets_price_eur_per_kg: float = 0.0,
    ):
        self.emission_model = emission_model
        self.ets_price = ets_price_eur_per_kg
        self._solver = None
        self._solver_name = "Unknown"
        self._init_solver()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def optimise(
        self,
        routes: List[MILPRoute],
        carbon_budget_kg: Optional[float] = None,
        budget_reduction_pct: Optional[float] = None,
    ) -> MILPResult:
        """
        Solve the carbon-budget MILP.

        Parameters
        ----------
        routes              : list of MILPRoute objects (pre-costed)
        carbon_budget_kg    : absolute carbon budget in kg CO2e
        budget_reduction_pct: if carbon_budget_kg is None, compute budget as
                              baseline × (1 - budget_reduction_pct/100)
                              e.g. 20 → 20% reduction from baseline

        Returns
        -------
        MILPResult
        """
        # Pre-compute costs and emissions if not yet done
        self._precompute_route_costs(routes)

        # Baseline
        baseline_cost = sum(
            r.cost_per_mode.get(r.current_mode, 0.0) for r in routes
        )
        baseline_em = sum(
            r.emission_per_mode.get(r.current_mode, 0.0) for r in routes
        )

        # Determine budget
        if carbon_budget_kg is None:
            if budget_reduction_pct is None:
                raise ValueError("Provide carbon_budget_kg or budget_reduction_pct")
            carbon_budget_kg = baseline_em * (1.0 - budget_reduction_pct / 100.0)

        logger.info(f"MILP: {len(routes)} routes  budget={carbon_budget_kg:,.0f} kg  "
                    f"baseline_em={baseline_em:,.0f} kg  "
                    f"baseline_cost=€{baseline_cost:,.0f}")

        start = time.perf_counter()
        result = self._solve_pulp(routes, carbon_budget_kg,
                                  baseline_cost, baseline_em)
        result.solve_time_s = round(time.perf_counter() - start, 4)
        return result

    def sweep_budgets(
        self,
        routes: List[MILPRoute],
        reductions: List[float] = None,
    ) -> pd.DataFrame:
        """
        Solve at multiple budget levels and return a cost-emission trade-off table.

        This generates the exact Pareto frontier for this MILP (no heuristic
        approximation — each point is a certified optimum).

        Parameters
        ----------
        routes     : list of MILPRoute objects
        reductions : list of % emission reductions to evaluate
                     default: [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]

        Returns
        -------
        pd.DataFrame with columns: reduction_pct, budget_kg, cost, emissions,
                                    cost_change_pct, shadow_price
        """
        if reductions is None:
            reductions = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]

        self._precompute_route_costs(routes)

        rows = []
        for pct in reductions:
            logger.info(f"Sweep: {pct}% reduction target")
            result = self.optimise(routes, budget_reduction_pct=pct)
            rows.append({
                "reduction_target_pct":  pct,
                "carbon_budget_kg":      round(result.carbon_budget_kg, 0),
                "optimal_cost_eur":      round(result.total_cost, 2),
                "actual_emissions_kg":   round(result.total_emissions_kg, 0),
                "cost_change_pct":       round(result.cost_change_pct, 2),
                "emission_change_pct":   round(result.emission_change_pct, 2),
                "shadow_price_eur_tonne": round(
                    (result.shadow_price_eur_per_kg or 0) * 1000, 2),
                "status":                result.status,
                "n_mode_shifts":         len(result.mode_shifts),
                "solve_time_s":          result.solve_time_s,
            })

        df = pd.DataFrame(rows)
        return df

    # ------------------------------------------------------------------
    # PuLP solver
    # ------------------------------------------------------------------

    def _solve_pulp(
        self,
        routes: List[MILPRoute],
        budget: float,
        baseline_cost: float,
        baseline_em: float,
    ) -> MILPResult:
        """Build and solve the MILP using PuLP."""
        try:
            import pulp
        except ImportError:
            raise ImportError(
                "PuLP is required: pip install pulp\n"
                "For better performance also install CBC: pip install pulp[cbc]"
            )

        prob = pulp.LpProblem("CarbonBudgetRouting", pulp.LpMinimize)

        # ---- Decision variables ----
        # x[r_id][m] = 1 if route r uses mode m
        x = {}
        for r in routes:
            x[r.route_id] = {}
            for m in r.feasible_modes:
                x[r.route_id][m] = pulp.LpVariable(
                    f"x_{r.route_id}_{m}", cat="Binary"
                )

        # ---- Objective ----
        # Cost + optional ETS carbon price
        obj_terms = []
        for r in routes:
            for m in r.feasible_modes:
                c = r.cost_per_mode[m]
                e = r.emission_per_mode[m]
                effective_cost = c + self.ets_price * e
                obj_terms.append(effective_cost * x[r.route_id][m])

        prob += pulp.lpSum(obj_terms), "TotalCost"

        # ---- Constraint 1: exactly one mode per route ----
        for r in routes:
            prob += (
                pulp.lpSum(x[r.route_id][m] for m in r.feasible_modes) == 1,
                f"OneModePerRoute_{r.route_id}"
            )

        # ---- Constraint 2: carbon budget ----
        emission_terms = []
        for r in routes:
            for m in r.feasible_modes:
                emission_terms.append(r.emission_per_mode[m] * x[r.route_id][m])

        prob += (
            pulp.lpSum(emission_terms) <= budget,
            "CarbonBudget"
        )

        # ---- Solve ----
        solver = self._solver or pulp.PULP_CBC_CMD(msg=0)
        prob.solve(solver)

        status = pulp.LpStatus[prob.status]
        logger.info(f"MILP status: {status}  "
                    f"objective=€{pulp.value(prob.objective):,.2f}")

        if status != "Optimal":
            logger.warning(f"MILP did not find optimal solution: {status}")
            return MILPResult(
                status=status, total_cost=float("inf"),
                total_emissions_kg=float("inf"),
                baseline_cost=baseline_cost, baseline_emissions=baseline_em,
                cost_change_pct=float("nan"), emission_change_pct=float("nan"),
                carbon_budget_kg=budget, shadow_price_eur_per_kg=None,
                mode_assignments={}, mode_shifts=[],
                solve_time_s=0.0, solver_used=self._solver_name,
            )

        # ---- Extract solution ----
        mode_assignments = {}
        for r in routes:
            for m in r.feasible_modes:
                if pulp.value(x[r.route_id][m]) > 0.5:
                    mode_assignments[r.route_id] = m
                    break
            if r.route_id not in mode_assignments:
                mode_assignments[r.route_id] = r.current_mode  # fallback

        total_cost = sum(
            r.cost_per_mode.get(mode_assignments.get(r.route_id, r.current_mode), 0.0)
            for r in routes
        )
        total_em = sum(
            r.emission_per_mode.get(mode_assignments.get(r.route_id, r.current_mode), 0.0)
            for r in routes
        )

        # Shadow price on carbon budget constraint
        shadow_price = None
        try:
            budget_constr = prob.constraints.get("CarbonBudget")
            if budget_constr is not None:
                shadow_price = -budget_constr.pi  # PuLP: dual of ≤ constraint
        except Exception:
            pass

        # Mode shifts
        mode_shifts = []
        for r in routes:
            assigned = mode_assignments.get(r.route_id, r.current_mode)
            if assigned != r.current_mode:
                mode_shifts.append({
                    "route_id":       r.route_id,
                    "from_mode":      r.current_mode,
                    "to_mode":        assigned,
                    "distance_km":    r.distance_km,
                    "weight_tons":    r.weight_tons,
                    "cost_delta":     r.cost_per_mode[assigned] - r.cost_per_mode[r.current_mode],
                    "emission_delta": r.emission_per_mode[assigned] - r.emission_per_mode[r.current_mode],
                })

        return MILPResult(
            status=status,
            total_cost=round(total_cost, 2),
            total_emissions_kg=round(total_em, 2),
            baseline_cost=round(baseline_cost, 2),
            baseline_emissions=round(baseline_em, 2),
            cost_change_pct=round((total_cost - baseline_cost) / max(1, baseline_cost) * 100, 2),
            emission_change_pct=round((total_em - baseline_em) / max(1, baseline_em) * 100, 2),
            carbon_budget_kg=round(budget, 2),
            shadow_price_eur_per_kg=round(shadow_price, 6) if shadow_price else None,
            mode_assignments=mode_assignments,
            mode_shifts=sorted(mode_shifts, key=lambda s: s["emission_delta"]),
            solve_time_s=0.0,
            solver_used=self._solver_name,
        )

    # ------------------------------------------------------------------
    # Cost / emission pre-computation
    # ------------------------------------------------------------------

    def _precompute_route_costs(self, routes: List[MILPRoute]):
        """
        Fill in cost_per_mode and emission_per_mode for every feasible mode.
        Uses PIEM for emissions if emission_model is provided.
        """
        for r in routes:
            if r.cost_per_mode and r.emission_per_mode:
                continue  # already computed

            for m in r.feasible_modes:
                # Cost
                base_cost = r.distance_km * _MODE_COST_PER_KM[m] * r.weight_tons
                transfer  = _TRANSFER_COST[m] if m != r.current_mode else 0.0
                r.cost_per_mode[m] = base_cost + transfer

                # Emission
                if self.emission_model is not None:
                    try:
                        from algorithm.physics.emission_model import RouteEmissionInput
                        inp = RouteEmissionInput(
                            distance_km=r.distance_km,
                            weight_tons=r.weight_tons,
                            transport_mode=m,
                        )
                        r.emission_per_mode[m] = self.emission_model.compute(inp).total_emission_kg
                    except Exception:
                        r.emission_per_mode[m] = self._simple_emission(r, m)
                else:
                    r.emission_per_mode[m] = self._simple_emission(r, m)

    @staticmethod
    def _simple_emission(route: MILPRoute, mode: str) -> float:
        ef = {"truck": 0.161, "rail": 0.041, "ship": 0.015, "air": 0.602}
        return route.distance_km * route.weight_tons * ef.get(mode, 0.161)

    # ------------------------------------------------------------------
    # Solver initialisation
    # ------------------------------------------------------------------

    def _init_solver(self):
        """Try to load best available solver (CBC > GLPK > default)."""
        try:
            import pulp
            solvers_to_try = [
                ("CBC",  lambda: pulp.PULP_CBC_CMD(msg=0)),
                ("GLPK", lambda: pulp.GLPK_CMD(msg=0)),
            ]
            for name, factory in solvers_to_try:
                try:
                    solver = factory()
                    self._solver = solver
                    self._solver_name = name
                    logger.info(f"MILP solver: {name}")
                    return
                except Exception:
                    continue
            self._solver = None
            self._solver_name = "PuLP default"
        except ImportError:
            self._solver = None
            self._solver_name = "PuLP not installed"


# ---------------------------------------------------------------------------
# Factory: convert Route objects from hybrid_ml_ga.py → MILPRoute
# ---------------------------------------------------------------------------

def routes_to_milp(routes) -> List[MILPRoute]:
    """
    Convert hybrid_ml_ga.Route objects to MILPRoute objects for the MILP solver.
    """
    milp_routes = []
    for i, r in enumerate(routes):
        milp_routes.append(MILPRoute(
            route_id     = getattr(r, "route_id", f"R{i:04d}"),
            origin       = r.origin,
            destination  = r.destination,
            distance_km  = r.distance_km,
            weight_tons  = r.weight_tons,
            commodity_type = r.commodity_type,
            current_mode = r.transport_mode,
        ))
    return milp_routes


def build_milp_from_df(df: pd.DataFrame) -> List[MILPRoute]:
    """
    Build MILPRoute list from a DataFrame (e.g. from SyntheticRouteGenerator).
    """
    routes = []
    for _, row in df.iterrows():
        r = MILPRoute(
            route_id      = str(row.get("route_id", _)),
            origin        = str(row.get("origin", "?")),
            destination   = str(row.get("destination", "?")),
            distance_km   = float(row["distance_km"]),
            weight_tons   = float(row["weight_tons"]),
            commodity_type = str(row.get("commodity_type", "general")),
            current_mode  = str(row["transport_mode"]),
        )
        routes.append(r)
    return routes


# ---------------------------------------------------------------------------
# Standalone demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
    logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")

    print("\n=== Carbon-Budget MILP Optimizer — Demo ===\n")

    # --- Salamanca-style network ---
    salamanca_routes = [
        MILPRoute("R001", "Salamanca", "Madrid",    212,  120, "general", "truck"),
        MILPRoute("R002", "Salamanca", "Barcelona", 796,   85, "general", "truck"),
        MILPRoute("R003", "Salamanca", "Valencia",  593,   75, "general", "truck"),
        MILPRoute("R004", "Salamanca", "Sevilla",   465,   65, "general", "truck"),
        MILPRoute("R005", "Salamanca", "Bilbao",    397,   55, "general", "truck"),
        MILPRoute("R006", "Salamanca", "Zaragoza",  558,   50, "general", "truck"),
        MILPRoute("R007", "Salamanca", "Malaga",    582,   45, "general", "truck"),
        MILPRoute("R008", "Salamanca", "Murcia",    624,   40, "general", "truck"),
        MILPRoute("R009", "Salamanca", "Valladolid",115,   30, "general", "truck"),
        MILPRoute("R010", "Salamanca", "Cordoba",   401,   28, "general", "truck"),
        MILPRoute("R011", "Salamanca", "Alicante",  607,   25, "general", "truck"),
    ]

    # Load PIEM
    try:
        from algorithm.physics.emission_model import EmissionModelV2
        em = EmissionModelV2()
    except Exception:
        em = None

    solver = CarbonBudgetMILP(emission_model=em, ets_price_eur_per_kg=0.0)

    # 1. Single solve at 20% reduction
    print("--- Single solve: 20% emission reduction target ---")
    result = solver.optimise(salamanca_routes, budget_reduction_pct=20)
    result.print_summary()

    # 2. Sweep: exact Pareto frontier at 0-50% reductions
    print("\n--- Pareto sweep: 0% → 50% reduction targets ---")
    pareto_df = solver.sweep_budgets(salamanca_routes,
                                     reductions=[0, 10, 20, 30, 40, 50])
    print(pareto_df[[
        "reduction_target_pct", "optimal_cost_eur", "actual_emissions_kg",
        "cost_change_pct", "shadow_price_eur_tonne", "n_mode_shifts", "solve_time_s"
    ]].to_string(index=False))

    # 3. With ETS carbon price
    print("\n--- With EU ETS carbon price (€80/tonne = €0.08/kg) ---")
    ets_solver = CarbonBudgetMILP(
        emission_model=em, ets_price_eur_per_kg=0.08)
    ets_result = ets_solver.optimise(salamanca_routes, budget_reduction_pct=0)
    ets_result.print_summary()
    print("(Budget=0% — ETS price alone drives mode shifts where carbon-cost offsets transport-cost)")
