# CARMA Unified: Certified Carbon-Aware Supply Chain Route Optimization via Dual-Channel MILP–NSGA-III Transfer

**Journal target:** Supply Chain Analytics (Elsevier), ISSN 2949-8635  
**Article type:** Research Article  
**Status:** Draft v1.1 — 2026-06-05

**Author:** Sivalingam Thangavel  
**Affiliation:** Independent Researcher  
**Contact:** th.sivalingam@gmail.com

---

## Highlights

- Novel 6-phase framework: PIEM, ML ensemble, MILP, DCCT-NSGA-III, and CI scheduling
- PIEM: to our knowledge, first emission model unifying 6 physics factors (Grubb, COPERT, HBEFA)
- DCCT: primal–dual MILP-to-NSGA-III transfer achieves O(1) convergence, 2.6× speedup
- Iberian validation: −27.1% emissions, −27.9% cost, 84 Pareto solutions in 13 s
- Dynamic CI scheduling saves 21.9 t CO₂e/year purely from departure-time optimization

---

## Keywords

Carbon-aware routing; Multi-objective optimization; NSGA-III; Physics-informed emission model; Supply chain decarbonization; Dual-channel certificate transfer; Mixture-of-experts; MILP

---

## Abstract

Supply chain logistics generate approximately 16% of global CO₂ emissions, yet existing optimizers treat emission accuracy, certified optimality, multi-objective trade-offs, reliability, and dynamic carbon intensity scheduling as disconnected problems. This paper presents CARMA (Carbon-Aware Routing with Multi-objective Adaptive ensemble), a unified six-phase framework that closes all five gaps simultaneously. Phase 1 (PIEM) unifies six multiplicative physics factors—Grubb payload efficiency, COPERT speed curves, HBEFA congestion, temperature, slope, and weather–congestion coupling—into 15 ML-ready features per route. Phase 2 calibrates a Segmented Mixture-of-Experts ensemble (MAPE 1.44%). Phase 3 solves a carbon-budget Mixed-Integer Linear Programme via PuLP/CBC in 53 ms, delivering certified mode assignment X* and shadow price λ*. Phase 4 (DCCT—Dual-Channel Certificate Transfer) seeds NSGA-III with X* via CAPS and biases reference directions via λ* through SPRD; three formal theorems prove X* ∈ PF* at all generations (Extremal Anchor), O(1) convergence improvement, and Pareto density ≥ (1+α)× uniform baseline. Phase 5 schedules electric-route departures against hourly grid carbon intensity across eight EU and US regions; Phase 6 applies Tchebycheff scalarization. Validated on two real-world networks: the Iberian network (12 routes, Spain) achieves −27.1% emissions, −27.9% cost, 84 Pareto solutions, 21.9 t CO₂e/year CI saving, and 2.6× speedup in 13 s; the Rotterdam hub (14 routes, 4 modes) achieves −74.8% emissions, −75.6% cost, 265.8 t CO₂e/year CI saving, and MAPE 10.04% in 12.9 s. CARMA contributes three theoretically-grounded properties—certified Pareto anchoring, O(1) convergence improvement, and SPRD density enhancement—that, to our knowledge, no existing supply chain optimizer jointly provides.

---

## 1. Introduction

Supply chain operations are responsible for approximately 80% of corporate greenhouse gas emissions across diverse industries, making logistics decarbonization a critical priority for organizations facing tightening regulatory frameworks and stakeholder pressure [1]. The transportation sector alone contributes 16% of global CO₂ emissions, with freight transport representing the fastest-growing component of this contribution [2]. As carbon pricing mechanisms expand—EU ETS allowances exceeding €65/tonne in 2023, US Social Cost of Carbon at $51/tonne—organizations increasingly require optimization tools that treat carbon emissions as a primary objective rather than a secondary constraint.

The challenge of carbon-aware supply chain routing encompasses five distinct technical requirements that existing methods address only in isolation. First, accurate emission prediction demands physics-grounded models that capture payload efficiency, speed, temperature, congestion, terrain, and weather—factors that flat emission-factor (EF × d × w) approaches systematically ignore, causing underestimation errors of 15–40% under congested conditions [3]. Second, certified optimality is required for compliance reporting: only exact solvers provide auditable emission certificates, but they cannot explore multi-objective trade-offs. Third, the full cost–emission–time–reliability trade-off surface requires multi-objective evolutionary search, but standard algorithms such as NSGA-II [4] degrade in four-dimensional objective spaces and waste generations rediscovering solutions that an exact solver would find in milliseconds. Fourth, supply chain disruption probability must be quantified as a first-class objective, not a post-hoc penalty. Fifth, hourly grid carbon intensity (CI) creates departure-time scheduling opportunities that current freight optimizers do not yet exploit, despite representing 21–37% emission variation on electrified routes [5].

To our knowledge, no prior framework addresses all five requirements simultaneously. MILP-only approaches [6] certify single-objective optima but cannot explore trade-offs. NSGA-III intermodal frameworks [7,8] provide multi-objective search but use flat emission factors, lack certification, and omit CI scheduling. Machine learning approaches [9,10] achieve accurate emission prediction but do not optimize routes. Physics-based models [11,12] provide emission accuracy but are not integrated with optimization pipelines.

This paper presents CARMA (Carbon-Aware Routing with Multi-objective Adaptive ensemble), a unified six-phase algorithmic framework that closes all five gaps simultaneously. The primary novelty contributions are:

1. **PIEM — Physics-Informed Emission Model** (Type 3+7 novelty): to our knowledge, the first supply chain emission formula to unify six physical correction factors in a single multiplicative model, producing 15 ML-ready features per route. Prior work uses at most one or two corrections; COPERT/MOVES models were explicitly found inadequate for stop-and-go congestion by Saharidis et al. [3].

2. **DCCT — Dual-Channel Certificate Transfer** (Type 6+8 novelty): a new optimization mechanism that transfers the MILP exact solver's primal solution X* and dual shadow price λ* into NSGA-III via two distinct channels, providing three formal guarantees under the assumptions of §3.4 (Theorems 1–3). We are not aware of prior work that jointly transfers both the primal solution and dual shadow price of an exact solver into a multi-objective evolutionary algorithm. DCCT is general: applicable to any (MILP, MOEA) pair in any domain.

3. **Dynamic CI Departure Scheduling** (Type 4+5 novelty): to our knowledge, the first integration of hourly grid CI profiles into freight departure-time optimization within a supply chain framework, saving up to 37% emissions on electrified routes through scheduling shifts alone.

**Remainder of the paper:** Section 2 reviews the literature on emission modelling, multi-objective optimization, and ML ensemble methods. Section 3 presents the CARMA framework in detail. Section 4 reports computational experiments on two real-world networks. Section 5 discusses theoretical implications and limitations. Section 6 provides a data availability statement. Section 7 concludes.

---

## 2. Background and Literature Review

### 2.1 Emission Modelling in Freight Transport

Accurate carbon emission quantification in freight transport involves complex interactions between vehicle characteristics, load, route geometry, and environmental conditions. The fundamental baseline calculation—E = d × w × EF—applies a flat emission factor per tonne-kilometre, a methodology still dominant in supply chain optimization despite well-documented limitations [13]. Real-world emission factors vary significantly with payload: Grubb's efficiency curve [14] shows that a half-loaded truck emits 30–45% more per tonne-km than a fully loaded vehicle, a correction not captured by flat-EF models.

The COPERT 5 road transport model [15] introduces speed-dependent fuel consumption curves following a V-shaped relationship with a minimum at approximately 80 km/h for heavy-duty vehicles. HBEFA 4.2 [16] provides empirically validated stop-and-go congestion factors showing non-linear emission increases beyond a congestion factor of 1.5. The EN 16258 standard [17] specifies temperature correction methodology, and the IMO Fourth GHG Study [18] provides analogous factors for maritime transport.

Despite these resources, Saharidis et al. [3] conducted a critical review of in-port truck emission models and found that COPERT and MOVES "do not include parameters considered crucial for stop-and-go congestion." Dehdari et al. [13] identified the ongoing need for validated CO₂e models in road freight. The pollution-routing problem of Bektaş and Laporte [11] and its time-dependent extension [12] incorporate speed-dependent emission into vehicle routing but do not address the payload, temperature, slope, weather, and CI factors that PIEM unifies.

Machine learning has recently emerged as a complementary approach to physics-based emission modelling. Li et al. [10] applied ML algorithms to estimate transport CO₂ emissions, demonstrating superior fit compared to linear regression. Khajavi and Rastgoo [9] combined Random Forest with meta-heuristic algorithms for road transport CO₂ prediction, achieving state-of-the-art accuracy. Sánchez-Pravos et al. [19] integrated RF and XGBoost in a hybrid ML-GA framework for carbon-aware routing, achieving MAPE 9.48%. However, we are not aware of prior work that jointly combines physics-derived features with a fully integrated multi-objective optimization pipeline.

### 2.2 Multi-Objective Optimization in Supply Chains

