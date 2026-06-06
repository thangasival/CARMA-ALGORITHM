"""
CARMA — Carbon-Aware Routing with Multi-objective Adaptive ensemble
===================================================================

A novel algorithmic framework for carbon-aware supply chain optimization
combining six tightly integrated components into one unified pipeline.

Acronym decomposition
---------------------
  C — Carbon-budget constrained MILP (certified optimal static routing)
  A — Adaptive Mixture-of-Experts ML ensemble (context-dependent weights)
  R — Routing network optimizer (NSGA-III, 4-objective evolutionary search)
  M — Multi-objective optimization (cost, emissions, time, reliability)
  A — Adaptive Physics-Informed Emission Model v2 (Grubb + COPERT + HBEFA)

Plus temporal extension: Dynamic Carbon-Intensity scheduling (grid CI-aware
departure time optimization for electrified modes).

Citation placeholder
--------------------
  Thangavel, S. (2026). "CARMA: Carbon-Aware Routing with
  Multi-objective Adaptive ensemble for Supply Chain Optimization."
  Author: Sivalingam Thangavel <th.sivalingam@gmail.com>
  [Manuscript in preparation]

Quick start
-----------
  >>> from algorithm.carma import CARMA, CARMAConfig
  >>> config = CARMAConfig(carbon_budget_reduction_pct=20)
  >>> carma  = CARMA(config)
  >>> result = carma.run(routes, training_df=df)
  >>> result.print_summary()
"""

from .algorithm import CARMA, CARMAConfig, CARMAResult

__version__ = "1.0.0"
__author__  = "Sivalingam Thangavel"
__email__   = "th.sivalingam@gmail.com"
__all__     = ["CARMA", "CARMAConfig", "CARMAResult"]
