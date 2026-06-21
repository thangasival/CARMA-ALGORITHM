# CARMA — Marginal Abatement Cost for Intermodal Supply Chain Routing

**Carbon compliance regime classification via parametric MILP**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/downloads/)

**Paper:** *Marginal Abatement Cost as a Carbon Decision Signal in Intermodal Supply Chain Routing: A Parametric MILP Framework for Mode Shift, Allowance Purchase, and Regime Classification* — Supply Chain Analytics (Elsevier, under review)

---

## Overview

CARMA answers the question prior routing models skip: **should a logistics network shift modes or buy carbon allowances?**

The framework applies RHS-parametric MILP to the carbon-budget constraint of an intermodal routing model. By solving the integer programme at sequential budget levels and differencing the results, it recovers a finite-difference marginal abatement cost (MAC) curve — bypassing LP-relaxation duals, which are structurally zero in mixed-integer mode-assignment models. Each (network, budget) point is then classified into one of five carbon-compliance regimes by comparing the network's MAC against an observable carbon price.

---

## Five-Regime Taxonomy

| Regime | Condition | Decision |
|--------|-----------|----------|
| **R1 — Mode shift preferred** | λ̂ < 0.90π | Reconfigure logistics network |
| **R2 — Parity** | 0.90π ≤ λ̂ ≤ 1.10π | Margin-neutral; decide on strategic grounds |
| **R3 — Allowance purchase preferred** | λ̂ > 1.10π | Buy ETS allowances |
| **R4 — Co-benefit** | Carbon constraint non-binding | No carbon instrument needed |
| **R5 — Infeasible** | No feasible modal assignment exists | Network redesign required |

where λ̂(r) = [Z(r) − Z(r−Δr)] / [E(r−Δr) − E(r)] in €/kg CO₂e, and π is the observable carbon price.

---

## Key Results

### Three Network Archetypes

| Network | Type | Routes | Modes | Result at 65 €/t ETS |
|---------|------|--------|-------|----------------------|
| **Salamanca** | Rail-limited domestic | 12 | Truck / Rail | R3 — Allowance preferred (MAC 245–4,366 €/t, 3.8–67× ETS) |
| **Iberian** | Maritime-accessible | 12 | Truck / Rail / Ship | R4 — Co-benefit (77.1% emission cut, 55.7% cost saving) |
| **Frankfurt** | Hub-limited | 14 | Truck / Rail / Air | R4 → R3 → R5 (infeasible above 25% budget) |

### Within-Class Consistency (150 Generated Networks, 1,650 MILP Solves)

| Family | At 20% budget | Median MAC (binding cases) |
|--------|---------------|---------------------------|
| Rail-limited domestic (50 networks) | 54% non-binding, 46% allowance-preferred, **0% shift-preferred** | 1,398 €/t (21× ETS) |
| Maritime-accessible (50 networks) | 100% non-binding | — |
| Hub-limited (50 networks) | 52% infeasible | — |

---

## Method

### Parametric MILP

For carbon reduction target r ∈ {0, 5, 10, …, 50}%:

```
min   Σ_{r,m} c_{rm} · x_{rm}
s.t.  Σ_{r,m} ef_{rm} · x_{rm} ≤ E₀ · (1 − r/100)
      Σ_m x_{rm} = 1   ∀r
      x_{rm} ∈ {0, 1}
```

LP-relaxation duals on the carbon-budget constraint equal zero in all 33 base-archetype solves (3 networks × 11 budget levels) — an expected consequence of the integer-programme value function being non-smooth.

### Finite-Difference MAC

```
λ̂(r) = [Z(r) − Z(r−Δr)] / [E(r−Δr) − E(r)]     (€/kg CO₂e)
B*(r) = λ̂(r) × 1000                               (€/t CO₂e — for comparison with π)
```

The RHS-parametric MILP technique (Jenkins 1982) solves the integer programme at point values of the carbon-budget parameter and joins results across flat regions. The contribution is not the parametric MILP procedure itself but its application to the carbon-compliance decision: comparing B*(r) against π to classify the compliance regime.

---

## Quick Start

### Installation

```bash
git clone https://github.com/sthangavel/CARMA-ALGORITHM.git
cd CARMA-ALGORITHM
pip install -r requirements.txt
```

### Run Experiments

```bash
# Parametric MAC sweep — all three network archetypes
python experiments/parametric_abatement.py

# Budget step-size robustness (Δr = 2.5%, 5%, 10%)
python experiments/budget_step_robustness.py

# Parameter sensitivity sweep (cost rates, emission factors)
python experiments/parameter_sensitivity.py

# 150-network within-class consistency study
python experiments/generated_network_robustness.py

# Generate all paper figures
python experiments/generate_figure1.py   # Fig. 1 — framework pipeline
python experiments/generate_figures.py   # Fig. 2 — MAC curves, Fig. 3 — regime heatmaps
```

---

## Repository Structure

```
CARMA-ALGORITHM/
│
├── algorithm/
│   ├── optimization/
│   │   └── carbon_milp.py              — Parametric MILP solver (CarbonBudgetMILP)
│   └── utils/
│       └── metrics.py                  — Evaluation utilities
│
├── experiments/
│   ├── parametric_abatement.py         — Core MAC sweep (3 archetypes, 11 budget levels)
│   ├── budget_step_robustness.py       — Step-size sensitivity
│   ├── parameter_sensitivity.py        — Cost/emission factor sensitivity
│   ├── generated_network_robustness.py — 150-network within-class consistency
│   ├── generate_figure1.py             — Fig. 1: CARMA framework pipeline
│   └── generate_figures.py             — Fig. 2: MAC curves, Fig. 3: regime heatmaps
│
├── paper/
│   ├── CARMA_manuscript_v3.md          — Full manuscript (Supply Chain Analytics)
│   └── figures/
│       ├── fig1_carma_pipeline.png
│       ├── fig2_mac_curves.png
│       └── fig3_regime_heatmaps.png
│
├── config.py
└── requirements.txt
```

---

## Network Definitions

### Emission Factors (kg CO₂e / tonne-km)

| Mode | Factor | Source |
|------|--------|--------|
| Truck | 0.0762 | HBEFA 4.2 HDV Euro VI |
| Rail (Spain) | 0.0285 | Eurostat 2022 Spanish grid |
| Rail (Germany) | 0.0570 | Eurostat 2022 EU-27 average |
| Ship | 0.0110 | Eurostat 2022 short-sea |
| Air | 0.6800 | ICAO CORSIA 2022 |

### Terminal Costs (€ per shipment, mode change from truck)

| Mode | Terminal cost |
|------|--------------|
| Rail | €680 |
| Ship | €750 |
| Air | €350 |

---

## Dependencies

| Package | Used for |
|---------|----------|
| `pulp` | MILP solver (CBC backend) |
| `numpy` | Numerical arrays |
| `pandas` | Result DataFrames |
| `matplotlib` | Figure generation |

```bash
pip install pulp numpy pandas matplotlib
```

---


## License

MIT License — see [LICENSE](LICENSE) for details.