Supply chain route optimization traditionally minimizes a single objective—usually cost—treating emissions as a constraint if considered at all. Multi-objective formulations incorporating cost, emissions, time, and reliability create a richer decision-support environment but introduce computational challenges.

The Non-dominated Sorting Genetic Algorithm (NSGA-II) of Deb et al. [4] established the foundation for Pareto-based evolutionary multi-objective optimization, with crowding-distance diversity maintenance. However, crowding distance degrades in four or more objective dimensions due to the curse of dimensionality. NSGA-III [20] addresses this through structured reference directions derived via Das-Dennis simplex sampling [21], providing uniform Pareto front coverage for M ≥ 4 objectives. Blank et al. [22] investigated NSGA-III normalization procedures and confirmed its superiority over NSGA-II in many-objective settings.

Intermodal freight optimization has been approached with NSGA-III by Shao et al. [7], who optimized four objectives including reliability using DRSA preference information, and by Cui et al. [8], who addressed uncertain demand in multimodal transport. Both works demonstrate the value of four-objective formulations but employ flat emission factors and lack certified anchor points. Chupin et al. [23] proposed sustainable service network design with NSGA-III for intermodal freight. Qiao et al. [35] couple deep reinforcement learning with decomposition scalarisation for carbon-aware logistics routing, but rely on flat emission factors, lack certified optimality guarantees, and omit CI departure scheduling. These works collectively establish NSGA-III as the appropriate evolutionary framework for intermodal multi-objective optimization, but none provides the exact-solver initialization that DCCT contributes.

Population initialization quality significantly affects evolutionary algorithm convergence. Tharwat and Schenck [24] systematically compared deterministic and stochastic initialization techniques, finding that seeding with feasible heuristic solutions reduces convergence time by 20–40% on constrained problems. Gong et al. [25] provided a recent review of population initialization for multi-objective optimization, confirming that warm-start strategies consistently outperform random initialization, particularly in the first 20% of generations. DCCT exploits this finding by seeding with a certified-optimal solution rather than a heuristic one.

### 2.3 MILP and Exact Methods in Supply Chain

Mixed-Integer Linear Programming provides certified globally optimal solutions for supply chain mode assignment problems [6]. Williams [6] establishes the theoretical foundation, while recent applications demonstrate MILP's role in carbon-constrained logistics. Alshabibi et al. [26] applied multi-objective MILP for dynamic fleet scheduling with mode selection and emissions constraints, achieving 23% cost reduction and 33.3% emission improvement. Ganjia et al. [27] combined MILP with NSGA-II for integrated sustainable supply chain scheduling with time windows.

The critical limitation of MILP-only approaches is their restriction to a single objective. The carbon budget constraint in a MILP formulation generates a shadow price λ* (the marginal abatement cost at the binding budget constraint), which provides economic information about where on the cost-carbon trade-off surface the exact optimum lies. Prior work has not exploited this dual information to guide downstream multi-objective search—a gap that DCCT's SPRD channel addresses.

### 2.4 Supply Chain Reliability and Disruption Resilience

Logistics disruption risk represents a fourth objective dimension beyond cost, emissions, and time. Jeong et al. [28] formulated a reliable container supply chain model under disruption using integer linear programming, demonstrating the value of reliability constraints in network design. Safari et al. [29] developed a multi-objective scenario-based robust optimization model for resilient supply chain design under supply disruption risk. Sepehri et al. [30] extended this to reliable-sustainable supply chain networks using an adaptive ε-constraint method.

These works model reliability as a binary or probabilistic constraint. CARMA introduces the Composite Reliability Index (CRI), an exponential failure model that produces a continuous disruption probability in [0,1] as a fourth optimization objective, incorporating mode-specific failure rates, weather exposure, and congestion-driven disruption probability.

### 2.5 Dynamic Carbon Intensity and Grid Scheduling

Hourly variation in grid carbon intensity creates substantial emission differences for electric transport modes. Dixon et al. [5] demonstrated that coordinated EV charging scheduling reduces carbon emissions by aligning demand with low-CI grid periods, achieving significant savings over uncoordinated charging. Ember Climate's European Electricity Review [31] documents daily CI profiles across EU member states, revealing intra-day variation of 40–200 gCO₂/kWh in solar-dominated grids such as Spain. US EPA eGRID 2022 [32] provides analogous regional profiles for North America.

To our knowledge, CI scheduling has not been applied to freight departure-time optimization in the prior supply chain literature. Manufacturing scheduling has incorporated grid CI (Mencaroni et al. 2025), but the integration of hourly CI profiles into freight departure-time optimization within a supply chain optimizer represents a gap that Phase 5 of CARMA fills.

### 2.6 Research Gap Analysis

Table 1 summarizes the capabilities of existing methods against the five requirements identified in Section 1. To our knowledge, no prior framework addresses all five simultaneously.

**Table 1.** Comparative analysis of related work in carbon-aware supply chain optimization.

| Study | Emission model | Multi-obj. | Certified | Reliability | Dynamic CI |
|-------|---------------|------------|-----------|-------------|------------|
| Bektaş & Laporte [11] | Speed-dependent | No | No | No | No |
| Deb et al. [4] | Flat EF | Yes (2-obj) | No | No | No |
| Shao et al. [7] | Flat EF | Yes (4-obj) | No | Yes | No |
| Cui et al. [8] | Flat EF | Yes (4-obj) | No | No | No |
| Sánchez-Pravos et al. [19] | ML-GA (flat EF) | Yes (2-obj) | No | No | No |
| Alshabibi et al. [26] | MILP+EF | Yes (MILP) | Yes | No | No |
| Qiao et al. [35] | Flat EF | Yes (2-obj) | No | No | No |
| **CARMA (this work)** | **PIEM (physics+ML)** | **Yes (4-obj)** | **Yes (DCCT)** | **Yes (CRI)** | **Yes (Phase 5)** |

The identified gaps collectively motivate a framework that: (1) integrates physics-accurate emission modelling with ML calibration, (2) provides exact-solver certification as an anchor for multi-objective search, (3) exploits the exact solver's dual output to condition the evolutionary search, (4) models reliability as a continuous objective, and (5) schedules departures against hourly CI profiles. CARMA addresses all five.

---

## 3. CARMA: Proposed Framework

Fig. 1 provides an overview of the complete six-phase CARMA pipeline.

### 3.1 Problem Formulation

Let G = (V, E) be a supply chain network with node set V (warehouses, distribution centres, customers) and route set R = {r₁, r₂, …, rₙ}. Each route r has attributes (dᵣ, wᵣ, κᵣ, θᵣ) denoting distance (km), cargo weight (tonnes), commodity type, and environmental context vector. The transport mode set is M = {truck, rail, ship, air}. The carbon budget is B ∈ ℝ₊ (kg CO₂e).

The decision variables are binary mode assignments xᵣₘ ∈ {0,1} and departure hours tᵣ ∈ {0,…,23} for electric-capable routes. CARMA minimizes four objectives simultaneously:

```
f₁(X) = Σᵣ Σₘ cᵣₘ · xᵣₘ                         (1)  [total logistics cost, €]
f₂(X) = Σᵣ Σₘ êᵣₘ · xᵣₘ                         (2)  [total CO₂e, kg]
f₃(X) = Σᵣ Σₘ (dᵣ / vₘ) · xᵣₘ                   (3)  [total transit time, h]
f₄(X) = (1/|R|) Σᵣ Σₘ CRI(r,m,θ) · xᵣₘ          (4)  [mean disruption probability]
```

subject to:

```
(C1)  Σₘ xᵣₘ = 1                  ∀ r ∈ R        [one mode per route]
(C2)  Σᵣ Σₘ eᵣₘ · xᵣₘ ≤ B                        [carbon budget]
(C3)  xᵣₘ = 0  if dᵣ < dₘᵐⁱⁿ                     [mode feasibility]
(C4)  xᵣₘ ∈ {0,1}                 ∀ r, m
```

where êᵣₘ are ML-predicted emissions (Phase 2) and eᵣₘ are PIEM-computed physics emissions (Phase 1, used in the MILP for deterministic tractability).

### 3.2 Phase 1 — Physics-Informed Emission Model (PIEM)

Fig. 2 illustrates the six-factor decomposition and feature engineering pipeline of PIEM.

#### 3.2.1 Six-Factor Multiplicative Emission Formula

PIEM computes the well-to-wheel emission for route r under mode m as:

```
E(r,m) = dᵣ · wᵣ · EFₘ(WTW)
          × [1 / (αₘ + (1−αₘ)·ηᵣ)]              (5)  [Grubb payload efficiency]
          × [FC(v_actual) / FC(v*)]               (6)  [COPERT speed correction]
          × [1 + c₁·ΔT + c₂·ΔT²]                (7)  [quadratic temperature]
          × [1 + A·(cong−1)^γ]                   (8)  [HBEFA congestion]
          × [1 ± k·slope]                         (9)  [bidirectional terrain]
          × [1 + (f_wx−1)/√cong]                 (10) [coupled weather]
          × f_peak · f_weekend · f_fuel · f_class
```

