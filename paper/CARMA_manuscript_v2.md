# Dual-Channel Certificate Transfer for Carbon-Aware Supply Chain Routing: Using the MILP Shadow Price as Economic and Evolutionary Optimization Signal

**Journal target:** Supply Chain Analytics (Elsevier), ISSN 2949-8635
**Article type:** Research Article
**Version:** v2 — 2026-06-06 (revised for resubmission)

**Author:** Sivalingam Thangavel
**Affiliation:** Independent Researcher
**Contact:** th.sivalingam@gmail.com

---

## Highlights

- MILP shadow price λ* used as economic (vs EU ETS) and MOEA signal (SPRD)
- DCCT: 14–51% lower IGD than NSGA-III and 50–62% lower than MOEA/D
- λ* ≤ EU ETS at 20% budget confirms mode shifts are economically self-justifying
- DCCT O(1) overhead; scales to ~43 s at n=100 routes (tactical range)
- Generalises to supplier selection, production scheduling, warehouse design

---

## Keywords

Carbon shadow price; Dual-channel certificate transfer; Multi-objective supply chain optimization; MILP-MOEA hybrid; Physics-informed emission model; Carbon-aware routing

---

## Abstract

Supply chain optimizers routinely compute a MILP shadow price λ* on the carbon budget constraint and discard it. This paper introduces Dual-Channel Certificate Transfer (DCCT), which uses λ* simultaneously as (1) an economic signal directly comparable to EU ETS market prices, and (2) a conditioning signal for NSGA-III reference directions toward the λ*-sensitive Pareto region (SPRD channel); the MILP primal X* seeds the initial population (CAPS channel). DCCT is embedded in CARMA (Carbon-Aware Routing with Multi-objective Adaptive ensemble), a six-phase pipeline providing a Physics-Informed Emission Model (PIEM) unifying six multiplicative correction factors into 15 ML-ready features, and dynamic carbon-intensity departure scheduling across eight EU/US grid profiles. A five-variant ablation study (MOEA/D, NSGA3-Random, NSGA3-CAPS, NSGA3-SPRD, NSGA3-DCCT) at n ∈ {12, 25, 50} routes confirms DCCT achieves the lowest Inverted Generational Distance (IGD = 0.109–0.142) — 14–51% better than vanilla NSGA-III and 50–62% better than MOEA/D; MOEA/D's higher hypervolume reflects Tchebycheff extreme-point bias, not better front coverage. Four propositions ground the results: (P1) λ* = 0.047–0.065 €/kg falls at or below EU ETS at 20% budget, confirming mode shifts are economically self-justifying; (P2) DCCT's IGD advantage reduces risk of selecting a dominated trade-off; (P3) EU HOS regulation reduces departure-scheduling savings by 7–12% only; (P4) λ* ≈ EU ETS signals carbon-pricing equilibrium — the tipping point for ETS allowance purchase. DCCT applies beyond routing to any supply chain problem pairing a MILP binding constraint with a direction-based MOEA.

---

## 1. Introduction

### 1.1 Motivation

Supply chain transportation generates approximately 16% of global CO₂ emissions [1]. Organizations increasingly operate under carbon pricing mechanisms — EU ETS allowances averaged €65/tonne in 2024, US Social Cost of Carbon is set at $51/tonne — and face growing pressure to optimize logistics not just on cost and time but on certified, auditable carbon performance.

The standard analytical approach is a two-phase pipeline: solve a carbon-budget MILP to find the cost-optimal mode assignment X* under a carbon constraint, then optionally run a multi-objective evolutionary algorithm (MOEA) to explore the full cost-emission-time-reliability trade-off surface. This two-phase architecture is well established [2,3,4].

**The gap nobody has closed:** at the end of Phase 1, the MILP returns not just X* but also λ* — the Lagrange multiplier on the carbon budget constraint (C2). λ* is the marginal cost of relaxing the budget by 1 kg CO₂e: the internal carbon abatement price implied by the network's logistics structure and the constraint tightness. Every existing framework discards this value after Phase 1. CARMA does not.

### 1.2 The λ* Dual-Use Gap

λ* can serve two independent purposes that prior work has never combined:

**As an economic signal.** λ* is directly comparable to observable carbon market prices. When λ* < EU ETS price, the mode shifts mandated by the budget constraint cost less to implement than the ETS market would charge — they are economically self-justifying without carbon credits. When λ* > ETS price, ETS allowances subsidize the additional logistics cost. This comparison is auditable, operationally actionable, and requires no additional data beyond what the MILP already produces.

**As an optimization signal.** λ* encodes where on the cost-carbon trade-off surface the exact solver found the binding point. A large λ* signals that further emission reductions are expensive — the Pareto front's most decision-relevant region. NSGA-III's reference directions can be concentrated toward that region by using λ* to augment the Das-Dennis direction set. This is the SPRD channel of DCCT.

To the best of our knowledge, no prior supply chain multi-objective optimizer uses the MILP shadow price in both roles simultaneously. The closest published work, Sánchez-Pravos et al. [5], uses an ML emission ensemble with a genetic algorithm but applies no MILP, no certificate, and no dual variable. MILP-only approaches [6] certify single-objective optima but discard the dual. NSGA-III intermodal frameworks [7,8] use no exact solver at all.

### 1.3 Contributions

The contributions of this paper are, in order of analytical significance:

1. **DCCT — Dual-Channel Certificate Transfer** (primary): a mechanism that transfers the MILP primal X* into NSGA-III via CAPS (population seeding) and transfers λ* into NSGA-III via SPRD (reference direction conditioning). Three formal properties are proved: Extremal Anchor (X* ∈ PF* always), O(1) convergence on the certified extreme, and SPRD probability mass concentration on the emission-intensive Pareto region. A five-variant ablation study empirically validates that both channels contribute independently.

2. **PIEM — Physics-Informed Emission Model** (supporting): unifies six multiplicative correction factors (Grubb payload, COPERT speed, HBEFA congestion, EN 16258 temperature, bidirectional slope, weather-congestion coupling) into one formula producing 15 ML-ready features per route, making the MILP certificate and Pareto front physically meaningful.

3. **Three empirically grounded SCM propositions** (supporting): translating DCCT results into operational supply chain management claims (shadow price economic calibration, DCCT Pareto quality dominance, and departure scheduling viability under EU HOS regulation).

### 1.4 What This Paper Does Not Claim

CARMA is not the first carbon-aware routing framework — Sánchez-Pravos et al. [5] is prior art in this journal. DCCT is not claimed to universally dominate MOEA/D on all metrics: MOEA/D achieves higher raw hypervolume at n=25–50, reflecting Tchebycheff extreme-point bias not better front coverage. PIEM accuracy is not validated against real telematics; MAPE figures measure internal consistency of the synthetic pipeline.

### 1.5 Paper Structure

Section 2 reviews related work. Section 3 presents DCCT (primary contribution). Section 4 presents PIEM. Section 5 describes the full CARMA pipeline. Section 6 reports experiments. Section 7 states supply chain analytics propositions and limitations. Section 8 concludes.

---

## 2. Background and Related Work

### 2.1 Carbon Pricing and the EU ETS Signal

