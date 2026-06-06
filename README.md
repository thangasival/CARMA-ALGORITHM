# CARMA-ALGORITHM

**Carbon-Aware Routing with Multi-objective Adaptive ensemble**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.14](https://img.shields.io/badge/python-3.14.3-blue.svg)](https://www.python.org/downloads/)
[![Algorithm: CARMA v1.0.0](https://img.shields.io/badge/Algorithm-CARMA%20v1.0.0-green.svg)]()

**Author:** Sivalingam Thangavel  
**Version:** 1.0.0 (2026)

---

## Overview

CARMA is a novel unified algorithmic framework for carbon-aware supply chain optimization. It integrates six tightly coupled components into a single 6-phase pipeline, delivering certified-optimal mode assignments, a Pareto-optimal trade-off surface, and dynamic departure scheduling aligned with grid carbon intensity.

| Letter | Stands for | Component |
|--------|-----------|-----------|
| **C** | **C**arbon-budget constrained | MILP with hard CO₂e budget |
| **A** | **A**daptive ML Ensemble | Segmented Mixture-of-Experts |
| **R** | **R**outing optimization | DCCT-NSGA-III 4-objective search |
| **M** | **M**ulti-objective | Cost, emissions, time, reliability |
| **A** | **A**daptive Physics | Physics-Informed Emission Model (PIEM) |

---

## Validated Results

### Iberian Network (12 routes, Spain — Ember CI profiles)

| Metric | Value |
|--------|-------|
| MILP cost reduction | **−27.9%** (EUR 139,875 → 100,875) |
| MILP emission reduction | **−27.1%** (19,558 → 14,251 kg CO₂e) |
| Mode shifts | **8 routes** changed |
| Pareto-optimal solutions | **84** (NSGA-III, M=4, p=6) |
| Dynamic CI saving | **421 kg CO₂e/run** = **21.9 t CO₂e/year** |
| MILP solve time | **53 ms** (certified optimal, CBC solver) |
| Full pipeline wall time | **~14 s** (2.4× DCCT speedup vs baseline NSGA-III) |

### Rotterdam European Multimodal Hub (14 routes — truck / rail / ship / air)

| Metric | Value |
|--------|-------|
| Truck-only baseline | 13,433 kg CO₂e |
| MILP emission reduction | **74.8%** (2,042 kg CO₂e) — highest across all networks |
| MILP cost reduction | **75.6%** (EUR 64,437 vs EUR 264,435 baseline) |
| Mode shifts | **14 of 14 routes** changed |
| Pareto-optimal solutions | **84** (10.7× cost spread, 7.1× emission spread) |
| ML MAPE (emission prediction) | **10.04%** — best prediction accuracy |
| Dynamic CI saving | **1,063 kg CO₂e/run** = **265.8 t CO₂e/year** |
| Economic value at EU ETS €65/t | **€17,277/year** |
| Full pipeline wall time | **12.9 s** (14 routes, 4 modes: truck/rail/ship/air) |

---

## Why CARMA is the Best Approach

Existing methods solve parts of the problem. CARMA is the first unified framework that solves all parts simultaneously and provably.

### Head-to-Head Comparison

| Capability | Flat-EF heuristic | MILP-only | NSGA-II (Deb 2002) | NSGA-III intermodal | **CARMA** |
|---|:---:|:---:|:---:|:---:|:---:|
| Physics-accurate emission model | — | — | — | — | **PIEM** |
| ML calibration per route segment | — | — | — | — | **Segmented MoE** |
| Certified optimal solution | — | **Yes** | — | — | **Phase 3 MILP** |
| Exact → heuristic knowledge transfer | — | — | — | — | **DCCT** |
| 4 objectives inc. reliability | — | — | 2 only | 4 (no CI) | **4 + CRI** |
| Formal Pareto convergence guarantee | — | — | — | — | **Theorem 1** |
| Hourly grid CI scheduling | — | — | — | — | **Phase 5** |
| O(1) convergence on Pareto extreme | — | — | — | — | **Theorem 2** |

### Why each alternative falls short

**Flat emission factor (EF × d × w):** Ignores payload efficiency, speed, congestion, slope, temperature, and weather. Underestimates truck emissions by 15–40% under congested conditions (Saharidis et al. 2018). Cannot distinguish a half-loaded truck from a full one.

**MILP-only:** Certifiably optimal on a single objective (cost or emissions), but cannot explore the full cost/emission/time/reliability trade-off. Gives one point; CARMA gives 84–92 Pareto-optimal solutions. No reliability objective. No departure-time optimization.

**NSGA-II:** Crowding distance degrades in 3+ dimensional objective space ("curse of dimensionality"). Random population initialization wastes generations rediscovering known optima. No emission model physics. No certified anchor point. CARMA's DCCT achieves in 0 generations what random NSGA-II needs Ω(|S|/N) generations to find.

**NSGA-III intermodal (Shao 2022, Cui 2025):** 4-objective with reliability — but uses flat emission factors, no exact-solver certificate, no dual-variable reference direction conditioning, and no grid CI scheduling. DCCT provides what these works lack: a provable bridge from exact to heuristic optimality.

### Three provable guarantees no prior method has

1. **Theorem 1 — Extremal Anchor:** X*_MILP ∈ PF* at every generation g ≥ 0. The certified-optimal emission point is always on the Pareto front, by construction.
2. **Theorem 2 — O(1) convergence:** G*(ε) = 0 with DCCT vs Ω(|S|/N) without. Validated: 28.1s → 10.6s (2.6× speedup), same N and G_max.
3. **Theorem 3 — SPRD density:** Pareto coverage in the λ*-sensitive region ≥ (1+α) × uniform baseline — denser exactly where the decision-maker's cost-carbon trade-off is most sensitive.

No existing supply chain optimizer provides all three simultaneously.

---

## Three Novel Contributions

### 1. PIEM — Physics-Informed Emission Model
*Type 3+7 — Methodological + New Analytics Methodology*

First supply chain emission formula combining six physical correction factors in one unified multiplicative model:

```
E = d × w × EF × f_payload × f_speed × f_temperature × f_congestion × f_slope × f_weather
```

Prior work (flat EF×d×w) ignores all six factors. Gap confirmed by Saharidis et al. (2018): COPERT/MOVES "do not include parameters considered crucial for stop-and-go congestion."

### 2. DCCT — Dual-Channel Certificate Transfer
*Type 6+8 — Novel Optimization Mechanism + New Optimization Technique*

Transfers the MILP exact solver's primal–dual output (X*, λ*) into NSGA-III via two channels:

```
MILP ──┬── Channel 1: X*  ──[CAPS]──► Seeds 25% of P₀   (Theorem 1: X* ∈ PF* always)
       └── Channel 2: λ*  ──[SPRD]──► Biases ref. dirs   (Theorem 3: density ≥ (1+α)×)
                                              ↓
                              Certificate-Anchored Pareto Front PF*
```

No prior MOEA uses both primal and dual variables from an exact solver to condition the evolutionary search. DCCT is general: applicable to any (MILP, MOEA) pair — power systems, portfolio, manufacturing scheduling.

### 3. Dynamic CI Departure Scheduling
*Type 4+5 — Contextual + Synthesizing*

First freight departure-time optimizer using hourly grid carbon intensity. Supports EU (Ember 2023) and US regional profiles (EPA eGRID 2022: national, California, Texas). Same route, same mode — different departure hour → up to 37% emission difference.

---

## Quick Start

### Prerequisites

- **Python 3.14.3** (tested; 3.11+ should work)
- 8 GB RAM recommended (NSGA-III population N=84–92)

### Installation

```bash
git clone https://github.com/sthangavel/CARMA-ALGORITHM.git
cd CARMA-ALGORITHM

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

### Run Experiments

```bash
# End-to-end demo — Iberian 12-route network
python experiments/demo_carma.py

# Rotterdam European hub — 14 routes, 4 modes (truck/rail/ship/air)
python experiments/frankfurt_pharma_network.py

# Salamanca benchmark — comparison vs Sanchez-Pravos et al. [2026]
python experiments/salamanca_benchmark.py

# PIEM physics validation
python experiments/validate_piem.py

# ML ensemble training (reproduces Table 2)
python experiments/train_paper_models.py
```

---

## Repository Structure

```
CARMA-ALGORITHM/
│
├── algorithm/                       — Core CARMA library (importable package)
│   ├── carma/
│   │   ├── __init__.py              — CARMA package entry point
│   │   └── algorithm.py             — Unified 6-phase orchestrator (CARMA.run)
│   ├── physics/
│   │   └── emission_model.py        — PIEM: Physics-Informed Emission Model (Phase 1)
│   ├── ml_models/
│   │   ├── emission_predictors.py   — Base RF + XGBoost + feature engineering
│   │   └── adaptive_ensemble.py     — Segmented / Soft MoE / Stacked (Phase 2)
│   ├── optimization/
│   │   ├── carbon_milp.py           — Carbon-budget MILP + shadow price λ* (Phase 3)
│   │   ├── nsga3_optimizer.py       — DCCT-NSGA-III: CRI + CAPS + SPRD (Phase 4)
│   │   ├── dynamic_carbon_routing.py — Dynamic CI scheduling, EU+US profiles (Phase 5)
│   │   └── hybrid_ml_ga.py          — NSGA-II v2 (retained for 2-objective runs)
│   ├── data_prep/
│   │   ├── synthetic_generator.py   — Synthetic route dataset generator
│   │   ├── realistic_generator.py   — Quasi-real network generator
│   │   ├── epa_scraper.py           — EPA emission factors v1.3
│   │   └── climatiq_connector.py    — Climatiq API connector
│   └── utils/
│       └── metrics.py               — Statistical evaluation utilities
│
├── data/
│   ├── raw/                         — EPA, Climatiq, ClimateTrace source files
│   ├── processed/                   — Unified emission factors, case study results
│   └── synthetic/                   — Generated networks (50–2000 nodes) + scenarios
│
├── experiments/
│   ├── demo_carma.py                — Iberian 12-route CARMA demo
│   ├── frankfurt_pharma_network.py  — Rotterdam hub → 14 European cities (4 modes)
│   ├── salamanca_benchmark.py       — Salamanca benchmark vs Sanchez-Pravos [2026]
│   ├── validate_piem.py          — PIEM physics validation
│   └── train_paper_models.py        — ML ensemble training
│
├── paper/
│   └── CARMA_SPEC.md                — Formal spec: pseudocode, DCCT theorems, novelty
│
├── tests/                           — Unit and integration tests
├── config.py                        — Centralized configuration
└── requirements.txt                 — Python 3.14 dependencies (9 packages)
```

---

## CARMA Pipeline

```
Routes + Training data
        │
        ▼
┌─────────────────┐
│  Phase 1        │  PIEM: Grubb + COPERT + HBEFA + regen braking + weather
│  PIEM           │  → 15 physics-informed ML features per route
└────────┬────────┘
         ▼
┌─────────────────┐
│  Phase 2        │  Segmented MoE: per-segment optimal RF/XGB weights
│  ML Ensemble    │  → Calibrated CO₂e predictor (MAPE 1.44–4.5% per segment)
└────────┬────────┘
         ▼
┌─────────────────┐
│  Phase 3        │  PuLP/CBC MILP: certified optimal mode assignment
│  Carbon MILP    │  → X*_MILP (primal), λ* = shadow price (dual)  [DCCT source]
└────────┬────────┘
         ▼
┌─────────────────┐
│  Phase 4        │  DCCT-NSGA-III: CAPS seeds P₀ from X*_MILP (Thm 1)
│  DCCT-NSGA-III  │  SPRD biases ref dirs via λ* (Thm 3) → PF* (84–92 solutions)
└────────┬────────┘
         ▼
┌─────────────────┐
│  Phase 5        │  EU (Ember 2023) + US (EPA eGRID 2022) 24h CI profiles
│  Dynamic CI     │  → T* departure schedule, up to 37% saving per electric route
└────────┬────────┘
         ▼
┌─────────────────┐
│  Phase 6        │  Tchebycheff scalarization on PF*
│  Synthesis      │  → X*_pref matching user preference weights
└─────────────────┘
```

---

## Configuration

```python
from algorithm.carma import CARMA, CARMAConfig

config = CARMAConfig(
    carbon_budget_reduction_pct = 20.0,      # Phase 3: 20% emission cut
    ets_price_eur_per_tonne     = 65.0,      # EU ETS / US SCC carbon price
    ensemble_strategy           = "segmented",
    nsga3_population            = 84,        # = number of reference directions
    nsga3_partitions            = 6,         # p=6 → C(9,6)=84 dirs for M=4
    enable_dynamic_ci           = True,
    origin_country              = "ES",      # ES/DE/FR/GB/EU/US/CA/TX
    time_flexibility_hours      = 8.0,
    preference_weights          = {"cost": 0.40, "emissions": 0.40,
                                   "time": 0.10, "reliability": 0.10},
)

result = CARMA(config).run(routes, training_df=df)
result.print_summary()
```

Supported `origin_country` codes and their CI profiles:

| Code | Grid | Source |
|------|------|--------|
| `ES` | Spain — solar/wind dominant | Ember Climate 2023 |
| `DE` | Germany — coal/gas transitioning | Ember Climate 2023 |
| `FR` | France — nuclear dominant | Ember Climate 2023 |
| `GB` | UK — gas/wind mix | Ember Climate 2023 |
| `EU` | EU average (fallback) | Ember Climate 2023 |
| `US` | US national average | EPA eGRID 2022 |
| `CA` | California — solar duck curve | EPA eGRID 2022 |
| `TX` | Texas — gas + wind | EPA eGRID 2022 |

---

## Formal Specification

See [paper/CARMA_SPEC.md](paper/CARMA_SPEC.md) for the complete paper-ready algorithm specification:
- 46-line numbered pseudocode
- 7 key formulas (PIEM, MoE gating, MILP Lagrangian, Das-Dennis, DCCT framework, Dynamic CI, Tchebycheff)
- 3 DCCT theorems with proofs (Extremal Anchor, O(1) convergence, SPRD density)
- Literature-validated novelty classification (Type 3+7, Type 6+8, Type 4+5)
- Complexity and comparison tables
- 40 references across 8 thematic groups

---

## Dependencies

| Package | Version | Used for |
|---------|---------|----------|
| numpy | ≥2.4.0 | Arrays, reference directions, CAPS seeding |
| pandas | ≥3.0.0 | Route DataFrames, training data |
| scikit-learn | ≥1.8.0 | RandomForest, Ridge meta-learner |
| xgboost | ≥3.0.0 | XGBoost base learner in MoE |
| pulp | ≥3.0.0 | MILP solver (CBC backend) |
| deap | ≥1.4.0 | NSGA-III evolutionary framework |
| scipy | ≥1.17.0 | Statistical evaluation utilities |
| joblib | ≥1.4.0 | Parallel model fitting |
| matplotlib | ≥3.10.0 | Pareto front plots |
| seaborn | ≥0.13.0 | Figure styling |
| requests | ≥2.32.0 | Climatiq/EPA API connectors |

Install: `pip install -r requirements.txt`

---

## Citation

```bibtex
@article{thangavel2026carma,
  title   = {{CARMA} Unified: Certified Carbon-Aware Supply Chain Route Optimization
             via Dual-Channel {MILP}--{NSGA-III} Transfer},
  author  = {Thangavel, Sivalingam},
  year    = {2026},
  note    = {Manuscript in preparation}
}
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Acknowledgments

Data sources used in CARMA:
1. **EPA Supply Chain GHG Emission Factors** v1.3 (2024) — US emission factors
2. **EPA eGRID 2022** — US regional grid carbon intensity (US/CA/TX profiles)
3. **Ember Climate** — European Electricity Review 2024 (ES/DE/FR/GB/EU profiles)
4. **HBEFA 4.2** — Handbook Emission Factors for Road Transport, UBA Germany
5. **COPERT 5** — European Environment Agency road emission model
6. **BTS Commodity Flow Survey 2022** — US freight cost data
7. **Climatiq API** — emission factor database