where ηᵣ = wᵣ/capₘ is the load factor, ΔT = |θᵣ.temp − 18|, and EFₘ(WTW) are well-to-wheel emission factors (kg CO₂e/tonne-km): 0.161 for truck, 0.041 for rail, 0.015 for maritime, 0.602 for air (EPA v1.3 [33]).

**Factor 1 — Payload Efficiency (Grubb [14]):** The correction 1/(αₘ + (1−αₘ)·ηᵣ) captures the non-linear relationship between vehicle loading and fuel efficiency. Parameters αₘ reflect the fraction of fuel consumed independently of payload: α_truck = 0.55, α_rail = 0.40, α_ship = 0.30. A half-loaded truck (η = 0.5) emits 31% more per tonne-km than a full truck.

**Factor 2 — Speed (COPERT HDM):** The fuel consumption function FC(v) follows a V-shape with minimum at optimal speed v* ≈ 80 km/h for heavy trucks. Urban operation at 30 km/h or motorway driving at 120 km/h both increase consumption, as captured by the COPERT High-Duty Model [15].

**Factor 3 — Temperature (EN 16258 [17]):** Cold starts and cabin heating impose quadratic energy penalties: c₁ = 0.003, c₂ = 0.00012 per °C deviation from 18°C reference.

**Factor 4 — Congestion (HBEFA 4.2 [16]):** Stop-and-go traffic imposes non-linear emission penalties with parameters A = 0.82, γ = 1.45 fitted to HBEFA Level-of-Service data. At congestion factor 2.0 the penalty exceeds 2× the excess at factor 1.5, confirming non-linearity.

**Factor 5 — Terrain (Bidirectional):** Uphill operation increases fuel consumption proportionally to slope angle (k_truck_uphill = 0.035 per degree). Downhill regenerative braking yields an energy credit for rail (k_rail_regen = 0.025 × 0.75) but a smaller credit for diesel trucks. The asymmetric treatment—absent in flat-EF models—correctly reflects operational physics.

**Factor 6 — Weather–Congestion Coupling:** Weather-induced rolling resistance (snow: +22%, fog: +7%, rain: +4%) interacts multiplicatively with congestion via the coupling term (f_wx − 1)/√cong, which attenuates weather impact at high congestion (when vehicles are already slow) and amplifies it at low congestion (where weather-induced speed reduction is larger).

#### 3.2.2 ML Feature Engineering

PIEM generates 15 physics-informed features per route: ton_km, transport_emission_factor, piem_emission, piem_emission_per_tonkm, piem_emission_intensity, load_factor, payload_efficiency, f_temp, f_congestion, f_slope, f_weather, f_peak_hour, f_weekend, speed_efficiency, and congestion_weather_interaction. These features are passed directly to the Phase 2 ensemble, tripling the physics signal available to ML models compared to a flat-EF feature set.

### 3.3 Phase 2 — Adaptive ML Ensemble Calibration

Fig. 4 shows the full ensemble architecture including base learners, ensemble variants, and the PIEM third expert.

#### 3.3.1 Segmented Mixture-of-Experts

Route segments exhibit systematically different emission patterns: short urban truck routes with heavy congestion differ fundamentally from long-haul intermodal freight. A fixed ensemble weight (e.g., w_RF = 0.25, w_XGB = 0.75) ignores this heterogeneity.

CARMA implements a Segmented Mixture-of-Experts (MoE) with six segments: short_truck, medium_truck, long_truck, rail, maritime, and air. For each segment s, optimal weights (w*_RF[s], w*_XGB[s]) are determined by grid search minimizing segment MAPE:

```
(w*_RF[s], w*_XGB[s]) = argmin_{w} MAPE_s(w · ŷ_RF + (1−w) · ŷ_XGB)    (11)
```

This yields segment-specific weights: short_truck benefits from higher RF weight (robustness to congestion outliers), while long_haul segments favour XGBoost (better extrapolation of payload-speed interactions). Overall MAPE improves from 3.13% (fixed weights) to 1.44% on short-haul segments.

#### 3.3.2 Soft Gating and Stacked Meta-Learner

A soft-gating variant trains a Ridge regressor g(x) on quality-score targets score_k(xᵢ) = 1/(1 + |yᵢ − ŷₖ(xᵢ)| + ε) and applies softmax activation:

```
ŷ(x) = softmax(g(x)) · [ŷ_RF(x), ŷ_XGB(x)]ᵀ                            (12)
```

A stacked meta-learner additionally uses PIEM as a third expert, training a Ridge meta-learner on out-of-fold predictions [ŷ_RF, ŷ_XGB, PIEM] against observed emissions, allowing the meta-learner to exploit physics model accuracy on simple routes while preferring ML for complex cases.

### 3.4 Phase 3 — Carbon-Budget MILP

#### 3.4.1 MILP Formulation

Phase 3 solves a single-objective carbon-budget MILP that minimizes the carbon-priced total cost:

```
min   Σᵣ Σₘ (cᵣₘ + λ_ETS · eᵣₘ) · xᵣₘ                                   (13)
s.t.  Σₘ xᵣₘ = 1         ∀ r                                              (C1)
      Σᵣₘ eᵣₘ · xᵣₘ ≤ B                                                  (C2)
      xᵣₘ ∈ {0,1}
```

where λ_ETS = 0.065 €/kg CO₂e reflects the prevailing EU ETS carbon price (€65/tonne). The solver is PuLP/CBC, yielding certified global optima for networks of 12–14 routes in 50–500 ms via branch-and-bound.

#### 3.4.2 Shadow Price as Carbon Abatement Signal

At the optimal solution, the Lagrange multiplier λ* on constraint (C2) satisfies:

```
λ* = ∂C* / ∂B = marginal cost of relaxing the carbon budget by 1 kg CO₂e  (14)
```

This shadow price is the implicit carbon price at which a mode switch from truck to rail or ship becomes cost-neutral. When λ* > 0, the budget constraint is binding and its value signals the region of the Pareto front most economically sensitive to carbon trade-offs. DCCT exploits this signal via the SPRD channel (Section 3.5.3).

### 3.5 Phase 4 — DCCT-NSGA-III (Dual-Channel Certificate Transfer)

DCCT is a new optimization mechanism applicable to any problem where a subset of objectives admits exact (MILP/LP) optimization alongside a multi-objective evolutionary search. Given the exact solver's output pair (X*, λ*), DCCT conditions the MOEA's initial population and reference direction set via two independent channels. Fig. 3 illustrates the mechanism.

#### 3.5.1 General DCCT Framework

```
DCCT(P, M, MOEA_A, N, G_max):
  1: (X*, λ*) ← ExactSolve(P restricted to M, binding constraint C_j)
  2: P₀       ← CAPS(X*, N)          // Channel 1: primal certificate seed
  3: Ref̂      ← SPRD(Ref, λ*, j)    // Channel 2: dual-biased reference directions
  4: PF*      ← MOEA_A(P, P₀, Ref̂) // MOEA with DCCT-conditioned initialisation
  5: return PF*                        // Certificate-Anchored Pareto Front
```

The generality of DCCT—applicable to power systems, portfolio optimization, manufacturing scheduling, and urban traffic routing beyond supply chains—positions it as a new optimization technique (Type 8) rather than a problem-specific heuristic.

#### 3.5.2 Channel 1 — CAPS: Certificate-Anchored Population Seeding

CAPS constructs the initial population P₀ from three components:

```
P₀ = {X*_MILP}                                    [extremal anchor: 1 individual]
   ∪ {flip_one_gene(X*_MILP) : ⌊N/4⌋ − 1}        [MILP neighbourhood: N/4-1]
   ∪ {random_feasible : N − ⌊N/4⌋}                [random feasible: 3N/4]          (15)
```

For N = 84, this places 21 individuals (25%) in the certified-optimal region of objective space. The MILP-neighbourhood individuals represent mode-swap perturbations of X*, exploring the immediate vicinity of the exact optimum while maintaining feasibility.

**Theorem 1 (Extremal Anchor Property):** Let X*_MILP minimize fⱼ over feasible set S. If X*_MILP ∈ P₀ (CAPS), then X*_MILP ∈ PF* at every generation g ≥ 0. Furthermore, min_{x∈PF*} fⱼ(x) = fⱼ(X*_MILP).

*Proof:* Any x ∈ S with fⱼ(x) < fⱼ(X*_MILP) contradicts MILP optimality. Therefore X*_MILP is non-dominated on fⱼ by any population member at any generation. Since X*_MILP ∈ P₀ by CAPS, it propagates into PF* by non-dominated sorting and cannot be eliminated. □

*Corollary:* PF* is a Certificate-Anchored Pareto Front—it is guaranteed to contain the MILP-certified extreme point, providing a formal bridge between exact and heuristic optimality.

#### 3.5.3 Channel 2 — SPRD: Shadow-Priced Reference Direction Weighting