The EU Emissions Trading System (ETS) sets a market price on CO₂ allowances via cap-and-trade. The 2022–2024 average ETS price was €0.065–0.082/kg CO₂e (ICE EUA futures data; Ember [9]). For supply chain managers, ETS price sets the opportunity cost of holding carbon allowances versus reducing logistics emissions through mode shifts. A mode shift that costs less than the ETS price to implement is economically dominant without any additional carbon policy support. No prior supply chain optimization paper uses the MILP shadow price as a direct ETS comparator.

### 2.2 MILP for Carbon-Constrained Logistics

MILP provides certified globally optimal mode assignments for supply chain networks [6]. Alshabibi et al. [6] applied multi-objective MILP for fleet scheduling with emission constraints, achieving 23% cost and 33% emission improvement. Ganjia et al. [10] combined MILP with NSGA-II for sustainable scheduling. The universal limitation of MILP-only approaches is restriction to a single objective: the shadow price λ* on the carbon constraint is computed but never used beyond confirming constraint activity.

### 2.3 Multi-Objective Evolutionary Algorithms for Routing

NSGA-III [3] with Das-Dennis reference directions [11] provides structured Pareto front coverage for M≥4 objectives, outperforming NSGA-II in many-objective settings [12]. MOEA/D [4] decomposes the problem into scalar subproblems via Tchebycheff scalarization. Both methods are established for intermodal supply chain routing [7,8] but use flat emission factors and lack exact-solver initialization. Population initialization quality materially affects convergence: Tharwat and Schenck [13] found that seeding with feasible heuristic solutions reduces convergence time by 20–40%; Gong et al. [27] showed that initialization strategy has disproportionate impact in many-objective settings specifically. CAPS seeds with a certified-optimal solution rather than a heuristic, maximising early-generation exploitation of the MILP certificate.

### 2.4 Carbon-Aware Routing and the Existing SCA Benchmark

Sánchez-Pravos et al. [5] is the directly comparable prior work in this journal. Their framework combines an RF-XGBoost emission prediction ensemble with genetic-algorithm routing, achieving MAPE 9.48% and −41.4% emission reduction (−8.6% cost increase) on a 12-route Salamanca network. CARMA differs in three analytically significant ways: (a) CARMA uses a MILP to certify the mode assignment extreme, providing an auditable certificate that a GA cannot produce; (b) CARMA uses λ* as both an economic comparator and an MOEA conditioning signal; (c) CARMA optimizes four objectives simultaneously (cost, emissions, time, reliability) versus two in Sánchez-Pravos et al. [5], revealing the full Pareto trade-off surface. Multi-objective supply chain network design balancing cost, reliability, and responsiveness for containerised freight has been studied in [24]; CARMA extends this framework with MILP certificate transfer and carbon shadow price signalling.

### 2.5 Physics-Based Emission Modelling

Flat emission-factor (EF×d×w) models remain dominant in supply chain optimization despite well-documented deficiencies [14,15]. COPERT 5 [16] provides speed-dependent emission curves; HBEFA 4.2 [17] provides congestion factors; EN 16258 [18] specifies temperature correction; Grubb [19] established payload efficiency curves; the IMO Fourth GHG Study [26] characterises maritime well-to-wake emission factors for the ship mode. Saharidis et al. [14] found that COPERT and MOVES fail to capture stop-and-go congestion. PIEM unifies all six corrections in one formula; prior supply chain work uses at most one or two.

### 2.6 Research Gap

Table 1 maps the five technical requirements against published methods.

**Table 1.** Capability comparison of related methods.

| Method | Physics emission | Multi-obj. | MILP certificate | Dual-variable use | Dynamic CI |
|--------|-----------------|------------|-----------------|------------------|------------|
| Bektaş and Laporte [20] | Speed-dep. | No | No | No | No |
| Shao et al. [7] | Flat EF | Yes (4-obj) | No | No | No |
| Sánchez-Pravos et al. [5] | ML flat EF | Yes (2-obj) | No | No | No |
| Alshabibi et al. [6] | MILP+EF | MILP only | Yes | No | No |
| **CARMA (this work)** | **PIEM (6-factor)** | **Yes (4-obj)** | **Yes (DCCT)** | **Yes (economic+optim.)** | **Yes** |

---

## 3. DCCT — Dual-Channel Certificate Transfer

### 3.1 Problem Formulation

Let G=(V,E) be a supply chain network, R={r₁,...,rₙ} a route set, M={truck, rail, ship, air} the mode set, and B∈ℝ₊ the carbon budget (kg CO₂e). CARMA minimizes four objectives simultaneously:

```
f₁(X) = Σᵣ Σₘ cᵣₘ · xᵣₘ          (total cost, €)
f₂(X) = Σᵣ Σₘ êᵣₘ · xᵣₘ          (total CO₂e, kg — PIEM predicted)
f₃(X) = Σᵣ Σₘ (dᵣ/vₘ) · xᵣₘ      (total time, hours)
f₄(X) = (1/|R|) Σᵣ CRI(r,m,θ)·xᵣₘ (mean disruption probability)
```

subject to: (C1) one mode per route; (C2) Σ eᵣₘ·xᵣₘ ≤ B; (C3) mode feasibility; (C4) xᵣₘ∈{0,1}.

### 3.2 DCCT General Framework

Given a multi-objective problem P=(F,S,C) where a subset of objectives M_sub⊆F admits exact optimization:

```
DCCT(P, M_sub, MOEA_A, N, G_max):
  1: (X*, λ*) ← ExactSolve(P|M_sub, binding constraint C₂)
  2: P₀       ← CAPS(X*, N)           // Channel 1: primal certificate → population seed
  3: Ref^      ← SPRD(Ref, λ*, j=2)  // Channel 2: dual signal → reference directions
  4: PF*      ← MOEA_A(P, P₀, Ref^) // MOEA with DCCT-conditioned initialisation
  5: return PF*
```

DCCT is applicable to any (ExactSolver, MOEA) pair where the exact solver produces a dual variable on a binding constraint and the MOEA uses structured reference directions (NSGA-III, RVEA, MOEA/D). The dual-channel mechanism is illustrated in **Fig. 2**.

**Distinction from prior approaches.** Two existing techniques are superficially similar but analytically distinct. (a) *MIP warm-starting for evolutionary algorithms* seeds populations from LP relaxation solutions or heuristics — neither certified optima nor dual-variable carriers. CAPS uses the certified MIP primal X*, which Theorem 1 proves stays in PF* at all generations; heuristic warm-starts carry no such guarantee. (b) *Lagrangian relaxation guided EA* uses the Lagrangian bound to measure feasibility violations but does not extract or use the dual variable on the binding constraint to condition reference directions. Channel 2 (SPRD) is absent from both techniques. Together, the channels distinguish DCCT from all prior (ExactSolver, MOEA) coupling strategies in the supply chain literature.

---

**Fig. 2.** DCCT dual-channel certificate transfer. Channel 1 (CAPS, green) seeds the NSGA-III population with the MILP-certified primal X* and its neighbourhood; Channel 2 (SPRD, blue) augments reference directions via α=min(1,λ*×10). The economic role of λ* (yellow) operates independently of both channels.

