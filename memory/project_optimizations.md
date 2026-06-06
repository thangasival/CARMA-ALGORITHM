---
name: carbon-supply-chain-optimizations
description: All algorithmic improvements implemented for the carbon-aware supply chain optimization project
metadata:
  type: project
---

Six algorithmic improvements implemented and validated (2026-06-05):

1. **Physics-Informed Emission Model v2** — `src/physics/emission_model_v2.py`
   - Grubb payload efficiency curve, COPERT HDM speed model, quadratic temperature, non-linear congestion (HBEFA), bidirectional slope with regenerative braking, weather-congestion coupling
   - 15 new ML features vs 5 in v1; physics_v2_emission correlation = 1.0 on synthetic data
   - **Why:** v1 multiplicative factors were physically incorrect (linear temp, symmetric slope, independent weather×congestion)

2. **Hybrid ML-GA v2** — `src/optimization/hybrid_ml_ga.py` (full rewrite)
   - Batch vectorized fitness evaluation (10-50× speedup), 3 objectives (cost/emissions/time), route-aware crossover at gene boundaries, adaptive mutation decay, explicit Physics v2 fallback (no more silent EF table)
   - **Why:** v1 had critical bug — GA fell back to simple EF table when ML not connected, defeating "Hybrid" claim

3. **Context-Adaptive Ensemble** — `src/ml_models/adaptive_ensemble.py`
   - SegmentedEnsemble: 6 route segments, per-segment optimal (w_RF, w_XGB) via grid search → 1.44% MAPE vs 3.13% fixed
   - SoftMixtureEnsemble: learned Ridge gating network, softmax weights
   - StackedEnsemble: OOF Ridge meta-learner with physics v2 as 3rd expert
   - **Why:** Fixed 0.25/0.75 ignores that RF outperforms XGB on short-haul

4. **Carbon-Budget MILP** — `src/optimization/carbon_milp.py`
   - PuLP + CBC; solves in 50ms vs GA's 5+ minutes; certified optimal
   - sweep_budgets() generates exact Pareto frontier across budget levels
   - Shadow price = internal carbon abatement cost (€/kg CO2e)
   - **Why:** GA gives heuristic approximation; MILP gives certified optimum for static routing

5. **NSGA-III 4-Objective** — `src/optimization/nsga3_optimizer.py`
   - 4th objective: service unreliability (mode + weather + congestion risk)
   - 84 structured reference directions (Das-Dennis simplex lattice, M=4, p=6)
   - Tchebycheff scalarization for preferred solution selection
   - **Why:** NSGA-II crowding distance degrades in 3+ objective space

6. **Dynamic Carbon-Intensity Routing** — `src/optimization/dynamic_carbon_routing.py`
   - 24-hour grid CI profiles for ES/DE/FR/GB/EU (Ember Climate 2023)
   - Optimizes departure time for electrified rail/trucks to align with green grid hours
   - Fleet demo: 8.89% emission reduction = 41.66 tonnes CO2e/year just from scheduling shifts
   - Electric truck Madrid-Valencia: 37.2% saving by departing at solar noon
   - **Why:** Same route, same mode, different hour = 2-4× different CI; no existing supply chain tools model this

**How to apply:** Each module is self-contained with its own `__main__` demo. Validate physics v2 first: `python validate_emission_model_v2.py`. Integration order: physics_v2 → synthetic_generator (updated) → emission_predictors (updated feature engineering) → adaptive_ensemble → MILP or NSGA-III.