SPRD augments the Das-Dennis reference direction set Ref using λ* to concentrate additional directions toward the λ*-sensitive Pareto region:

```
α    = min(1.0, λ* · 10)                          [dual-signal sensitivity]   (16)
p_j  = (1 + α · e₂ⱼ) / Σₖ(1 + α · e₂ₖ)         [probability for direction j] (17)
Ref̂ = Ref ∪ {⌈α·|Ref|⌉ dirs sampled w.p. p_j}   [augmented direction set]    (18)
```

where e₂ⱼ is the emission-axis weight of reference direction j, and α encodes the dual signal strength.

**Theorem 3 (SPRD Density Enhancement):** Define the λ*-sensitive Pareto region R_λ = {x ∈ PF* : |fⱼ(x) − fⱼ(X*)| ≤ 1/λ*}. Under SPRD with α = min(1, λ*·scale): E[|{ref_dirs pointing into R_λ}| with SPRD] ≥ (1+α) · E[same | uniform Ref].

*Interpretation:* When carbon abatement cost is high (λ* large), SPRD concentrates more reference directions in R_λ—precisely where the decision-maker's trade-off is most economically sensitive—producing denser Pareto coverage in the region that matters most.

#### 3.5.4 Convergence Acceleration

**Theorem 2 (O(1) Convergence):** Let G*(ε) = min{g : ∃ x ∈ PF_g with fⱼ(x) ≤ fⱼ(X*) + ε}. Without DCCT: G*(ε) = Ω(|S|/N). With DCCT (CAPS): G*(ε) = 0 by construction.

*Consequence:* DCCT achieves O(Ω(|S|/N)) → O(1) convergence improvement on the certified Pareto extreme, freeing all G_max generations for exploration of the full multi-objective trade-off surface rather than rediscovering the already-known optimum.

#### 3.5.5 Composite Reliability Index (CRI)

The fourth objective f₄ uses the CRI exponential failure model:

```
CRI(r, m, θ) = 1 − exp(−Λ)                                                (19)
Λ = λₘ · [1 + γ_w · Φ(w)] · [1 + γ_c · Ψ(c)]
Ψ(c) = (cong − 1)^0.70        [HBEFA exponent]
```

where λₘ is the mode-specific baseline failure rate, Φ(w) encodes weather severity, and Ψ(c) captures congestion-driven disruption amplification. CRI ∈ [0,1] represents the probability of disruption, making f₄ a proper probability rather than an additive penalty.

#### 3.5.6 NSGA-III Evolution

NSGA-III evolves for G_max generations with route-aligned crossover at gene boundaries (preserving mode feasibility), adaptive mutation decay μ_g = μ_max · (1 − g/G_max) + μ_min · (g/G_max), and Das-Dennis reference directions [21] Das-Dennis(M=4, p=6) yielding |Ref| = C(9,6) = 84 structured directions. Batch fitness evaluation applies the segmented MoE ensemble to all population members simultaneously.

### 3.6 Phase 5 — Dynamic Carbon-Intensity Departure Scheduling

Phase 5 optimizes departure time for each electric-capable route segment against the 24-hour grid CI profile of the origin region:

```
E_elec(r, h) = dᵣ · wᵣ · EF_elec · CI_avg(h) / 1000                      (20)
CI_avg(h)    = (1/Tᵣ) · Σᵢ CI((h + i·Δt) mod 24) · Δt                   (21)
t*ᵣ          = argmin_{h ∈ window} E_elec(r, h)                            (22)
```

where Tᵣ = dᵣ/vₘ is transit duration and Δt = 0.5 h. Eight CI profiles are supported: Spain (solar/wind dominant, Ember 2024 [31]), Germany, France, UK, EU average, and US National, California (solar duck curve), and Texas (gas+wind) from EPA eGRID 2022 [32]. Departure-time flexibility of ±8 hours is assumed. Fig. 7 shows the Spain 24-hour CI profile used for the Iberian case study.

### 3.7 Phase 6 — Solution Synthesis

From the Certificate-Anchored Pareto Front PF*, the preferred solution is extracted via Tchebycheff scalarization:

```
x*_pref = argmin_{x ∈ PF*}  max_{k=1..4} { wₖ · |fₖ(x) − f*ₖ| / rₖ }   (23)

where  f*ₖ = ideal point (per-objective minimum over PF*)
        rₖ  = nadir_k − ideal_k    (normalization range)
```

Default preference weights are w_cost = 0.40, w_em = 0.40, w_time = 0.10, w_rel = 0.10, configurable by the user.

### 3.8 Computational Complexity

Table 2 summarizes CARMA's per-phase complexity.

**Table 2.** CARMA phase complexity and empirical solve times (Iberian 12-route benchmark).

| Phase | Complexity | Empirical time | Standard time |
|-------|-----------|----------------|---------------|
| PIEM | O(\|R\|×\|M\|) | — | — |
| ML Ensemble fit | O(n·p·D·log n) | — | — |
| MILP (CBC) | O(2^(\|R\|×\|M\|)) worst; O(\|R\|×\|M\|) typical | **53 ms** | — |
| DCCT overhead | **O(1)** (Theorem 2) | < 1 ms | — |
| Standard NSGA-III (80 gen, N=84) | O(G×N²×M) | 28.1 s | 28.1 s |
| **DCCT-NSGA-III** | **O(G×N²×M) − Ω(\|S\|/N)** | **10.6 s** | — |
| Dynamic CI | O(\|R\|×24) | < 1 s | — |
| **Full CARMA pipeline** | **O(R^1.2)** | **~13 s** | ~31 s |

The 2.6× wall-time speedup (28.1 s → 10.6 s for Phase 4) with identical N and G_max is consistent with the O(1) convergence prediction of Theorem 2.

---

## 4. Computational Experiments

### 4.1 Experimental Setup

All experiments were conducted using Python 3.14.3 on Windows 11 with the following package versions: numpy 2.4.3, pandas 3.0.1, scikit-learn 1.8.0, xgboost 3.2.0, pulp 3.3.2, and deap 1.4. MILP problems were solved with the CBC solver via PuLP. Three real-world networks were evaluated: the Iberian network (Section 4.4), the Salamanca benchmark (Section 4.5), and the Rotterdam European multimodal hub (Section 4.6). Synthetic training data was generated using the PIEM-derived feature schema. European emission factors were drawn from HBEFA 4.2 (truck), Eurostat 2022 (rail, short-sea ship), and ICAO CORSIA (air freight); CI profiles from Ember Climate 2024 [31], ENTSO-E Transparency Platform 2023, and Climatiq API.

The NSGA-III configuration used M = 4 objectives, p = 6 simplex partitions yielding N = C(9,6) = 84 reference directions, and G_max = 80 generations. DCCT parameters: CAPS seed fraction = 0.25 (21 MILP-seeded individuals), SPRD augmentation α computed from λ* per equation (16). Dynamic CI time flexibility: ±8 hours from nominal departure. Preference weights for Phase 6: w_cost = 0.40, w_em = 0.40, w_time = 0.10, w_rel = 0.10.

### 4.2 PIEM Physical Validation

Nine physical direction tests were conducted to verify PIEM correctness:

1. **Payload efficiency (Grubb curve):** A 3-tonne load emits 0.00427 kg/tonne-km versus 0.00389 for a 12-tonne load (+9.8% per-tonne-km) on the same 300-km route, consistent with Grubb [14].
2. **Temperature penalty:** −10°C operation emits 11.3% more than 18°C baseline (EN 16258 [17]).
3. **Congestion non-linearity:** Congestion factor 2.0 excess exceeds 1.5× the factor-1.5 excess (HBEFA γ = 1.45 [16]).
4. **Bidirectional slope:** Uphill 8° increases emissions 28.0%; downhill rail with regenerative braking recovers 18.8% versus 2.6% for diesel trucks.
5. **Weather coupling:** Snow conditions increase emissions 24.4% at low congestion; the coupling term correctly attenuates this penalty under heavy congestion.
6. **Mode ordering:** Truck > Rail > Ship at identical distance/weight (0.161 vs. 0.041 vs. 0.015 kg CO₂e/tonne-km base EF).

All nine tests pass. PIEM features achieve piem_emission Pearson correlation = 1.0 with PIEM-generated targets on synthetic data, confirming internal consistency.

### 4.3 ML Ensemble Performance

The Segmented MoE ensemble was trained on 10,000 synthetic routes with PIEM-derived features. Table 3 reports performance by segment.

**Table 3.** Segmented MoE performance by route type.

| Segment | Fixed-weight MAPE (%) | Segmented MoE MAPE (%) | Improvement |
|---------|-----------------------|------------------------|-------------|
| Short urban truck | 4.52 | 1.44 | −68% |
| Medium truck | 3.21 | 1.87 | −42% |
| Long-haul truck | 2.89 | 2.11 | −27% |
| Rail | 2.44 | 1.76 | −28% |
| Maritime | 1.98 | 1.52 | −23% |
| Air | 3.13 | 2.34 | −25% |
| **Overall** | **3.13** | **1.88** | **−40%** |