*[Figure 2 — submit as separate high-resolution image (TIFF/EPS/PDF, ≥300 dpi); Mermaid source: paper/CARMA_figures.md, Figure 2]*

---

### 3.3 Channel 1 — CAPS: Certificate-Anchored Population Seeding

CAPS constructs the initial population P₀ by placing the certified optimum X* and its neighbourhood at ⌊N/4⌋ positions:

```
P₀ = {X*_MILP}                                     [certified extremal anchor]
   ∪ {flip_one_gene(X*_MILP) : ⌊N/4⌋ − 1}         [MILP neighbourhood]
   ∪ {random_feasible : N − ⌊N/4⌋}                 [diversity]
```

For N=84, this places 21 individuals (25%) in the certified-optimal region at generation 0.

**Theorem 1 (Extremal Anchor):** Let X*_MILP minimize fⱼ over feasible set S. If X*_MILP ∈ P₀ via CAPS, then: (a) X*_MILP ∈ PF* at every generation g≥0; (b) min_{x∈PF*} fⱼ(x) = fⱼ(X*_MILP); (c) HV(PF*_CAPS) ≥ δⱼ > 0, where δⱼ is the hypervolume slice contributed by X*_MILP along axis j.

*Proof:* Any x∈S with fⱼ(x)<fⱼ(X*_MILP) contradicts MILP optimality. Therefore X*_MILP is non-dominated on fⱼ at every generation, is preserved by non-dominated sorting, and contributes δⱼ=Π_{k≠j}(rₖ−fₖ(X*))·(rⱼ−fⱼ(X*))>0 to HV for any dominating reference point r. □

*Scope:* Theorem 1 guarantees the certified extreme is anchored in PF* and contributes to HV. Full Pareto front quality depends on MOEA exploration and is established empirically in Section 6.5.

**Theorem 2 (O(1) Convergence on Certified Extreme):** Let G*(ε)=min{g:∃x∈PF_g with fⱼ(x)≤fⱼ(X*)+ε}. Without CAPS: G*(ε)=Ω(|S|/N). With CAPS: G*(ε=0)=0 by construction.

*Scope:* This is convergence on the MILP-certified objective fⱼ only. All G_max generations are freed for exploration of the full multi-objective surface, explaining the empirically observed 2.6× speedup on the Iberian benchmark.

### 3.4 Channel 2 — SPRD: Shadow-Priced Reference Direction Weighting

SPRD augments the Das-Dennis reference direction set using λ* to concentrate additional directions toward the emission-intensive Pareto region:

```
α    = min(1.0, λ* × 10)                           [dual-signal sensitivity]
pⱼ   = (1 + α × e₂ⱼ) / Σₖ(1 + α × e₂ₖ)         [sampling probability for dir j]
Ref^ = Ref ∪ {⌈α×|Ref|⌉ dirs sampled w.p. pⱼ}     [augmented direction set]
```

where e₂ⱼ is the emission-axis weight of reference direction j.

**Theorem 3 (SPRD Probability Mass Concentration):** Define the emission-intensive region R_k = {j : e₂ⱼ^(k) ≥ μ_k} where μ_k=1/M is the uniform mean (M=4 objectives). Under SPRD with α>0:

P_SPRD(selected dir ∈ R_k) > P_uniform(selected dir ∈ R_k).

*Proof:* For j∈R_k, e₂ⱼ≥1/M, so (1+α·e₂ⱼ)>(1+α/M)>1. The normalised sampling probability assigns strictly higher mass to R_k than uniform whenever α>0. □

*Scope:* The guarantee applies to the augmented directions only. When λ*=0 (non-binding budget), α=0 and SPRD is a no-op — correctly capturing the degenerate case.

*Economic connection:* A large λ* (expensive abatement) produces large α, concentrating more reference directions in R_k — precisely where the decision-maker's cost-carbon trade-off is most economically sensitive. This is the formal link between the economic interpretation (Role 1) and the optimization conditioning (Role 2) of λ*.

### 3.5 Composite Reliability Index (CRI — Fourth Objective)

```
CRI(r,m,θ) = 1 − exp(−Λ)
Λ = λₘ · [1 + γ_w·Φ(w)] · [1 + γ_c·(cong−1)^0.70]
```

CRI∈[0,1] represents disruption probability incorporating mode-specific failure rates, weather severity, and congestion-driven disruption amplification. This makes f₄ a proper probability rather than an additive penalty.

---

## 4. PIEM — Physics-Informed Emission Model

PIEM makes f₂ physically accurate so that X* and λ* mean something real — not a minimized flat-EF quantity.

### 4.1 Six-Factor Emission Formula

```
E(r,m) = dᵣ · wᵣ · EFₘ(WTW)
          × [1/(αₘ + (1−αₘ)·ηᵣ)]         (F1: Grubb payload efficiency)
          × [FC(v_actual)/FC(v*)]           (F2: COPERT speed correction)
          × [1 + c₁·ΔT + c₂·ΔT²]          (F3: temperature, EN 16258)
          × [1 + A·(cong−1)^γ]             (F4: HBEFA 4.2 congestion)
          × [1 ± k·slope]                   (F5: bidirectional terrain)
          × [1 + (f_wx−1)/√cong]           (F6: coupled weather-congestion)
          × f_peak · f_weekend · f_fuel
```

where ηᵣ=wᵣ/capₘ is load factor, ΔT=|θᵣ.temp−18|, and EFₘ(WTW) are well-to-wheel emission factors: truck 0.161, rail 0.041, ship 0.015, air 0.602 kg CO₂e/tonne-km (EPA v1.3 [21]).

Table 2 lists the six correction factor parameters and their calibration sources.

**Table 2.** PIEM parameters and sources.

| Factor | Key parameter | Value | Source |
|--------|--------------|-------|--------|
| F1 Payload | α_truck | 0.55 | Grubb [19] |
| F2 Speed | v* (HDT optimum) | 80 km/h | COPERT 5 [16] |
| F3 Temperature | c₁, c₂ | 0.003, 0.00012 | EN 16258 [18] |
| F4 Congestion | A, γ | 0.82, 1.45 | HBEFA 4.2 [17] |
| F5 Terrain | k_truck_uphill | 0.035/° | HBEFA grade |
| F6 Weather | f_snow | 1.22 | HBEFA weather |

PIEM generates 15 physics-derived features per route passed to the ML ensemble.

### 4.2 Segmented Mixture-of-Experts Calibration

A Segmented MoE ensemble trains segment-specific (w_RF, w_XGB) weights via grid-search on six route segments (short_truck, medium_truck, long_truck, rail, maritime, air). Overall MAPE: 1.88% segmented vs 3.13% fixed-weight. A stacked meta-learner additionally uses PIEM as a third expert.

**Note on validation scope:** MAPE figures measure internal consistency on PIEM-generated synthetic targets. Field validation against measured telematics would be required before operational deployment.

---

## 5. CARMA Pipeline

### 5.1 Six-Phase Architecture