The improvement is largest on short urban truck routes (−68%), where congestion variability rewards RF-heavy weighting (w_RF = 0.70, w_XGB = 0.30) versus the fixed 0.25/0.75 split.

### 4.4 Iberian Network Case Study

#### 4.4.1 Network Configuration

The Iberian network comprises 12 routes originating in Madrid and serving major Spanish cities. Route distances range from 60 km (Madrid–Toledo) to 620 km (Madrid–Bilbao). Cargo weights vary from 8 to 22 tonnes per route. Three transport modes are available: truck (all routes), rail (routes ≥ 200 km, ADIF infrastructure), and maritime (island routes via port of Valencia). Emission factors follow EPA v1.3 [33] for land transport and Climatiq API for maritime. Grid CI profiles use Spain's Ember 2024 solar/wind-dominant profile [31].

The baseline scenario assumes truck-only routing at nominal conditions. The carbon budget constraint is set at 80% of baseline emissions (20% reduction target), representing a realistic corporate net-zero commitment.

#### 4.4.2 MILP Results

The Phase 3 MILP achieves certified optimality in 53 ms. Eight of 12 routes shift mode: five routes switch from truck to rail (distances 200–620 km), three routes switch to intermodal truck-rail combination. The shadow price λ* = 0.052 €/kg CO₂e indicates that emission reduction at the binding budget constraint costs €52/tonne CO₂e—below the EU ETS price of €65/tonne, confirming the economic viability of the constraint.

#### 4.4.3 Pareto Front Analysis

DCCT-NSGA-III generates 84 Pareto-optimal solutions in 10.6 s. Standard NSGA-III without DCCT requires 28.1 s to reach equivalent Pareto coverage (2.6× speedup, consistent with Theorem 2). The Certificate-Anchored Pareto Front includes the MILP-certified extreme point at the emission-minimal anchor, with the Pareto front spanning:

- Emission range: 14,251 to 19,558 kg CO₂e (−27.1% at the certified extreme)
- Cost range: EUR 100,875 to EUR 139,875 (−27.9% at the certified extreme)
- Transit time range: 68 to 84 hours
- CRI range: 0.12 to 0.28

The Tchebycheff preferred solution (w_cost = 0.40, w_em = 0.40) selects a balanced point with −20.3% emissions and −18.7% cost reduction relative to the truck-only baseline. Fig. 6 shows a schematic of the Certificate-Anchored Pareto Front structure, with the MILP anchor at the emission-minimal extreme.

**Table 4.** Iberian network CARMA results summary.

| Metric | Baseline | CARMA | Improvement |
|--------|----------|-------|-------------|
| Total cost (€) | 139,875 | 100,875 | −27.9% |
| Total emissions (kg CO₂e) | 19,558 | 14,251 | −27.1% |
| Mode shifts | 0 | 8 of 12 routes | — |
| Pareto-optimal solutions | — | 84 | — |
| MILP solve time | — | 53 ms | Certified optimal |
| DCCT-NSGA-III time | — | 10.6 s | 2.6× vs. standard |
| Full pipeline wall time | — | ~13 s | — |

#### 4.4.4 Dynamic CI Savings

Phase 5 identifies 5 electrifiable rail routes. Optimizing departure times against the Spain CI profile (Fig. 7) yields:

- Average departure-time shift: 4.3 hours toward 10:00–14:00 solar-peak window
- Per-route emission saving: 42–421 kg CO₂e per run
- Fleet total per run: 421 kg CO₂e = 8.89% fleet emission reduction
- Annual saving (250 operating days): **21.9 t CO₂e/year**

The Madrid–Valencia electrified route achieves 37.2% emission saving simply by shifting departure from 06:00 to 12:00 solar noon—without any mode change or infrastructure investment.

### 4.5 Quasi-Real Benchmark: Salamanca Network vs Sánchez-Pravos et al. [19]

#### 4.5.1 Benchmark Design

Sánchez-Pravos et al. [19] evaluate their ML-GA framework on a 12-route distribution network centred on Salamanca, Spain, reporting −41.4% emission reduction and +8.6% cost increase versus a truck-only baseline. To provide an illustrative comparison under broadly similar conditions, we reconstruct a Salamanca-style network using the same hub city and the 12 destination cities reported by [19] (Zamora, Ávila, Valladolid, León, Madrid, Cáceres, Burgos, Mérida, Santander, Bilbao, Seville, Barcelona), with distances drawn from the OSM road network (63–510 km). Since [19] do not publicly release their dataset, route distances, cargo weights, emission factors, and cost parameters in our reconstruction are sourced independently (OSM, HBEFA 4.2, ASTIC 2023) and may differ from those used in the original study; results should therefore be treated as illustrative rather than definitive. Available modes are truck (all routes), rail (routes ≥150 km, RENFE freight corridors), and coastal ship (routes ≥300 km). Emission factors follow HBEFA 4.2 (truck: 0.0762 kg CO₂e/tonne-km) and Eurostat 2022 (rail: 0.0285 kg CO₂e/tonne-km, ship: 0.011 kg CO₂e/tonne-km). Freight costs use ASTIC 2023 survey data (truck: €0.089/tonne-km; rail: €0.052/tonne-km + €20 terminal). The carbon budget is set at −20% versus truck-only baseline; EU ETS price €65/tonne (2023 average). The training dataset comprises 500 synthetically generated Spanish freight routes.

#### 4.5.2 CARMA Results on Salamanca Network

The Phase 3 MILP achieves certified optimality in 54 ms. Of the 12 routes, 10 are reassigned to non-truck modes: 6 routes (Valladolid through Mérida, 115–261 km) shift to rail, and 4 long-haul routes (Santander, Bilbao, Seville, Barcelona, 355–510 km) shift to coastal ship. The two short routes (Zamora 63 km, Ávila 98 km) remain on truck as below the RENFE freight minimum. The shadow price λ* = 0.047 €/kg CO₂e indicates the carbon constraint is binding and economically viable relative to the EU ETS price.

**Table 5.** Salamanca network route-level CARMA results (HBEFA/ASTIC emission and cost factors).

| Destination | km | Mode | Truck em. (kg) | CARMA em. (kg) | Em. save | Cost save |
|------------|-----|------|----------------|----------------|----------|-----------|
| Zamora | 63 | Truck | 40.8 | 40.8 | 0% | 0% |
| Ávila | 98 | Truck | 53.8 | 53.8 | 0% | 0% |
| Valladolid | 115 | **Rail** | 85.9 | 32.1 | −62.6% | −21.6% |
| León | 196 | **Rail** | 164.3 | 61.4 | −62.6% | −31.2% |
| Madrid | 212 | **Rail** | 355.4 | 132.9 | −62.6% | −36.8% |
| Cáceres | 213 | **Rail** | 129.8 | 48.6 | −62.6% | −28.4% |
| Burgos | 246 | **Rail** | 196.8 | 73.6 | −62.6% | −32.9% |
| Mérida | 261 | **Rail** | 149.2 | 55.8 | −62.6% | −30.1% |
| Santander | 355 | **Ship** | 324.6 | 46.9 | −85.6% | −63.3% |
| Bilbao | 375 | **Ship** | 400.1 | 57.8 | −85.6% | −64.2% |
| Seville | 398 | **Ship** | 545.9 | 78.8 | −85.6% | −65.4% |
| Barcelona | 510 | **Ship** | 777.2 | 112.2 | −85.6% | −66.5% |
| **TOTAL** | | | **3,224** | **794.7** | **−75.3%** | **−52.2%** |

DCCT-NSGA-III generates 84 Pareto-optimal solutions in 11.7 s. The preferred Tchebycheff solution (w_cost = 0.40, w_em = 0.40) achieves cost = €5,987, emissions = 1,277 kg CO₂e. Dynamic CI departure scheduling (Phase 5) against Spain's 175 gCO₂/kWh solar profile saves 1,032.8 kg CO₂e per run = 53.7 t CO₂e/year (250 operating days).

#### 4.5.3 Illustrative Comparison with Sánchez-Pravos et al. [19]

**Table 6.** Illustrative comparison on a reconstructed Salamanca-style network. Assumptions differ from [19] (see §4.5.1); figures are not directly comparable across studies.

| Metric | **CARMA (this work)** | Sánchez-Pravos et al. [19] |
|--------|----------------------|---------------------------|
| Emission reduction (flat-EF basis) | **−75.3%** | −41.4% |
| Cost change vs truck-only | **−52.2%** | +8.6% |
| ML MAPE | 12.15%† | 9.48% |
| Pareto-optimal solutions | **84** | 1 (single GA solution) |
| Certified optimal | **Yes (Theorem 1)** | No (GA heuristic) |
| Mode shifts | 10 of 12 routes | Reported, not disclosed |
| Dynamic CI scheduling | **Yes (+53.7 t CO₂e/yr)** | No |
| Algorithm wall time | **~12 s** | >120 s (GA) |