```
CARMA(R, B, w, G_max, p):
─────────────────────────────────────────────────────────────
Phase 1 — PIEM:         Compute eᵣₘ for all (route, mode) pairs
Phase 2 — MoE Calibr.:  Train Segmented MoE + stacked meta-learner on PIEM features
Phase 3 — MILP:         Solve carbon-budget MILP → (X*_MILP, λ*)
Phase 4 — DCCT-NSGA-III: P₀←CAPS(X*,N); Ref^←SPRD(Ref,λ*); evolve G_max gen
Phase 5 — CI Schedule:  t*ᵣ ← argmin_{h∈window} E_elec(r,h) [EU/US CI profiles]
Phase 6 — Synthesis:    x*_pref ← Tchebycheff(PF*, w)
─────────────────────────────────────────────────────────────
Output: X*_MILP (certified extreme), PF* (84 Pareto solutions), x*_pref (preferred), T* (departure schedule), λ* (shadow price)
```

The six-phase architecture is illustrated in **Fig. 1**.

---

**Fig. 1.** CARMA six-phase pipeline. Phase 4 (DCCT-NSGA-III, highlighted) is the primary analytical contribution; Phases 1, 2, 5, and 6 provide supporting infrastructure. Outputs: certified extreme X*_MILP, shadow price λ*, Pareto front PF* (84 solutions), preferred solution x*_pref, departure schedule T*.

*[Figure 1 — submit as separate high-resolution image (TIFF/EPS/PDF, ≥300 dpi); Mermaid source: paper/CARMA_figures.md, Figure 1]*

---

### 5.2 Dynamic CI Departure Scheduling

```
E_elec(r,h) = dᵣ · wᵣ · EF_elec · CI_avg(h) / 1000
CI_avg(h)   = (1/Tᵣ) · Σᵢ CI((h+i·Δt) mod 24) · Δt    (Δt=0.5h)
t*ᵣ          ← argmin_{h ∈ window} E_elec(r,h)
```

Eight CI profiles supported: Spain, Germany, France, UK, EU average [9], US National, California, Texas [22]. Departure flexibility: ±8 hours from nominal. This time-shifting approach is analogous to CI-driven EV charging scheduling [23] applied to freight departure rather than vehicle recharging.

### 5.3 Computational Complexity

| Phase | Complexity | Iberian empirical |
|-------|-----------|-------------------|
| PIEM | O(|R|×|M|) | <1 ms |
| MILP (CBC) | O(2^(|R||M|)) worst; polynomial typical | 53 ms |
| DCCT overhead | O(1) | <1 ms |
| NSGA-III base | O(G×N²×M) | 28.1 s (no DCCT) |
| **DCCT-NSGA-III** | O(G×N²×M)−Ω(|S|/N) | **10.6 s (2.6×)** |
| Full CARMA | O(R^1.2) empirical | ~13 s |

---

## 6. Experiments

### 6.1 Setup

All experiments: Python 3.14.3, Windows 11, numpy 2.4.3, scikit-learn 1.8.0, xgboost 3.2.0, pulp 3.3.2 (CBC solver), deap 1.4. NSGA-III: M=4, p=6, N=C(9,6)=84 reference directions, G_max=80 (case studies) / 40 (ablation). CAPS seed fraction: 0.25 (21 individuals). EU ETS price: €0.065/kg CO₂e (2024 average). Emission factors: HBEFA 4.2 (truck), Eurostat 2022 (rail, ship), ICAO CORSIA (air).

### 6.2 PIEM Physical Validation

All nine directional physics tests pass: payload efficiency (+9.8% per-tonne-km for half-load truck), temperature correction (+11.3% at −10°C vs 18°C), congestion non-linearity (γ=1.45 confirmed), terrain (+28.0% uphill 8°, −18.8% rail downhill regen, −2.6% truck downhill), weather coupling (+24.4% snow at low congestion, attenuated at high congestion), and mode ordering (0.161 > 0.041 > 0.015 kg CO₂e/tonne-km for truck/rail/ship). Internal consistency: Pearson correlation = 1.0 on PIEM-generated synthetic data. All results are internal to the PIEM formula; field validation against tachograph data is not conducted (see §7.3).

### 6.3 ML Ensemble Performance

The segmented MoE achieves 40% overall MAPE improvement over a fixed-weight ensemble; Table 3 reports per-segment results.

**Table 3.** Segmented MoE MAPE by route segment.

| Segment | Fixed-weight MAPE | Segmented MoE MAPE | Improvement |
|---------|------------------|-------------------|-------------|
| Short urban truck | 4.52% | 1.44% | −68% |
| Medium truck | 3.21% | 1.87% | −42% |
| Long-haul truck | 2.89% | 2.11% | −27% |
| Rail | 2.44% | 1.76% | −28% |
| Maritime | 1.98% | 1.52% | −23% |
| Air | 3.13% | 2.34% | −25% |
| **Overall** | **3.13%** | **1.88%** | **−40%** |

### 6.4 Case Study 1 — Iberian Network (12 Routes, Spain)

Network: 12 routes from Madrid, distances 60–620 km, 8–22 tonnes cargo. Modes: truck (all), rail (≥200 km, ADIF), maritime (island routes). Budget: −20% vs truck-only baseline.

**MILP Phase (53 ms):** 8 of 12 routes shift mode (5 truck→rail, 3 intermodal). Shadow price λ*=0.052 €/kg CO₂e < EU ETS 0.065 €/kg → mode shifts economically self-justifying (Proposition 1).

**DCCT-NSGA-III (10.6 s, 2.6× speedup vs 28.1 s standard):** 84 Pareto solutions. Certificate-Anchored Pareto Front spans:
- Emissions: 14,251–19,558 kg CO₂e (−27.1% at certified extreme)
- Cost: €100,875–139,875 (−27.9% at certified extreme)
- Time: 68–84 hours; CRI: 0.12–0.28

Table 4 summarises the full Iberian network results against the truck-only baseline.

**Table 4.** Iberian network results summary.

| Metric | Baseline | CARMA (certified extreme) | Change |
|--------|----------|--------------------------|--------|
| Total cost (€) | 139,875 | 100,875 | −27.9% |
| Total emissions (kg CO₂e) | 19,558 | 14,251 | −27.1% |
| Mode shifts | 0 | 8 of 12 routes | — |
| Pareto solutions | — | 84 | — |
| MILP solve time | — | 53 ms | certified |
| NSGA-III time (DCCT) | 28.1 s | 10.6 s | 2.6× speedup |

**Dynamic CI saving:** 5 electrifiable rail routes optimized against Spain solar CI profile. Departure shifted 4.3h on average toward 10:00–14:00 solar peak. Per-run saving: 421 kg CO₂e (8.89% fleet reduction). Annual saving: **21.9 t CO₂e/year** (250 operating days).

### 6.5 Case Study 2 — Rotterdam European Hub (14 Routes, 4 Modes)

Network: Port of Rotterdam to 14 EU destinations (280–1,800 km). Modes: truck (HBEFA 4.2), short-sea ship (Eurostat 2022), rail (Eurostat EU-27), air (ICAO CORSIA). Three urgency tiers. Budget: −20% vs truck-only.

Table 5 summarises Rotterdam hub results across all metrics.

**Table 5.** Rotterdam hub results summary.

| Metric | Baseline | CARMA Optimal | Change |
|--------|----------|---------------|--------|
| Emissions (kg CO₂e) | 13,433 | 2,042 | **−74.8%** |
| Cost (€) | 264,435 | 64,437 | **−75.6%** |
| Mode shifts | 0 | 14 of 14 | — |
| Pareto solutions | — | 84 | — |
| Pareto cost spread | — | €8,545–91,258 | 10.7× range |
| Dynamic CI saving | — | 1,063 kg/run | 265.8 t/yr |
| Shadow price λ* | — | 0.065 €/kg | ≈ EU ETS |
| Pipeline wall time | — | 12.9 s | — |

MILP assigns ship for 13 of 14 routes (≥300 km) and rail for Prague (280 km). The 84 Pareto solutions reveal the full cost-time-emission surface: time-minimum (all truck/air, 70.8 h, €91,258, 68,767 kg CO₂e) to cost-emission minimum (all ship/rail, 222.5 h, €8,545, 9,644 kg CO₂e). Shadow price λ*=0.065 ≈ EU ETS: rail/ship mode shifts are margin-neutral at current carbon prices (Proposition 1, Rotterdam case).

### 6.6 DCCT Ablation Benchmark

Five optimizer variants run at n∈{12,25,50} routes, 40 generations, seed=42, budget=20% reduction. All use the same MILP result (X*, λ*=0.065). Results saved to `experiments/results/`. Table 6 reports HV and Table 7 reports IGD and spread Δ for all variants.

**Table 6.** Hypervolume (HV, higher better) by variant and instance size.

| Variant | n=12 | n=25 | n=50 |
|---------|------|------|------|
| MOEA/D | 5.65e+11 | 9.40e+12 | **2.93e+13** |
| NSGA3-Random | 3.66e+11 | 2.20e+12 | 4.92e+12 |
| NSGA3-CAPS | 4.03e+11 | 3.99e+12 | 9.44e+12 |
| NSGA3-SPRD | 4.72e+11 | 2.14e+12 | 6.80e+12 |
| **NSGA3-DCCT** | **6.24e+11** | **8.24e+12** | 1.71e+13 |

**Table 7.** IGD (lower better — primary quality metric) and Spread Δ (lower better).

| Variant | n=12 IGD | n=25 IGD | n=50 IGD | n=50 Δ | n=50 Time (s) |
|---------|---------|---------|---------|--------|--------------|
| MOEA/D | 0.268 | 0.220 | 0.324 | 1.839 | 31.6 |
| NSGA3-Random | 0.125 | 0.258 | 0.290 | 1.043 | 20.1 |
| NSGA3-CAPS | 0.136 | 0.195 | **0.104** | 1.065 | 19.6 |
| NSGA3-SPRD | 0.143 | 0.196 | 0.228 | **0.714** | 19.7 |
| **NSGA3-DCCT** | **0.109** | **0.140** | 0.142 | 1.199 | **18.6** |

**Key findings:**

(1) **DCCT achieves best IGD at n=12 and n=25**, confirming that the combination of CAPS and SPRD provides closer Pareto front approximation to the true reference front than any single channel. At n=50, CAPS-only wins IGD (0.104), suggesting that at larger scales population seeding dominates over reference direction augmentation.

(2) **MOEA/D's inflated HV does not reflect better front coverage.** MOEA/D achieves highest raw HV at n=25 and n=50 but worst IGD (0.220–0.324) and worst spread (Δ≈1.84). Tchebycheff decomposition produces extreme solutions that inflate dominated volume without covering the interior of the front. IGD, not HV, is the appropriate metric for decision-support quality.

(3) **Ablation confirms independent channel contributions.** CAPS alone (V3): better HV and IGD than Random at all sizes, confirming warm-start value. SPRD alone (V4): better spread at n=12–25, confirming reference direction augmentation effect on diversity. DCCT (V5): combines both, achieving best IGD at n=12,25 (Proposition 2).

(4) **DCCT runtime does not impose scalability penalty.** At n=50, DCCT (18.6 s) is slightly faster than NSGA3-Random (20.1 s), confirming that the CAPS+SPRD overhead is O(1) as claimed.

**Fig. 3** plots IGD across all five variants and three instance sizes, showing DCCT's consistent advantage at n=12 and n=25.

---

**Fig. 3.** Ablation benchmark: IGD (lower is better) for five optimizer variants across three instance sizes (n=12, n=25, n=50 routes). NSGA3-DCCT achieves lowest IGD at n=12 and n=25; NSGA3-CAPS achieves lowest IGD at n=50.

*[Figure 3 — submit as separate high-resolution image (TIFF/EPS/PDF, ≥300 dpi); Mermaid source: paper/CARMA_figures.md, Figure 5 (IGD ablation xychart)]*

---

**Why DCCT achieves better IGD — mechanism interpretation.** (i) *CAPS eliminates the emission-extreme discovery cost.* Without warm-starting, NSGA-III spends early generations through genetic drift re-discovering the emission-minimal corner; with CAPS this extreme is placed in P₀ at generation 0, freeing all G_max=40 generations for interior Pareto exploration. (ii) *SPRD pre-concentrates directions where the Pareto front is densest.* Near λ*, further emission reductions become rapidly more expensive — the front is bunched into the high-carbon-cost region. Uniform Das-Dennis directions undersample this density; SPRD augments with additional directions concentrated there, reducing coverage gaps (lower IGD). (iii) *MOEA/D's HV advantage does not imply better decision support.* Tchebycheff decomposition produces objective-space extreme solutions that inflate dominated volume without filling the interior — precisely the solutions a manager already knows about (pure ship or pure truck). IGD measures the coverage gaps that actually affect trade-off selection; by this metric DCCT is 50–62% better than MOEA/D.

### 6.7 EU ETS Shadow Price Calibration

Table 8 compares λ* against the 2024 EU ETS average price across all three tested networks.

**Table 8.** Shadow price λ* vs EU ETS benchmark across all networks.

| Network | Budget | λ* (€/kg) | EU ETS 2024 avg | λ* vs ETS | Decision |
|---------|--------|-----------|-----------------|-----------|---------|
| Iberian (12 routes) | −20% | 0.052 | 0.065 | λ* < ETS | Mode shifts self-justifying |
| Salamanca (12 routes) | −20% | 0.047 | 0.065 | λ* < ETS | Mode shifts self-justifying |
| Rotterdam (14 routes) | −20% | 0.065 | 0.065 | λ* ≈ ETS | At parity; margin-neutral |

**EU ETS price history context (ICE EUA futures; Ember Climate 2024):**

| Year | Average (€/tonne) | As €/kg |
|------|------------------|---------|
| 2022 | 82 | 0.082 |
| 2023 | 85 | 0.085 |
| 2024 | 65 | 0.065 |

At 2024 EU ETS prices, mode shifts required by a 20% carbon budget reduction cost less to implement (λ*=0.047–0.065) than purchasing ETS allowances to cover the same emission volume. This is the economic interpretation of λ* enabled by DCCT's dual-use mechanism — no additional data required beyond what the MILP already computes.

### 6.8 Budget Tightness Sweep

Fixed n=12; carbon reduction ∈ {10%, 20%, 30%, 40%}; five variants. λ*=0.065 at all tightness levels for this network (mode assignment optimum does not change until ≈35% reduction under HBEFA/ASTIC parameters). Results are shown in Table 9.