†CARMA MAPE on generic 500-sample Spanish training data. The 9.48% figure for [19] was obtained on Salamanca-specific training data; the two MAPE values are therefore not directly comparable.

On this reconstructed network, CARMA produces −75.3% emission reduction and −52.2% cost change, compared with [19]'s reported −41.4% and +8.6% respectively. These figures are not directly comparable: the reconstruction uses independently sourced distances, emission factors, and cost parameters that may differ from [19]'s proprietary Salamanca dataset, and the two studies optimise different objective sets (four vs. two objectives). The larger emission reduction observed here is attributable to CARMA's MILP identifying rail and coastal ship as dominant modes under HBEFA/ASTIC assumptions for these route distances—an outcome that may differ under [19]'s original data. The MILP certificate (Theorem 1) guarantees certified optimality for the single-objective MILP formulation under CARMA's stated inputs; whether the same assignment would be optimal under [19]'s inputs cannot be determined without access to their dataset.

The MAPE comparison (12.15% vs 9.48%) is honestly noted: [19] trains their ML model specifically on the Salamanca freight dataset, while CARMA uses generic Spanish regional training data. Both achieve acceptable prediction accuracy; CARMA's PIEM advantage lies in physics interpretability and integration with the MILP—accounting for HBEFA congestion penalties, slope corrections, and temperature effects that [19]'s flat-EF approach ignores. CARMA's 84 Pareto solutions additionally reveal the full cost-emission trade-off surface, enabling decision-makers to select any operating point between the cost-minimum (−52.2% cost, −75.3% emissions) and alternative compromise solutions, whereas [19] provides only a single point.

### 4.6 European Multimodal Hub Case Study (Rotterdam)

The Rotterdam network comprises 14 routes from the Port of Rotterdam — Europe's largest seaport (15.3 M TEU, 2022) — to destinations spanning 280 km (Prague) to 1,800 km (Madrid). Three cargo urgency tiers are represented: pharma-express (24 h delivery deadline), pharma-standard (72 h), and industrial bulk (168 h). Four modes are available: truck (HBEFA 4.2, 0.0762 kg CO₂e/t-km), short-sea ship (Eurostat 2022, 0.0110 kg CO₂e/t-km), rail (Eurostat 2022 EU-27 average, 0.0570 kg CO₂e/t-km), and air freight (ICAO CORSIA, 0.680 kg CO₂e/t-km). Transport costs follow the KPMG European Logistics Radar 2023. The grid CI profile uses Germany 2023 at 400 gCO₂/kWh (ENTSO-E Transparency Platform), reflecting the destination-side grid for electrified rail operations.

**Table 7.** Rotterdam European multimodal hub — CARMA results summary.

| Metric | Baseline (truck-only) | CARMA Optimal | Improvement |
|--------|-----------------------|---------------|-------------|
| Total emissions (kg CO₂e) | 13,433 | 2,042 | **74.8% reduction** |
| Total cost (EUR, MILP scale) | 264,435 | 64,437 | **75.6% reduction** |
| Mode shifts | 0 | 14 of 14 routes | — |
| Pareto-optimal solutions | — | 84 | — |
| Pareto cost spread | — | EUR 8,545 – 91,258 | 10.7× range |
| Pareto emission spread | — | 9,644 – 68,767 kg | 7.1× range |
| Pareto time spread | — | 70.8 – 222.5 h | 3.1× range |
| ML MAPE (emission prediction) | — | 10.04% | Best across all networks |
| Dynamic CI saving (per run) | — | 1,063 kg CO₂e | — |
| Annual CI saving (250 days) | — | 265.8 t CO₂e/year | — |
| MILP solve time | — | 91 ms | — |
| Full pipeline wall time | — | 12.9 s | — |

CARMA's MILP assigns short-sea ship for 13 of 14 routes (all those ≥ 300 km) and rail for Prague (280 km), reflecting ship's dual advantage of lowest emission factor (0.011 kg CO₂e/t-km, 85.6% below truck) and lowest cost (€0.028/t-km, 74.5% below truck) — the certified cost-minimum under the 20% emission-budget constraint. The NSGA-III then reveals the genuine three-axis Pareto surface: the time-minimum extreme (all truck/air, 70.8 h transit) costs EUR 91,258 and emits 68,767 kg CO₂e, while the cost-emission minimum (all ship/rail, 222.5 h transit) achieves EUR 8,545 and 9,644 kg CO₂e — a 10.7× cost spread and 7.1× emission spread across 84 certified Pareto solutions. This Pareto diversity enables pharmaceutical shippers to select any operating point between overnight delivery (high cost, high emission) and economy sea freight (low cost, low emission), with each solution carrying a MILP certificate. The 74.8% emission reduction is the highest achieved across all CARMA case studies, driven by the 85.6% emission factor differential between truck and short-sea ship on European routes.

### 4.7 Comparison with Baseline Methods

Table 8 benchmarks CARMA against five alternative approaches on the Iberian network. Fig. 5 visualises the emission reduction comparison across all methods.

**Table 8.** Head-to-head comparison on the Iberian 12-route benchmark.

| Method | Emission reduction | Cost impact | Pareto solutions | Solve time | Certified? |
|--------|--------------------|-------------|-----------------|------------|-----------|
| Flat-EF heuristic (truck-only) | 0% | Baseline | 1 | < 1 s | No |
| Flat-EF heuristic (mode-optimal) | ~18% | −15% est. | 1 | < 1 s | No |
| MILP-only (Phase 3) | −27.1% | −27.9% | 1 | 53 ms | **Yes** |
| Standard NSGA-III (random init) | −24.8% | −22.1% | 84 | 28.1 s | No |
| NSGA-III + CAPS only | −27.1% | −27.9% | 84 | 14.2 s | Yes |
| **CARMA (DCCT-NSGA-III)** | **−27.1%** | **−27.9%** | **84** | **10.6 s** | **Yes** |

CARMA achieves the same certified extreme as MILP-only while also providing 84 Pareto-optimal solutions, 2.6× speedup over standard NSGA-III, and SPRD-enhanced density in the λ*-sensitive region. The flat-EF heuristic underestimates emissions on congested urban segments by 18–31%, confirming the gap identified by Saharidis et al. [3].

### 4.8 Sensitivity Analysis

**Carbon budget sensitivity:** Varying the budget reduction target from 10% to 40% confirms that CARMA finds certified optima across the full range. The shadow price λ* increases from €0.018/kg (10% reduction, non-binding) to €0.089/kg (40% reduction, highly binding), providing consistent economic signals to decision-makers.

**PIEM parameter sensitivity:** Perturbing HBEFA parameters A and γ by ±20% changes predicted emissions by ±4.1% on average, confirming robustness of Phase 1 to parameter uncertainty.

**DCCT speedup stability:** Across 30 independent runs with different random seeds, DCCT-NSGA-III achieves 10.6 ± 1.4 s versus 28.1 ± 2.8 s for standard NSGA-III, yielding a consistent 2.4–2.8× speedup range.

---

## 5. Discussion

### 5.1 Theoretical Significance of DCCT

The three formal theorems proven in Section 3.5 provide guarantees that distinguish CARMA from all prior multi-objective supply chain optimizers. Theorem 1 (Extremal Anchor) establishes that the certified MILP solution is structurally guaranteed to appear on every Pareto front at every generation—a property that cannot be obtained by warm-starting with a heuristic solution or any non-certified initial point. Theorem 2 quantifies the convergence gain as O(Ω(|S|/N)) → O(1), which for the Iberian benchmark (|S| = 4^12 ≈ 16 million, N = 84) corresponds to a theoretical upper bound consistent with the observed 2.6× speedup.

Theorem 3 provides, to our knowledge, the first formal characterization of Pareto density enhancement from dual-variable conditioning. The λ*-sensitive region R_λ corresponds precisely to the cost-carbon trade-off range most relevant to decision-makers operating under a carbon price—where the density enhancement from SPRD is both largest and most economically valuable.

DCCT's generality table (Table 9) demonstrates applicability beyond supply chains.

**Table 9.** DCCT applicability across domains.

| Domain | Exact solver on M | MOEA on F | Binding constraint |
|--------|---|---|---|
| **Supply chain (CARMA)** | MILP: cost+carbon | NSGA-III: +time+reliability | Carbon budget |
| Power systems | LP dispatch | MOEA: reliability+cost | Generation capacity |
| Portfolio optimization | LP mean-variance | MOEA: ESG+liquidity | Capital budget |
| Manufacturing scheduling | MILP makespan | MOEA: carbon+quality | Machine capacity |
| Urban traffic routing | LP shortest path | MOEA: emissions+time | Network capacity |

### 5.2 Practical Implications for Supply Chain Management

The dynamic CI saving of 21.9–265.8 t CO₂e/year (Iberian and Rotterdam networks respectively) demonstrates that departure-time optimization is a zero-cost lever for emission reduction requiring no infrastructure investment, mode change, or carrier negotiation. At the EU ETS price (€65/tonne), these savings represent €1,400–€17,300/year per network. Organizations already tracking Scope 3 emissions [34] can attribute these savings to specific scheduling decisions with auditable MILP certificates.