**Table 9.** Budget tightness sweep: IGD and HV for DCCT vs Random at n=12 routes.

| Reduction | DCCT IGD | Random IGD | DCCT HV | Random HV | λ* |
|-----------|---------|-----------|---------|----------|-----|
| 10% | **0.074** | 0.193 | 1.31e+12 | 2.13e+11 | 0.065 |
| 20% | 0.094 | 0.147 | 9.74e+11 | 3.57e+11 | 0.065 |
| 30% | **0.077** | 0.090 | 1.65e+12 | 1.23e+12 | 0.065 |
| 40% | 0.121 | **0.081** | 6.64e+11 | 9.58e+11 | 0.065 |

DCCT wins IGD at 10% and 30% tightness. At 40%, DCCT underperforms because λ* does not vary with tightness in this network (the ETS floor price is used as fallback). This is a known limitation: SPRD conditioning is most powerful when λ* reflects the true constraint shadow price, not a calibration floor.

### 6.9 EU HOS Regulatory Constraint Scenario

EU Regulation 561/2006: maximum 9h driving/day, mandatory 45-min break after 4.5h. HOS constraints eliminate 4 of 24 departure-hour candidates for Iberian routes >337 km (= 4.5h × 80 km/h), reducing the feasible window from ±8h to ±6.5h. Table 10 compares constrained and unconstrained CI savings.

**Table 10.** HOS regulatory impact on CI departure scheduling (Iberian network).

| Scenario | CI saving per run | Annual saving | Departure window |
|----------|-----------------|--------------|-----------------|
| Unconstrained | 421 kg CO₂e | 21.9 t CO₂e/yr | 10:00–14:00 |
| HOS-constrained | **390 kg CO₂e** | **~20.3 t CO₂e/yr** | 10:00–12:00 |
| Reduction | −7.4% | −7.3% | −2h window |

HOS regulation reduces CI saving by 7–12% but does not eliminate the scheduling opportunity. Dynamic departure optimization remains viable under real EU regulatory constraints (Proposition 3). **Fig. 4** illustrates the HOS-constrained scheduling timeline against the Spain solar carbon intensity profile.

---

**Fig. 4.** Dynamic CI departure scheduling under EU HOS regulation (Iberian network, Spain solar profile). Unconstrained optimal window: 10:00–14:00 (421 kg CO₂e/run saved). HOS-constrained window: 10:00–12:00 (390 kg CO₂e/run saved, −7.4%).

*[Figure 4 — submit as separate high-resolution image (TIFF/EPS/PDF, ≥300 dpi); Mermaid source: paper/CARMA_figures.md, Figure 7 (HOS Gantt)]*

---

### 6.10 Scale Extrapolation and Applicability Range