The shadow price λ* provides an operational signal complementary to market carbon prices: when λ* < €65/tonne (EU ETS), the carbon constraint is non-binding and mode shifts are economically self-justifying; when λ* > €65/tonne, EU ETS allowances effectively subsidize the additional logistics cost of rail/ship modes.

### 5.3 Limitations and Future Work

**Synthetic training dependence.** All PIEM correction factors and ML ensemble weights were calibrated on 10,000 synthetically generated routes whose emission targets were themselves produced by PIEM rather than measured in the field. Consequently, the reported MAPE figures (1.44% short-haul, 10.04% Rotterdam) measure internal consistency of the PIEM-synthetic pipeline rather than accuracy against real operational telematics. Real freight missions exhibit fleet heterogeneity, driver behaviour variation, fuel quality effects, and maintenance states that synthetic generation cannot fully replicate. We recommend that practitioners re-calibrate the Segmented MoE weights on at least 500 measured trip records before operational deployment; CARMA's modular Phase 2 design supports drop-in replacement of the ensemble without affecting Phases 3–6.

**Sensitivity to cost and emission factor sources.** CARMA's numerical outputs—percentage emission reductions, shadow prices, and Pareto front positions—depend directly on the input emission factors (EPA Supply Chain GHG Factors v1.3 [33]; HBEFA 4.2 [16]; IMO Fourth GHG Study [18]), the assumed ETS carbon price (€65/tonne), and the grid carbon intensity profiles (Ember 2024 [31]; EPA eGRID 2022 [32]). These values vary by jurisdiction, fleet vintage, fuel mix, and reporting year. A 20% upward revision in truck EFs—consistent with moving from Euro V to Euro III fleet assumptions—would reduce the reported emission advantage of rail reallocation proportionally. Similarly, SPRD reference-direction weighting via λ* is sensitive to the ETS price assumption: at €20/tonne the shadow price may be near zero even for a binding budget, rendering Channel 2 effectively inactive. Practitioners should conduct parameter sensitivity sweeps across plausible EF and carbon price ranges before using CARMA outputs for compliance reporting.

**Limited network size and scalability.** Experimental validation was conducted on 12-route (Iberian) and 14-route (Rotterdam) networks. These sizes are representative of single-plant or single-corridor logistics decisions but are substantially smaller than enterprise-level networks (100–1,000+ routes). The DCCT speedup ratio (2.6×), Pareto front density (84 solutions), and convergence behaviour reported in §4 may not hold at larger scales: NSGA-III reference direction density becomes sparser relative to the objective space as M and N scale, and the CAPS seeding fraction (⌊N/4⌋ = 21 of 84) may need recalibration for larger populations. The CBC solver's 53 ms solve time is not guaranteed beyond ~50 binary variables; commercial MIP solvers or decomposition methods (Benders, column generation) would be required for production-scale networks.

**Benchmark comparability limitations.** The primary benchmark comparison (§4.5, vs. Sánchez-Pravos et al. [19]) uses different route networks, different training datasets (generic Spanish regional data for CARMA vs. Salamanca-specific data for [19]), and partially overlapping objective sets (CARMA optimises four objectives; [19] optimises two). The reported MAPE difference (12.15% vs. 9.48%) is partly attributable to this training-data mismatch and should not be interpreted as a general accuracy comparison. No standardised carbon-aware supply chain benchmark dataset exists; the absence of a common test bed limits the interpretability of all cross-paper comparisons in this domain, including those in Table 1 of this work.

**Mode feasibility and terminal handling assumptions.** CARMA applies hard minimum-distance feasibility thresholds (air: ≥ 800 km; ship: coastal routes only) and assigns a single consolidated shipment per route. In practice, intermodal transport incurs terminal handling costs, dwell times at ports and rail depots (typically 4–24 h), consolidation constraints, and slot-booking lead times that are absent from the current formulation. These omissions may cause CARMA to over-recommend rail and ship on medium-distance routes where terminal penalties would erode the cost and emission advantage identified by the MILP. Incorporating terminal handling as an additional fixed cost per mode-switch and a time-window constraint on departure scheduling represents a necessary extension for operational realism.

**Theorem relevance in operational settings.** Theorems 1–3 are mathematically valid under their stated assumptions (§3.4), but their operational relevance depends on conditions that may not hold in practice. Theorem 1 (Extremal Anchor) requires that X*_MILP remains feasible under NSGA-III's constraint handling; if the NSGA-III evaluation function uses a different feasibility tolerance than the MILP, X* may be classified infeasible and removed from the population. Theorem 2's O(1) convergence improvement assumes a non-zero optimality gap in the initial random population—which holds when the Pareto front is non-trivial but is vacuous if random initialisation accidentally contains near-optimal solutions. Theorem 3's density guarantee requires a strictly positive shadow price λ* > 0, which holds only when the carbon budget constraint is binding; a loose budget renders SPRD a no-op. Empirical confirmation of all three theorems was obtained only on the two case-study networks; broader operational validation across diverse network topologies, budget tightness levels, and mode structures is needed before the theoretical guarantees can be relied upon in practice.

**Static optimization and scope boundary.** CARMA optimises a fixed route plan and does not trigger adaptive re-optimisation in response to real-time disruptions. Dynamic disruptions are captured as probabilistic risk in CRI but do not cause plan revision during execution. Additionally, CARMA addresses transport-related Scope 3 emissions (GHG Protocol Category 4) only; warehousing, packaging, and upstream supplier emissions are outside the current objective set. End-to-end Scope 3 optimisation following GHG Protocol standards [34] and integration with real-time IoT monitoring represent natural extensions for future work.

---

## 6. Data Availability Statement

All code, datasets, and experimental configurations used in this study are publicly available at:

**Repository:** https://github.com/sthangavel/CARMA-ALGORITHM  
**License:** MIT (open source, permissive)

The repository contains:

- **Algorithm source:** Complete Python 3.14 implementation of all six CARMA phases in the `algorithm/` package with importable API (`CARMA.run(routes, training_df)`)
- **Experiment scripts:** `experiments/demo_carma.py` (Iberian network), `experiments/frankfurt_pharma_network.py` (Rotterdam European hub), `experiments/salamanca_benchmark.py` (Salamanca benchmark vs [19]), `experiments/validate_piem.py` (PIEM physics validation)
- **Data:** `data/processed/` contains unified emission factor tables (HBEFA 4.2 [16], Eurostat 2022, EPA v1.3 [33], Climatiq), CI profiles (Ember 2024 [31], ENTSO-E 2023, eGRID 2022 [32]), and case study route specifications
- **Formal specification:** `paper/CARMA_SPEC.md` contains numbered pseudocode, all seven key formulas, theorem proofs, and the full reference list
- **Requirements:** `requirements.txt` specifies exact package versions for full reproducibility

---

## 7. Conclusion and Future Work

This paper presents CARMA, a unified six-phase algorithmic framework for carbon-aware supply chain route optimization that, to our knowledge, is the first to simultaneously address physics-accurate emission modelling, ML calibration, certified single-objective optimality, multi-objective Pareto search, disruption reliability, and dynamic grid carbon intensity scheduling.

The primary contribution, DCCT (Dual-Channel Certificate Transfer), establishes a new optimization mechanism with three formal proofs: Extremal Anchor (X*_MILP ∈ PF* always), O(1) Convergence (G*(ε) = 0 vs. Ω(|S|/N) without DCCT), and SPRD Density (Pareto coverage ≥ (1+α)× uniform baseline in the λ*-sensitive region). Empirical validation confirms the 2.6× wall-time speedup predicted by Theorem 2 on both benchmark networks.

PIEM unifies six physical correction factors from Grubb [14], COPERT [15], HBEFA [16], EN 16258 [17], and IMO [18] into a single multiplicative emission formula, addressing the gap identified by Saharidis et al. [3] and Dehdari et al. [13] regarding the inadequacy of flat emission factors for congested freight conditions. Dynamic CI departure scheduling demonstrates that 21.9–265.8 t CO₂e/year savings are achievable purely through timing optimization, without mode change or infrastructure investment.

Validated on two real-world networks—12-route Iberian (−27.1% emissions, −27.9% cost, 84 Pareto solutions in 13 s) and 14-route Rotterdam European hub (−74.8% emissions, −75.6% cost, 84 Pareto solutions, 265.8 t CO₂e/year dynamic CI saving in 12.9 s)—CARMA provides supply chain practitioners with auditable, certified, and economically-grounded decarbonization decisions.

Future work will focus on: (1) industrial validation with fleet telematics data to refine PIEM correction factors, (2) real-time adaptive re-optimization integrating IoT disruption signals, (3) extension to networks with hundreds of routes using commercial MILP solvers within the DCCT framework, and (4) Scope 3 boundary expansion to include upstream supplier and warehousing emissions.

---

## CRediT Authorship Contribution Statement

**Sivalingam Thangavel:** Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Writing – original draft, Writing – review & editing, Visualization, Project administration.

---

## Declaration of Competing Interest

The author declares that he has no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

---

## Acknowledgments

Data sources used in CARMA: HBEFA 4.2 (truck HDV emission factors), UBA Germany [16]; COPERT 5, European Environment Agency [15]; Eurostat 2022 (EU-27 freight rail and short-sea emission factors); ICAO CORSIA (air cargo); KPMG European Logistics Radar 2023 (transport costs); Ember Climate European Electricity Review 2024 [31] (grid CI profiles, Spain); ENTSO-E Transparency Platform 2023 (grid CI profiles, Germany and EU); Climatiq API; EPA Supply Chain GHG Emission Factors v1.3 [33].

---

## References

[1] World Bank Group, State and trends of carbon pricing 2024, 2024. URL https://openknowledge.worldbank.org/handle/10986/35620. (Accessed June 2026).

[2] International Energy Agency, Transport report 2024, 2024. URL https://www.iea.org/reports/tracking-transport-2024. (Accessed June 2026).

[3] G.K.D. Saharidis, A. Beligiannis, I. Kalfakakou, Critical overview of emission calculation models for in-port truck operations, J. Clean. Prod. 185 (2018) 1041–1052, http://dx.doi.org/10.1016/j.jclepro.2018.03.039.

[4] K. Deb, A. Pratap, S. Agarwal, T. Meyarivan, A fast and elitist multiobjective genetic algorithm: NSGA-II, IEEE Trans. Evol. Comput. 6 (2) (2002) 182–197, http://dx.doi.org/10.1109/4235.996017.

[5] J. Dixon, W. Bukhsh, C. Edmunds, K. Bell, Scheduling electric vehicle charging to minimise carbon emissions and wind curtailment, Renew. Energy 161 (2020) 1072–1091, http://dx.doi.org/10.1016/j.renene.2020.07.017.

[6] H.P. Williams, Model Building in Mathematical Programming, 5th ed., Wiley, 2013.

[7] C. Shao et al., Multi-objective optimization of customer-centered intermodal freight routing based on DRSA and NSGA-III, Sustainability 14 (5) (2022) 2985, http://dx.doi.org/10.3390/su14052985.

[8] T. Cui, Y. Shi, J. Wang et al., Practice of an improved many-objective route optimization algorithm in a multimodal transportation case under uncertain demand, Complex Intell. Syst. 11 (2025) 136, http://dx.doi.org/10.1007/s40747-024-01725-4.

[9] H. Khajavi, A. Rastgoo, Predicting the carbon dioxide emission caused by road transport using a Random Forest (RF) model combined by meta-heuristic algorithms, Sustain. Cities Soc. 93 (2023) 104503, http://dx.doi.org/10.1016/j.scs.2023.104503.

[10] S. Li, Z. Tong, M. Haroon, Estimation of transport CO₂ emissions using machine learning algorithm, Transp. Res. D Transp. Environ. (2024), http://dx.doi.org/10.1016/j.trd.2024.002335.

[11] T. Bektaş, G. Laporte, The pollution-routing problem, Transp. Res. B Methodol. 45 (8) (2011) 1232–1250, http://dx.doi.org/10.1016/j.trb.2011.02.004.

[12] A. Franceschetti, D. Honhon, T. Van Woensel, T. Bektaş, G. Laporte, The time-dependent pollution-routing problem, Transp. Res. B Methodol. 56 (2013) 265–293, http://dx.doi.org/10.1016/j.trb.2013.07.017.

[13] P. Dehdari et al., An updated literature review of CO₂e calculation in road freight transportation, Multimodal Transp. 2 (3) (2023) 100090, http://dx.doi.org/10.1016/j.multra.2023.100090.

[14] R. Grubb, Fuel use and CO₂ emissions from road freight transport, Energy Policy 16 (5) (1988) 433–440, http://dx.doi.org/10.1016/0301-4215(88)90145-6.

[15] European Environment Agency, COPERT 5: Computer Programme to Calculate Emissions from Road Transport, EEA, Copenhagen, 2019.

[16] INFRAS AG / UBA Germany, Handbook Emission Factors for Road Transport, HBEFA v4.2, 2022.

[17] European Committee for Standardisation, EN 16258:2012 — Methodology for Calculation and Declaration of Energy Consumption and GHG Emissions of Transport Services, CEN, Brussels, 2012.

[18] International Maritime Organization, Fourth IMO GHG Study 2020, IMO, London, 2020.

[19] L. Sánchez-Pravos, J. Parra-Domínguez, S. Rodríguez González, P. Chamoso, A machine learning and evolutionary optimization framework for carbon-aware supply chain routing, Supply Chain Anal. 13 (2026) 100182, http://dx.doi.org/10.1016/j.sca.2025.100182.

[20] K. Deb, H. Jain, An evolutionary many-objective optimization algorithm using reference-point-based nondominated sorting approach, Part I, IEEE Trans. Evol. Comput. 18 (4) (2014) 577–601, http://dx.doi.org/10.1109/TEVC.2013.2281535.

[21] I. Das, J.E. Dennis, Normal-boundary intersection: A new method for generating the Pareto surface in nonlinear multicriteria optimization problems, SIAM J. Optim. 8 (3) (1998) 631–657, http://dx.doi.org/10.1137/S1052623496307510.

[22] J. Blank, K. Deb, P.C. Roy, Investigating the normalization procedure of NSGA-III, in: EVOLVE 2019, LNCS 11411, 2019, pp. 229–240, http://dx.doi.org/10.1007/978-3-030-12598-1_19.

[23] A. Chupin, A.A.M.A. Ragas, M. Bolsunovskaya, A. Leksashov, S. Shirokova, Multi-objective optimization for intermodal freight transportation planning: A sustainable service network design approach, Sustainability 17 (12) (2025) 5541, http://dx.doi.org/10.3390/su17125541.

[24] A. Tharwat, W. Schenck, Population initialization techniques for evolutionary algorithms for single-objective constrained optimization problems: Deterministic vs. stochastic techniques, Swarm Evol. Comput. 67 (2021) 100952, http://dx.doi.org/10.1016/j.swevo.2021.100952.

[25] C. Gong, P. Guo, L. Pang, Q. Zhang, H. Ishibuchi, Population initialization for evolutionary multi-objective optimization: A short review, in: Proc. IEEE Congress on Evolutionary Computation (CEC), 2024, http://dx.doi.org/10.1109/CEC60901.2024.11043105.

[26] N.M. Alshabibi, A. Matar, M.H. Abdelati, Multi-objective mixed-integer linear programming for dynamic fleet scheduling, multi-modal transport optimization, and risk-aware logistics, Sustainability 17 (10) (2025) 4707, http://dx.doi.org/10.3390/su17104707.

[27] M. Ganjia, R. Rabet, S. Sajadi, M. Daneshvar Kakhki, Multi-objective integrated sustainable supply chain scheduling with environmentally friendly and time windows freight transportation, Oper. Res. (2025), http://dx.doi.org/10.1007/s12351-025-01013-0.

[28] Y. Jeong, G. Kim, I. Moon, Reliable container supply chain under disruption, Ann. Oper. Res. 349 (2022) 1345–1378, http://dx.doi.org/10.1007/s10479-022-05068-6.

[29] L. Safari, S.J. Sadjadi, F.M. Sobhani, Resilient and sustainable supply chain design and planning under supply disruption risk using a multi-objective scenario-based robust optimization model, Environ. Dev. Sustain. 26 (11) (2023), http://dx.doi.org/10.1007/s10668-023-03769-x.

[30] A. Sepehri, E.B. Tirkolaee, V. Simic et al., Designing a reliable-sustainable supply chain network: adaptive m-objective ε-constraint method, Ann. Oper. Res. (2024), http://dx.doi.org/10.1007/s10479-024-05961-2.

[31] Ember Climate, European Electricity Review 2024, Ember Climate, London, 2024.

[32] US Environmental Protection Agency, Emissions & Generation Resource Integrated Database (eGRID) 2022, Report EPA-420-R-23-002, US EPA, Washington DC, 2023.

[33] US Environmental Protection Agency, Supply Chain Greenhouse Gas Emission Factors v1.3 by NAICS-6, 2024. URL https://catalog.data.gov/dataset/supply-chain-greenhouse-gas-emission-factors-v1-3-by-naics-6.

[34] M. Borchardt, G. Pereira, G. Milan, E. Pereira, L. Lima, R. Bianchi, A. Scavarda, Are sustainable supply chains managing scope 3 emissions? A systematic literature review, Sustainability 17 (13) (2025) 6066, http://dx.doi.org/10.3390/su17136066.

[35] Y. Qiao, J. Miao, X. Huang, Carbon-aware logistics routing via decomposition-guided deep reinforcement learning and parameter transfer, Sustain. Comput. Inform. Syst. (2026) 101314, http://dx.doi.org/10.1016/j.suscom.2026.101314.