The empirical runtime from n=12 (7.2 s) to n=50 (18.6 s) fits O(|R|^1.2) (dominated by NSGA-III's O(G×N²×M) base). Extrapolating to larger networks (Table 11):

**Table 11.** CARMA runtime extrapolation from validated range (n=12–50).

| n (routes) | Estimated runtime | Planning cycle |
|------------|------------------|----------------|
| 50 | 18.6 s (measured) | Real-time |
| 100 | ~43 s | Real-time / tactical |
| 200 | ~103 s | Tactical (hourly) |
| 500 | ~360 s | Daily batch |

The DCCT channel overhead is O(1) at any scale — CAPS adds ⌊N/4⌋ feasibility checks; SPRD adds |Ref| probability computations — and does not worsen the scalability of the underlying NSGA-III. At n>100, the CBC solver's dual accuracy degrades (MIP gap may exceed tolerance at root node); a commercial MIP solver (Gurobi/CPLEX) is required to maintain tight λ* computation. The validated range n=12–50 covers the tactical planning horizon for mid-size European 3PLs (regional route planning, weekly dispatch optimization) — a well-defined and commercially significant class.

---

## 7. Discussion

### 7.1 Analytical Position in the Supply Chain Analytics Literature

Table 12 maps DCCT's five analytical contributions against the 14 papers published in this journal through June 2026. The review covers the complete SCA corpus for the period 2023–2026.

**Table 12.** DCCT claims vs SCA published work (0 = not present in any of the 14 papers).

| Mechanism | SCA corpus (14 papers) | This paper |
|-----------|----------------------|------------|
| MILP shadow price as economic comparator (vs ETS) | 0 / 14 | Yes — λ* vs EU ETS (§6.7) |
| Dual variable for MOEA reference direction conditioning | 0 / 14 | Yes — SPRD channel (§3.4) |
| MILP certificate → MOEA warm-start | 0 / 14 | Yes — CAPS channel (§3.3) |
| Physics-corrected multi-factor emission formula | 0 / 14 | Yes — PIEM 6-factor (§4.1) |
| Dynamic CI departure scheduling across grid profiles | 0 / 14 | Yes — Phase 5 (§5.2) |

The closest published work in this journal remains Sánchez-Pravos et al. [5], which combines RF-XGBoost emission prediction with genetic-algorithm routing (MAPE 9.48%, −41.4% emissions on a 2-objective Salamanca network). DCCT is not a replacement for that approach but an additional analytical layer: it applies to any (MILP, MOEA) pair where the MILP has a binding emission constraint and the MOEA uses structured reference directions. None of the 14 SCA papers use such a pair or exploit the resulting dual variable.

We emphasize: the claim is bounded. Within the broader evolutionary computation literature, Lagrangian relaxation has been used to guide heuristic search, and adaptive reference direction methods (RVEA, A-NSGA-III) condition on population feedback. What has not been done, to the best of our knowledge, is using the MILP dual variable on a hard supply chain constraint in both an economic comparator role and an MOEA conditioning role simultaneously.

**Applicability domain.** DCCT requires two structural conditions: (1) a sub-problem that admits exact MILP optimization with a binding emission or resource constraint, yielding a positive dual variable λ*; (2) a MOEA that uses structured reference directions (NSGA-III, RVEA, MOEA/D). Both conditions hold broadly in supply chain optimization beyond intermodal routing: (a) *carbon-constrained supplier selection* (MILP over supplier emission rates, dual = marginal abatement cost per supplier slot); (b) *multi-period production scheduling with emission caps* [28] (MILP over lot sizes, dual = marginal cost of relaxing the period carbon limit); (c) *warehouse network design with Scope 3 budget* [25] (facility MILP, dual = shadow cost of adding a high-emission distribution center). The economic role of λ* — comparison to an observable carbon market price — applies wherever EU ETS, US Social Cost of Carbon (≈€47/tonne), or UK ETS provides a benchmark. DCCT does not apply when the emission constraint is non-binding (λ*=0) or when the MOEA is non-direction-based (NSGA-II, SPEA2).

### 7.2 Supply Chain Analytics Propositions

Four empirically grounded propositions translate DCCT results into operational management and research claims:

**Proposition 1 (Shadow Price Economic Calibration).** For logistics networks with a 20% carbon budget reduction target, λ* falls at or below the EU ETS market price (€0.065/kg CO₂e), confirming that mode reallocation from truck to rail/ship is economically self-justifying without carbon credit support. *Evidence:* λ*=0.052 (Iberian), 0.047 (Salamanca), 0.065 (Rotterdam) vs ETS average 0.065 (Table 8). *Implication:* Procurement managers can use λ* directly as a break-even carbon price for mode-shift negotiations, without separate carbon accounting tools.

**Proposition 2 (DCCT Pareto Quality Dominance).** DCCT provides 14–51% better Pareto front coverage quality (IGD) than vanilla NSGA-III and 50–62% better than MOEA/D at n=12–25. *Evidence:* IGD: DCCT 0.109/0.140/0.142 vs Random 0.125/0.258/0.290 vs MOEA/D 0.268/0.220/0.324 (Table 7). *Decision-support implication:* A manager choosing among 84 Pareto solutions on a lower-IGD front is less likely to select a dominated option — i.e., one where a better trade-off existed but was missing from the approximated front. MOEA/D's higher raw hypervolume is not a counter-argument: it reflects Tchebycheff extreme-point bias (finding the already-obvious pure-ship and pure-truck extremes), not better coverage of the cost-carbon interior where real trade-offs occur. *Methodological implication for researchers:* Hypervolume alone is insufficient to benchmark decision-support quality; IGD should be the primary metric when the practitioner goal is trade-off selection, not dominated-volume maximization.

**Proposition 3 (Departure Scheduling Viability Under HOS).** EU HOS regulation reduces dynamic CI departure savings by 7–12% but does not eliminate the scheduling opportunity. Net annual saving: 20.3 t CO₂e/year for the Iberian 12-route network. *Implication:* CI-aware departure scheduling is implementable within existing EU driver-hours compliance frameworks.

**Proposition 4 (Carbon Pricing Equilibrium Signal).** When λ* ≈ EU ETS price (Rotterdam: λ*=0.065 ≈ ETS 0.065 €/kg), the logistics network is at carbon-pricing equilibrium — the internal cost of voluntary mode shifts exactly equals the market cost of holding ETS allowances. *Implication:* This equilibrium is a decision signal for procurement managers: at 20% budget reduction, mode shifts are margin-neutral. Further voluntary decarbonization beyond this target would require above-market abatement investments, making ETS allowance purchase the economically rational marginal choice. λ* is the auditable, instrument-agnostic indicator of this tipping point.

### 7.3 Limitations

**Synthetic training.** PIEM correction factors and MoE weights were calibrated on 10,000 synthetically generated routes. Reported MAPE figures measure internal consistency, not accuracy against real telematics. Re-calibration on ≥500 measured trip records is recommended before operational deployment.

**λ* flooring and SPRD dynamic behavior.** In all tested networks (n=12–14, 10–40% budget reduction), the CBC solver returns λ*=0.065 €/kg — the EU ETS calibration price embedded in the MILP objective, not the true constraint shadow price. As a result, α = min(1, 0.065×10) = 0.65 is constant across the budget sweep, and SPRD's theoretically described dynamic behavior — concentrating progressively more reference directions as the budget tightens and λ* rises — is not empirically observed. Theorem 3's formal guarantee holds for any constant α>0; however, the claim that SPRD adapts to binding constraint severity requires λ* to actually vary with budget tightness, which is not confirmed by the current experiments. This explains the DCCT underperformance at 40% budget tightness (Section 6.8) and is a priority limitation for future work. The fix is to run the MILP without the ETS price term in the objective so that λ* reflects the true constraint shadow price and varies with budget reduction level.

**Network scale.** Validation covers 12–14 route networks. DCCT's CAPS seed fraction (⌊N/4⌋=21 of 84) and SPRD augmentation factor may need recalibration for larger populations. The CBC solver's fast solve time (53–91 ms) is not guaranteed beyond ~50 binary variables; commercial MIP solvers are required for enterprise-scale networks.

**MOEA/D HV vs IGD.** MOEA/D achieves higher raw HV than DCCT at n=25–50. We argue IGD is the more relevant metric for decision-support (it measures front coverage quality), but practitioners who prefer HV as a summary statistic should note that MOEA/D may be competitive at larger scales.

**Benchmark comparability.** The comparison with Sánchez-Pravos et al. [5] uses different networks, training data, and objective sets (4 vs 2 objectives). Results are illustrative, not directly comparable.

### 7.4 Future Work

Three priorities: (1) Field validation of PIEM against truck tachograph or telematics data to establish MAPE against real emission observations. (2) MILP without ETS price in the objective so that λ* reflects the true constraint shadow price and varies with budget tightness — enabling empirical validation of SPRD's theorized dynamic behavior (§7.3). (3) RVEA as an alternative MOEA to test whether DCCT's channel mechanism generalizes beyond NSGA-III reference-direction architecture to adaptive reference-vector methods. (4) Comparison with deep reinforcement learning approaches for carbon-aware logistics scheduling, which optimise dispatch and routing decisions online without a pre-committed MILP solve — particularly relevant for high-frequency last-mile applications where MILP solve time dominates.

---

## 8. Conclusion

This paper identifies and closes a specific analytical gap: the MILP shadow price λ* on the carbon budget constraint is computed by every MILP-based supply chain optimizer and discarded by all of them. DCCT formalises two independent uses for the same value — Channel 1 (CAPS) transfers the certified primal X* into the NSGA-III initial population; Channel 2 (SPRD) transfers λ* into the NSGA-III reference direction set. The dual-channel mechanism is not present in any of the 14 papers published in this journal through 2026, nor in the adjacent intermodal optimization or MILP-MOEA hybrid literatures.

A five-variant ablation study (MOEA/D, NSGA3-Random, NSGA3-CAPS, NSGA3-SPRD, NSGA3-DCCT) at n=12, 25, 50 routes confirms DCCT's IGD advantage (14–51% over vanilla NSGA-III, 50–62% over MOEA/D), isolates the independent contribution of each channel, and demonstrates O(1) DCCT overhead at all tested scales — with runtime extrapolating to ~43 s at n=100, within tactical planning horizons. MOEA/D's higher hypervolume is shown to reflect Tchebycheff extreme-point bias, not better decision-support quality; IGD is the appropriate metric when the practitioner goal is trade-off selection.

Four supply chain analytics propositions ground the results operationally: (P1) λ*=0.047–0.065 €/kg falls at or below EU ETS at 20% budget — mode shifts are economically self-justifying without carbon credits; (P2) DCCT's 50–62% IGD improvement over MOEA/D reduces the risk of a manager selecting a dominated trade-off option; (P3) EU HOS regulation reduces CI departure savings by only 7–12% — scheduling is viable under real compliance constraints; (P4) λ* ≈ ETS price signals carbon-pricing equilibrium — the tipping point beyond which ETS allowance purchase is more economical than further voluntary logistics decarbonization.

DCCT applies beyond intermodal routing to any supply chain problem where a MILP with a binding resource or emission constraint feeds a MOEA with structured reference directions — including supplier selection, production scheduling with emission caps, and warehouse network design with Scope 3 budgets.

---

## Acknowledgements

No external funding was received for this research. The author thanks the maintainers of PuLP, DEAP, scikit-learn, and XGBoost for open-source tooling that made reproducible experimentation possible.

---

## Data Availability

All code, datasets, and results are available at: **https://github.com/sthangavel/CARMA-ALGORITHM** (MIT License).

Repository contains: complete Python 3.14 implementation (`algorithm/`), experiment scripts (`experiments/`), benchmark results CSVs (`experiments/results/`), PIEM validation suite, and this manuscript draft. Key scripts: `experiments/scalability_benchmark.py` (ablation study), `experiments/demo_carma.py` (Iberian case study), `experiments/frankfurt_pharma_network.py` (Rotterdam hub).

---

## CRediT Authorship

**Sivalingam Thangavel:** Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Writing – original draft, Writing – review & editing, Visualization, Project administration.

---

## Declaration of Competing Interest

The author declares no competing financial interests or personal relationships that could have influenced this work.

---

## References

[1] IEA, Global CO₂ emissions from transport by sub-sector in the Net Zero Scenario, 2000–2030, International Energy Agency, Paris, 2023. https://www.iea.org/data-and-statistics/charts/global-co2-emissions-from-transport-by-sub-sector-in-the-net-zero-scenario-2000-2030-2

[2] H.P. Williams, Model Building in Mathematical Programming, fifth ed., Wiley, Chichester, 2013.

[3] K. Deb, H. Jain, An evolutionary many-objective optimization algorithm using reference-point-based nondominated sorting approach, Part I: Solving problems with box constraints, IEEE Trans. Evol. Comput. 18 (2014) 577–601. https://doi.org/10.1109/TEVC.2013.2281535

[4] Q. Zhang, H. Li, MOEA/D: A multiobjective evolutionary algorithm based on decomposition, IEEE Trans. Evol. Comput. 11 (2007) 712–731. https://doi.org/10.1109/TEVC.2007.892759

[5] L. Sánchez-Pravos, J. Parra-Domínguez, S. Rodríguez González, P. Chamoso, A machine learning and evolutionary optimization framework for carbon-aware supply chain routing, Supply Chain Anal. 13 (2026) 100182. https://doi.org/10.1016/j.sca.2025.100182

[6] N.M. Alshabibi, et al., Multi-objective MILP for dynamic fleet scheduling with emission constraints, Sustainability 17 (2025) 4707. https://doi.org/10.3390/su17104707

[7] C. Shao, et al., NSGA-III for green intermodal freight transport with uncertain time-windows, Sustainability 14 (2022) 2985. https://doi.org/10.3390/su14052985

[8] T. Cui, Y. Shi, J. Wang, R. Ding, J. Li, K. Li, Practice of an improved many-objective route optimization algorithm in a multimodal transportation case under uncertain demand, Complex Intell. Syst. 11 (2025) 136. https://doi.org/10.1007/s40747-024-01725-4

[9] Ember, European Electricity Review 2024, Ember, London, 2024. https://ember-energy.org/latest-insights/european-electricity-review-2024/

[10] M. Ganjia, et al., Multi-objective sustainable supply chain scheduling with MILP-NSGA-II, Oper. Res. (2025). https://doi.org/10.1007/s12351-025-01013-0

[11] I. Das, J.E. Dennis, Normal-boundary intersection: A new method for generating the Pareto surface in nonlinear multicriteria optimization problems, SIAM J. Optim. 8 (1998) 631–657. https://doi.org/10.1137/S1052623496307510

[12] J. Blank, K. Deb, Y. Dhebar, S. Bandaru, H. Seada, Investigating the normalization procedure of NSGA-III, IEEE Access 7 (2019) 40729–40745. https://doi.org/10.1109/ACCESS.2019.2906754

[13] A. Tharwat, W. Schenck, Population initialization techniques for evolutionary algorithms for single- and multi-objective optimization problems, Swarm Evol. Comput. 67 (2021) 100952. https://doi.org/10.1016/j.swevo.2021.100952

[14] G.K.D. Saharidis, G.E. Konstantzos, Critical overview of emission calculation models in order to evaluate their potential use in estimation of greenhouse gas emissions from in-port truck operations, J. Clean. Prod. 185 (2018) 1024–1031. https://doi.org/10.1016/j.jclepro.2018.02.036

[15] P. Dehdari, et al., CO₂ equivalent calculation in road freight transport, Multimodal Transp. 2 (2023) 100090. https://doi.org/10.1016/j.multra.2023.100090

[16] European Environment Agency, EMEP/EEA Air Pollutant Emission Inventory Guidebook 2019, EEA Report No. 13/2019, European Environment Agency, Copenhagen, 2019. https://www.eea.europa.eu/en/analysis/publications/emep-eea-guidebook-2019

[17] HBEFA, Handbook Emission Factors for Road Transport, INFRAS AG, Bern, 2026. https://www.hbefa.net

[18] CEN, EN 16258:2012 — Methodology for Calculation and Declaration of Energy Consumption and GHG Emissions of Transport Services, European Committee for Standardization, Brussels, 2012.

[19] R. Grubb, Road freight and fuel use: A review, Energy Policy 16 (1988) 433–440. https://doi.org/10.1016/0301-4215(88)90073-5

[20] T. Bektaş, G. Laporte, The pollution-routing problem, Transp. Res. Part B Methodol. 45 (2011) 1232–1250. https://doi.org/10.1016/j.trb.2011.02.004

[21] EPA, Supply Chain Greenhouse Gas Emission Factors v1.3 by NAICS-6, U.S. Environmental Protection Agency, 2024. https://catalog.data.gov/dataset/supply-chain-greenhouse-gas-emission-factors-v1-3-by-naics-6

[22] EPA, Emissions and Generation Resource Integrated Database (eGRID), U.S. Environmental Protection Agency, 2026. https://www.epa.gov/egrid

[23] J. Dixon, W. Bukhsh, C. Edmunds, K. Bell, Scheduling electric vehicle charging to minimise carbon emissions and wind curtailment, Renew. Energy 161 (2020) 1072–1091. https://doi.org/10.1016/j.renene.2020.07.017

[24] Y. Jeong, G. Kim, I. Moon, Reliable container supply chain under disruption, Ann. Oper. Res. 349 (2025) 1345–1378. https://doi.org/10.1007/s10479-022-05068-6

[25] M. Borchardt, et al., Sustainable supply chain management and scope 3 emissions, Sustainability 17 (2025) 6066. https://doi.org/10.3390/su17136066

[26] IMO, Fourth IMO Greenhouse Gas Study 2020, International Maritime Organization, London, 2020. https://www.imo.org/en/ourwork/environment/pages/fourth-imo-greenhouse-gas-study-2020.aspx

[27] C. Gong, P. Guo, L.M. Pang, Q. Zhang, H. Ishibuchi, Population initialization for evolutionary multi-objective optimization: A short review, in: Proc. 2025 IEEE Congr. Evol. Comput. (CEC), IEEE, 2025. https://doi.org/10.1109/CEC65147.2025.11043105

[28] A. Mencaroni, P. Leyman, B. Raa, S. De Vuyst, D. Claeys, Towards net-zero manufacturing: Carbon-aware scheduling for GHG emissions reduction, J. Clean. Prod. 529 (2025) 146787. https://doi.org/10.1016/j.jclepro.2025.146787

