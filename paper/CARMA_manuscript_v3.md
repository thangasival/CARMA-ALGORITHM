# Marginal Abatement Cost as a Carbon Decision Signal in Intermodal Supply Chain Routing: A Parametric MILP Framework for Mode Shift, Allowance Purchase, and Regime Classification

## Highlights

- Parametric MILP gives step-function MAC curves; compliance regime is topology-driven
- At 65 €/t ETS, domestic MAC is 3.8–67× ETS — allowance purchase preferred over shift
- Maritime co-benefit: 77% emission cut, 56% cost saving — no carbon instrument needed
- Five-regime taxonomy: mode shift, parity, buy, co-benefit, or infeasible target

---

## Keywords

Marginal abatement cost; Parametric MILP; Carbon compliance regime; Intermodal supply chain routing; Carbon decision analytics; Mode shift; Carbon allowance purchase; Multi-objective optimization; Co-benefit decarbonization

---

## Abstract

Physical mode shift dominates intermodal carbon strategy in the optimization literature, but whether it is economically rational depends on a comparison the literature rarely makes: the network's own marginal abatement cost (MAC) against the market price of carbon allowances. Prior routing studies — including in this journal — optimize assignments without classifying whether mode shift or allowance purchase is the rational compliance response. This paper closes that gap by applying RHS-parametric MILP [41] to the carbon-budget constraint: finite-difference MAC curves are estimated from sequential integer solutions — bypassing LP relaxation duals, which equal zero in all 33 base-archetype solves — and each (network, budget) point is classified into five carbon-compliance regimes: mode shift preferred, parity, allowance purchase preferred, co-benefit decarbonization, or infeasible. Applied to three intermodal network structural classes, the domestic truck-rail MAC ranges from 245 to 4,366 €/t — 3.8 to 67 times the EU ETS 2024 price of 65 €/t — placing every domestic budget point in the allowance-purchase-preferred regime. Maritime-accessible networks show the opposite: ship is cheaper and lower-emission on long hauls, so cost optimization already decarbonizes the fleet without any carbon instrument. Hub networks face a hard ceiling at 25% reduction beyond which no feasible modal alternative exists. Across 150 generated variants (1,650 MILP solves), within-class consistency is confirmed (a controlled resampling study, not a population-frequency estimate): rail-limited domestic networks split 54% non-binding and 46% allowance-preferred at 20% budget — 0% shift-preferred in either case, with median binding-case MAC of 1,398 €/t (21× ETS); all maritime variants remain non-binding; 52% of hub variants are infeasible. The five-regime taxonomy classifies these as topology-driven network conditions; its central output is the network-specific break-even carbon price that determines whether mode shift, allowance purchase, or network redesign is rational.

---

## 1. Introduction

### 1.1 The Carbon Compliance Decision Problem

Supply chain transportation generates approximately 16% of global CO₂ emissions [1]. Under the EU Emissions Trading System (ETS), organizations face a concrete compliance choice for every unit of freight: should they reduce emissions through physical mode shifts (truck to rail or ship), purchase ETS allowances on the carbon market, or achieve operational savings through timing adjustments? Each pathway has a different cost structure, and the rational choice depends on the internal cost of abatement relative to the market price of carbon.

This decision is analytically non-trivial. Mode shifts involve one-time reconfiguration of logistics networks with heterogeneous route economics. Allowance purchase provides continuous, price-linear compliance at the market rate. A logistics manager imposing a carbon budget — whether voluntary or regulatory — needs an instrument to identify which pathway is economically rational for the specific network.

### 1.2 The Marginal Abatement Cost Decision Gap

The analytical instrument required is the marginal abatement cost (MAC) of the logistics network: how much does it cost, in additional logistics expenditure, to achieve one more unit of emission reduction? In continuous linear models, the LP-relaxation dual on the carbon-budget constraint equals this cost directly. In mixed-integer programmes — the appropriate formulation for discrete mode assignment — this identity breaks down. Williams [2] establishes that the integer-programme value function is non-convex and piecewise constant; LP duals at the integer optimal are therefore often zero or undefined, a relaxation artifact rather than a managerial signal. More sophisticated MIP sensitivity concepts exist [25, 26, 29] but are not routinely exposed in standard logistics MILP workflows. The practical consequence: the CBC/PuLP workflow reported zero LP-relaxation dual values for all 33 base-archetype carbon-budget constraints, even when tightening the budget forced costly mode shifts. A logistics manager running a carbon-constrained MILP is left without a model-derived signal about whether to shift modes or buy allowances. The parametric finite-difference method addresses this directly: applying RHS-parametric MILP [41] to the carbon-budget constraint — solving at adjacent budget levels and differencing the integer solutions — recovers a managerial MAC estimate without relying on LP dual outputs, regardless of solver choice.

### 1.3 Research Questions

**RQ1.** How does the marginal abatement cost of a carbon-constrained intermodal routing network change with carbon budget tightness, modal availability, and network structure?

**RQ2.** When does the endogenous marginal abatement cost support physical mode shifting rather than market-based carbon allowance purchase, and when is neither required (co-benefit regime)?

### 1.4 Contributions

The central empirical finding is that domestic truck-rail mode shift is not economically rational at any realistic near-term carbon price: MAC is 245–4,366 €/t (4–67× EU ETS 2024), placing every tested budget point in the allowance-purchase-preferred regime. The framework that generates this finding is shadow-price-motivated but not shadow-price-dependent: it begins from the economic interpretation of a carbon shadow price, then replaces unreliable MIP duals with finite-difference MAC estimated from parametric MILP solutions.

This paper contributes a carbon decision analytics framework that links integer optimization outputs to managerial carbon-compliance choices. Its central object is not the route plan but the compliance regime: a classification of the (network, budget) point into mode shift preferred, parity, allowance purchase preferred, co-benefit decarbonization, or infeasible, derived by comparing the network's endogenous marginal abatement cost curve to observable carbon prices. Two results give this framework its weight. First, the regime is governed by network structure: in the domestic structural class, the Salamanca base case sits in the allowance-preferred regime across all tested budget levels (MAC 245–4,366 €/t, 4–67× ETS price); in the generated domestic family, 46% of instances are allowance-preferred and 54% non-binding at 20% budget — 0% shift-preferred in either case — consistent with prior firm-level and modal-inelasticity findings [31, 38], now derived endogenously from network topology. Second, the framework identifies when no carbon signal is needed at all: in maritime-accessible networks the cost-optimal assignment already satisfies tightening budgets (co-benefit decarbonization, constraint non-binding), and in hub networks a hard abatement ceiling appears beyond which no modal alternative exists. The analytical contribution is therefore a decision rule and a regime taxonomy keyed to the discrete modal topology of a specific network — not a new optimization algorithm.

Three specific bounded contributions follow:

1. **A network-structure-conditioned carbon-compliance regime taxonomy for intermodal routing** (primary). The framework converts parametric MILP-derived MAC into five operational regimes and, on three network archetypes used as structured illustrations rather than empirical validation cases, maps the regime boundaries over budget levels and carbon-price scenarios and characterizes the structural conditions — modal availability, long-haul share, abatement ceiling — that determine which regime a network occupies. Because realized emission rates and abatement costs vary strongly across corridors and countries [35], the archetype results are presented as existence-and-mechanism demonstrations whose external magnitudes require corridor-specific calibration; the transferable claim is the regime structure, not the specific MAC values. The managerial payload is the counter-orthodox finding that physical mode shift is the rational response only for a structurally identifiable subset of networks; for others, allowance purchase, co-benefit recognition, or network redesign dominates.

2. **Finite-difference MAC via RHS-parametric MILP applied to the carbon-budget constraint** (methodological adaptation). RHS-parametric MILP — solving the integer programme at point values of a right-hand-side parameter and joining results across flat regions — is an established operations-research technique (Jenkins [41]; see also [2, 25, 26, 29]). This paper applies that technique to the carbon-budget constraint in intermodal mode assignment, where naïve LP-relaxation duals are structurally unreliable (zero in all 33 base-archetype solves), and repurposes the resulting step-function value differences as a managerial MAC signal. The contribution is not the parametric MILP procedure itself but its decision-analytics transposition to carbon compliance: comparing the network-specific MAC against an observable carbon price to produce a regime classification.

The most directly comparable model-derived MAC applications — firm-level abatement against EU ETS prices [38] and step-wise MAC from energy-system optimization [22] — operate over technology and fuel portfolios at a single facility; neither addresses multi-modal routing-network topology, endogenous break-even carbon prices from discrete modal alternatives, or a five-regime operational taxonomy. The contribution is a decision-analytics synthesis, not a new optimization method: applying RHS-parametric MILP [41] to the carbon-budget constraint of an intermodal routing model, comparing the resulting step-function MAC to an observable carbon price, and packaging the outcome as five named regime labels that convert MILP outputs into a compliance instrument choice.

### 1.5 Scope and Exclusions

This paper is not the first carbon-aware routing study in this journal — Sánchez-Pravos et al. [3] is directly comparable prior art, sharing the Salamanca network dataset. The methodological distinction is purposive: their framework optimizes route assignments using ML-predicted emission factors; this framework derives the endogenous marginal abatement cost of those assignments and uses it to classify whether mode shift or allowance purchase is the rational compliance response. The decision framework is designed for tactical intermodal planning with identifiable modal alternatives and binding emission constraints; it is not a real-time routing method. The emission estimation used (physics-informed multi-factor formula) is not field-validated against telematics and should not be used for regulatory reporting without re-calibration. LP shadow prices from mixed-integer solvers are not the primary analytical instrument; the parametric MAC approach is.

### 1.6 Paper Structure

Section 2 reviews related work and positions the contribution. Section 3 develops the MAC decision framework. Section 4 presents the optimization model. Section 5 describes the experimental design. Section 6 reports results. Section 7 discusses theoretical and managerial implications. Section 8 concludes.

---

## 2. Literature Review

### 2.1 Carbon-Constrained Supply Chain Optimization

Carbon budgets in supply chain models are most commonly imposed as hard constraints in MILP or multi-objective formulations. Bektaş and Laporte [13] formulated the Pollution-Routing Problem with speed-dependent emission costs, establishing the link between logistics cost and carbon performance. Alshabibi et al. [4] applied multi-objective MILP for fleet scheduling under emission constraints, reporting 23% cost and 33% emission improvement. Ganjia et al. [8] combined MILP with NSGA-II for sustainable production scheduling with emission caps. These studies produce optimal mode assignments but do not extract or use the marginal cost of the emission constraint as a decision signal.

Multi-objective evolutionary approaches for intermodal routing have been developed by Shao et al. [5] (four-objective NSGA-III for green freight with uncertain time-windows) and Cui et al. [6] (many-objective routing under uncertain demand). Demir et al. [28] develop a bi-objective model for European hinterland intermodal freight and find that costs need not be greatly compromised to achieve significant emission reduction — a co-benefit result their model cannot explain analytically. Bouchery et al. [21] show that maximizing modal shift is harmful for both cost and carbon objectives and that a carbon-optimal level of modal shift exists; they do not extract a MAC curve to identify it. Hoen et al. [32] construct an emissions–profit frontier for voluntary carbon targets through mode switching across multiple carriers; the frontier is not converted into a network-specific break-even carbon price or allowance-purchase decision rule. Sánchez-Pravos et al. [3], the directly comparable prior work in this journal, achieved 41.4% emission reduction on a Salamanca logistics network using RF-XGBoost emission prediction with genetic-algorithm routing. The boundary is purposive: their framework answers *what route assignment minimizes cost and emissions?* — a routing optimization problem; the present framework answers *what is the marginal cost of each emission-reduction step, and does it justify mode shift or allowance purchase at the prevailing carbon price?* — a compliance decision problem. They produce no MAC, no break-even price, and no regime classification. The present paper uses the same Salamanca network as one structured archetype to allow direct comparison while contributing the compliance decision layer that their approach leaves open. None of these studies estimate or use marginal abatement cost.

### 2.2 Marginal Abatement Cost in Operations Research and Logistics

Marginal abatement cost (MAC) curves originate in climate economics as representations of the cost of reducing one additional unit of CO₂e, ordered from cheapest to most expensive opportunity (McKinsey Global Institute, 2009; IPCC AR6 WGIII, 2022). Kesicki and Strachan [17] provide the canonical critical assessment of MAC methodology, distinguishing expert-elicited from model-derived curves and asserting that model-derived curves are more defensible for evaluating incentive-based instruments such as carbon pricing; they also identify key limitations — omission of option interactions, inconsistent baselines, limited uncertainty treatment — that any operational MAC implementation must address. Huang et al. [24], in a comprehensive review of MAC estimation approaches across stakeholder types and decision contexts, confirm that bottom-up engineering methods remain the dominant and most appropriate approach for sector-level abatement decisions, including logistics. In climate policy analysis, MAC curves inform decisions about which emission reductions are cost-effective relative to a prevailing carbon price: if the MAC of a given abatement measure is below the carbon price, the measure is economically justified; otherwise, purchasing allowances is cheaper. This comparison is routine at the economy or sector level but has not been operationalized for individual logistics networks.

In operations research, MAC-related concepts appear in energy optimization (unit commitment, dispatch) and in facility carbon budgeting, but their application to intermodal supply chain routing is limited. Ricci et al. [23], in a systematic review of transport sector GHG mitigation cost applications, explicitly confirm "a significant research gap in the freight sector, which is largely overlooked compared to passenger transport" in MAC analysis. Dekker et al. [16] survey green logistics operations research and identify the trade-off between logistics cost and carbon emissions as a central open problem, but do not construct MAC curves. Kaack et al. [20] survey global decarbonization potential through freight modal shift and find that rail shift is achievable only under specific corridor and infrastructure conditions; they do not estimate the MAC of that shift for individual networks. Mencaroni et al. [15] develop parametric emission-cost analysis for manufacturing scheduling and identify break-even carbon prices for energy-intensive operations, but for a single-facility, single-mode problem without multi-modal assignment or comparison to carbon markets; Glenk et al. [33] extend model-derived abatement cost curves to firm-level EU ETS compliance (discussed below). No prior intermodal routing paper, to our knowledge, constructs a parametric MAC curve from sequential MILP solves and uses it to generate mode-shift versus allowance-purchase decision thresholds at the network level.

Misconel et al. [22] derive step-wise MAC from energy-system sequential optimization — the same mechanism as modal assignment, but for technology and fuel portfolios rather than freight routing. Glenk et al. [33] construct firm-level abatement cost curves calibrated to the EU ETS (in press); their abatement options are production and capture technologies at a single facility. Neither yields a five-regime taxonomy or network-specific break-even price. The allowance-purchase conclusion itself is prior art: Rekker et al. [38] find median firm-level MAC of 429 €/t — far above ETS prices — so most chemical producers prefer to buy. The domestic truck-rail result (245–4,366 €/t) is the routing-network analogue; the contribution is its endogenous derivation from network topology and embedding in the five-regime taxonomy.

At the network level, Bouchery et al. [21] show a carbon-optimal level of modal shift exists below the maximum achievable, without deriving the MAC that identifies it. Boehm et al. [31] find 100 €/t has "insignificant impact" on European truck-to-rail mode share — consistent with this paper's MAC range. Flodén et al. [30] find that modal shift away from RoRo shipping requires carbon prices above 90–150 €/t, confirming that corridor-specific break-even thresholds can far exceed observed ETS prices. Liu et al. [27] document co-benefit decarbonization in Chinese inland waterway freight (the Regime 4 mechanism). Lagouvardou et al. [39] identify a carbon-price turning point for a binary hub-relocation decision in maritime liner service; their analysis covers one binary reconfiguration, not a continuous MAC curve or multi-regime classification.

### 2.3 Research Gap and Positioning

The preceding literature reveals that the building blocks of this paper exist separately. Intermodal routing models optimize cost and emissions but rarely convert the carbon constraint into a managerial compliance signal. MAC curves compare abatement options to carbon prices but are mainly used in energy, industry, and aggregate transport-policy analysis rather than network-specific freight routing. Integer-programming theory explains why conventional shadow prices are unreliable for discrete mode-assignment problems, but this insight is not operationalized in sustainable logistics decision support. The literature therefore leaves a specific decision-analytics gap. Intermodal routing models show how carbon constraints or prices change routing outcomes, while MAC studies estimate abatement costs at sectoral or technology levels. What remains underdeveloped — and has remained open as a logistics decision-analytics problem since Dekker et al. [16] placed cost-emission trade-offs in freight transport on the research agenda in 2012 — is the middle layer: transposing the step-wise MAC logic that is structurally correct for discrete assignments from energy-technology portfolios to multi-modal routing networks, and using the resulting network-specific MAC curve to determine whether a logistics manager should shift modes, buy allowances, recognize co-benefit decarbonization, or redesign the network because the target is infeasible. This gap is narrow and must be stated precisely, because the adjacent concept of carbon-price-induced regime thresholds is well established. Supply-chain-planning models have reported inflection points in the cost–emission response to carbon pricing since Zakeri et al. [36]; transport mode-selection models have derived policy-dependent mode-shifting thresholds since Chen et al. [37]; Chen et al. [42] show discontinuous road-to-rail and rail-to-waterway transitions at specific carbon-tax increments for multimodal freight networks; Yin et al. [43] trace multimodal network modal-mix transitions under alternative carbon price scenarios; multimodal network-design MILPs show that below a threshold cap, carbon procurement becomes necessary [40]; and Noguchi [34] gives a formal existence proof of discontinuous modal-mix regimes on capacity-constrained multimodal networks. The present paper does not claim to discover regime thresholds. It claims the narrower and previously unfilled step: constructing the network-specific MAC curve that *locates* those thresholds for an intermodal-routing MILP, comparing it against observable carbon markets, and packaging the result as a five-regime operational taxonomy with named decision rules.

To the best of our knowledge, although regime-threshold behaviour under carbon pricing is established in adjacent literatures [34, 36, 37, 40, 42, 43], no prior intermodal-routing study has derived a network-specific MAC curve from RHS-parametric MILP and converted it into an operational five-regime carbon-compliance taxonomy covering mode shift, allowance purchase, co-benefit decarbonization, and infeasible targets.

**Table 1. Decision outputs produced by prior routing models versus the proposed framework.**

| Output | Conventional carbon-aware routing | Bi-objective / Pareto routing | Proposed MAC-regime framework |
|---|:---:|:---:|:---:|
| Optimal route or mode assignment | Yes | Yes | Yes |
| Cost and emission totals | Yes | Yes | Yes |
| Pareto trade-off front | No / limited | Yes | No |
| Network-specific MAC | No | No | Yes |
| Break-even carbon price | No | No | Yes |
| Mode-shift vs allowance-purchase rule | No | No | Yes |
| Co-benefit / non-binding regime identification | Usually implicit | Usually implicit | Explicit |
| Infeasible-target diagnosis | Solver status only | Solver status only | Explicit managerial regime |

**Table 2.** Comparison of related methods on key analytical dimensions.

| Method | MAC-to-regime signal | Decision rules | MILP certificate |
|--------|---------------------|----------------|-----------------|
| Bektaş & Laporte [13] | No | No | No |
| Bouchery et al. [21] | No (carbon-optimal shift) | No | No |
| Hoen et al. [32] | No (emissions–profit frontier) | No | No |
| Demir et al. [28] | No | No | No |
| Shao et al. [5] | No | No | No |
| Sánchez-Pravos et al. [3] | No | No | No |
| Alshabibi et al. [4] | No | No | Yes |
| Mencaroni et al. [15] | Partial (scheduling) | No | No |
| **This paper** | **Yes (adapted parametric MILP)** | **Yes (5 regimes)** | **Yes** |

---

## 3. Carbon Compliance Decision Framework

### 3.1 The Three-Pathway Carbon Compliance Problem

A logistics manager operating under a carbon emission budget B (kg CO₂e per planning period) faces two primary compliance pathways:

1. **Physical mode shift**: Reassign one or more routes from truck to rail or ship. This reduces emissions by changing the transport mode but incurs route-specific cost premiums (terminal handling, frequency constraints, longer transit times).

2. **Carbon allowance purchase**: Purchase EU ETS allowances at market price π (€/tonne CO₂e) to cover the emission overage. The cost is linear in the gap between actual emissions and budget.

The rational choice between these pathways depends on a single comparison: is the internal marginal cost of achieving the required emission reduction (λ̂, €/kg CO₂e) higher or lower than the carbon market price π (quoted in €/t CO₂e)? For direct comparison, the framework re-expresses λ̂ in the same units as π: the *endogenous network break-even carbon price* B*(r) = λ̂(r) × 1000 (€/t CO₂e). B*(r) is not a construct distinct from λ̂(r) — it is the MAC rescaled for comparison to the observable carbon price; the economic novelty is the comparison rule and the five-regime taxonomy that operationalizes it, not the unit conversion itself. When π exceeds B*, mode shift is the rational response; when π falls below B*, allowance purchase is rational. Unlike break-even prices derived from technology-portfolio models — which read abatement costs from an external menu — B* is endogenous to the specific network: it is determined by the discrete modal alternatives available and varies with both budget level and modal cost structure. The five-regime taxonomy maps π against B* to produce an actionable compliance classification.

**Notation box for the MAC decision framework.**

| Symbol | Meaning |
|---|---|
| r | Carbon reduction target (%) |
| Δr | Budget-step size (e.g., 5 percentage points) |
| π | Carbon market price (€/t CO₂e) |
| B(r) | Carbon budget at reduction target r: E_baseline × (1 − r/100) |
| Z(r) | Optimal logistics cost (€) at target r |
| E(r) | Optimal emissions (kg CO₂e) at target r |
| λ̂(r) | Finite-difference marginal abatement cost at target r (€/kg CO₂e) |
| r* | Maximum feasible abatement target (largest r with a feasible MILP) |

### 3.2 Finite-Difference Marginal Abatement Cost

Let Z(r) denote the minimum logistics cost at carbon reduction target r (%), and let E(r) denote the resulting total network emissions. Both Z and E are outputs of the MILP at the corresponding budget level B(r) = E_baseline × (1 − r/100).

For a reduction-step size Δr (e.g., 5 percentage points), the finite-difference marginal abatement cost is:

```
λ̂(r) = [Z(r) − Z(r − Δr)] / [E(r − Δr) − E(r)]     (€ / kg CO₂e)
```

This measures the incremental logistics cost required to move from the looser budget (r − Δr) to the tighter budget r. The numerator is the additional cost incurred by tightening the budget; the denominator is the additional emission reduction achieved. Thus:

- **λ̂ > 0**: Tightening the budget requires a mode shift that costs more than the logistics savings. The carbon budget is binding and the shift imposes a cost premium.
- **λ̂ = 0 / undefined**: The carbon budget is not binding at this level — the cost-optimal mode assignment already satisfies the constraint. No additional cost is incurred.
- **λ̂ < 0**: The mode shift required to meet the budget actually saves logistics cost (co-benefit).

**Validity of absolute MAC comparison.** A methodological concern with model-derived MAC is that absolute values may be less reliable than rankings (Huang et al. [24]; Kesicki and Strachan [17]): MAC estimates are sensitive to baseline choice, marginal-unit assumptions, and interaction effects that bottom-up models may omit. In the present framework, however, the absolute comparison between MAC and observable carbon price is defensible on structural grounds specific to the binding-constraint, discrete-assignment setting. First, the MAC is computed only when the constraint is demonstrably binding — tightening from r − Δr to r strictly increases cost and reduces emissions — so the value reflects an actual assignment change in the integer solution, not an imputed shadow price of a non-binding constraint. Second, the empirical MAC range (245–4,366 €/t) exceeds the benchmark carbon price (65 €/t) by 4–67×; even under the ±50% cost-parameter sensitivity sweep (Section 6.5), no tested parameterization shifts a domestic rail-limited network into the shift-preferred or parity regime. The absolute comparison is therefore robust to the parameter uncertainty relevant for this network class. This approach does not rely on naïve solver-reported LP-relaxation duals. In mixed-integer mode-assignment models, such duals are not reliable managerial MAC estimates because the integer optimal-value function is non-smooth and changes only when discrete assignments change — a fundamental property established by Kim and Cho [25] and Crema [26]. More sophisticated integer-programming sensitivity concepts exist, including average shadow prices, marginal-unit shadow prices, and perturbation-based methods [29]. However, these approaches are not routinely exposed as transparent, auditable outputs in standard logistics MILP workflows. Kuosmanen et al. [19] further establish, from a frontier analysis perspective, that shadow prices systematically over-estimate MAC because they reflect dual multipliers of the LP relaxation rather than the discrete cost of the next feasible technology switch — an additional distortion that applies even when LP duals are non-zero. The finite-difference MAC used here is therefore not presented as a new sensitivity-analysis theory, but as a practical, solver-independent estimator of the network's incremental abatement cost across adjacent carbon-budget levels. Our experiments confirm the practical problem: the CBC solver via PuLP reported zero LP relaxation dual values for the carbon-budget constraints in all three networks, even when tightening the budget forced costly mode shifts [2, 25, 26, 29]. The finite-difference method provides meaningful MAC estimates in all cases.

The finite-difference procedure used here is the RHS-parametric MILP technique of Jenkins [41] — solving the integer programme at point values of the carbon-budget parameter and joining the results — applied to the carbon-compliance decision context. Parametric integer programming and value-function analysis are established in operations research [2, 41]. The methodological contribution is not the parametric MILP procedure itself but its decision-analytics transposition: the MAC signal is compared against an observable market price to produce a five-regime compliance classification that incumbent routing models do not provide.

Fig. 1 illustrates the complete CARMA framework pipeline: intermodal network specification → parametric MILP budget sweep → finite-difference MAC estimation → five-regime classification → compliance instrument decision (see paper/figures/fig1_carma_pipeline.png).

**Figure 1.** CARMA framework pipeline. A parametric sweep of the carbon-budget RHS produces a step-function MAC curve via finite-difference; each (network, budget) point is classified into one of five carbon-compliance regimes; the regime determines whether mode shift, allowance purchase, co-benefit recognition, or network redesign is the rational response.

### 3.3 Carbon Compliance Regime Taxonomy

The framework identifies five regimes, organized into two groups. The three **core economic regimes** apply when the carbon constraint is binding and MAC is positive — that is, when tightening the budget imposes a real cost premium. The two **boundary regimes** apply when the framework's analytical conditions are not met: either the constraint is not binding (no MAC signal exists) or the MILP is infeasible (the budget target cannot be achieved at all).

For a given reduction target r, the finite-difference MAC λ̂(r) is the break-even carbon price. If the market carbon price π exceeds λ̂(r), physical mode shift is cheaper than purchasing allowances and should be preferred. If π is below λ̂(r), allowance purchase is cheaper than forcing internal abatement and should be preferred. Comparing λ̂ (in €/tonne CO₂e = λ̂ × 1000) to the current carbon market price π (€/tonne):

**Structural preconditions for regime classification.** A network manager can anticipate the likely regime from modal topology before running the parametric MILP, using three structural indicators: (1) *Modal cost differential* — if the cheapest low-emission mode already saves logistics cost relative to the baseline, the network is a co-benefit candidate (Regime 4) before any carbon instrument is applied; (2) *Terminal-cost-to-carbon-avoided ratio* — if the terminal handling premium for mode shift (typically €500–€1,200 per shipment for rail) materially exceeds the carbon cost avoided by the shift, allowance purchase will dominate across all realistic carbon prices; (3) *Modal abatement ceiling* — if the maximum emission reduction achievable by exhausting all feasible modal alternatives falls short of the compliance target, the network faces an infeasibility constraint that no carbon price can resolve. These structural indicators anticipate the regime; the parametric MILP instantiates it with the specific MAC value that supplies the decision-relevant break-even carbon price. From these structural conditions, the framework generates four theoretical predictions, tested empirically across 150 generated networks in §6.6 and formalized as empirical propositions in §7.2:

- **P1 (Rail-limited domestic class):** When terminal-cost penalties dominate distance-based rail savings, MAC will exceed any realistic near-term carbon price at all budget levels → allowance-purchase-preferred regime (Regime 3) is the structural expectation.
- **P2 (Maritime-accessible long-haul class):** When the lowest-emission mode is also the lowest-cost mode on long-haul segments, the carbon constraint will be non-binding under cost optimization → co-benefit decarbonization (Regime 4) is the structural expectation.
- **P3 (Hub-limited class):** When modal alternatives are few and quickly exhausted, feasibility will be lost before moderate budget targets are reached → infeasibility (Regime 5) is the structural expectation for aggressive reduction targets.
- **P4 (Cross-class invariance):** The same observable carbon price will imply opposite rational compliance decisions across these three structural classes, because compliance regime is topology-driven rather than price-driven.

**Core Economic Regimes (carbon constraint binding, λ̂ > 0):**

**Regime 1 — Mode Shift Preferred:** λ̂ < π × 0.90
Internal abatement cost is materially below the market price. Physical mode shifting is economically rational: reconfiguring the logistics network costs less than buying equivalent coverage from the carbon market.

**Regime 2 — Parity Zone:** 0.90 ≤ λ̂ / π ≤ 1.10
Internal abatement cost and market price are approximately equal (within 10%). The decision is margin-neutral. Managers should choose based on strategic considerations: long-term commitment to supply chain reconfiguration versus the flexibility of market compliance. *Regime 2 was not observed in any of the 33 base-archetype solves, 240 sensitivity cells, or 150 generated-network instances in this study — an informative result: the step-function MAC rarely lands within ±10% of the market price, so networks typically fall clearly on one side of the break-even threshold.*

**Regime 3 — Allowance Purchase Preferred:** λ̂ > π × 1.10
Internal abatement cost exceeds the market price. ETS allowance purchase is cheaper than forcing mode shifts. Forcing shifts would represent an above-market abatement investment with no economic justification at the current carbon price.

**Boundary Regimes:**

**Regime 4 — Co-Benefit Decarbonization (Constraint Non-Binding):** λ̂ undefined
The cost-optimal mode assignment already satisfies the carbon budget without any constraint penalty. Low-carbon modes are cost-competitive, so the private market already drives optimal decarbonization. No carbon compliance instrument is needed; the budget target is achieved as a by-product of cost minimization. This is not a failure of the framework — it is the most favorable outcome for the decision-maker.

**Regime 5 — Infeasible / Alternatives Exhausted:** MILP has no feasible solution at the target budget
The budget target cannot be achieved with the available modal alternatives. All feasible mode shifts have been deployed and total network emissions still exceed the target. The rational response is either to reduce the budget target, invest in new modal infrastructure, or accept that the emission constraint cannot be met within this network structure.

### 3.4 Assumptions and Boundary Conditions

**Generalizability: procedure versus numerical values.** The regime-determination procedure — parametric MILP sweep, finite-difference MAC estimation, comparison to observable carbon price, five-regime classification — is general and applies to any intermodal routing network with identifiable modal alternatives and an assessable emission constraint. The specific MAC values (e.g., 245–4,366 €/t for the domestic truck-rail archetype) are archetype-specific and require corridor-specific calibration before managerial application to a different network. The transferable claim is the procedure and the regime structure, not the cost constants. A practitioner applying the framework to a new network should expect to reproduce the regime logic while recomputing the MAC magnitudes from that network's own parametric MILP.

The framework is applicable when:
- (a) The MILP has a feasible solution at the target budget level.
- (b) At least one modal alternative exists with lower emissions than the current assignment.
- (c) The carbon market is accessible and comparable in scope and geography to the network's emissions.

The framework is not applicable when:
- The carbon constraint is non-binding (Regime 4): use co-benefit analysis instead.
- The carbon constraint is infeasible (Regime 5): reduce the budget target or invest in supply-chain redesign.
- The LP dual is used as a proxy for MAC: use parametric finite-difference instead.
- The logistics network is highly dynamic (real-time routing): the MILP must be re-solved at each planning cycle.

### 3.5 Algorithm Summary

**Algorithm 1.** MAC-based carbon compliance regime classification.

**Inputs:** Route set R = {ρ₁,…,ρₙ}; feasible mode set M(ρ) per route; mode costs c(ρ,m) and emission factors e(ρ,m); reduction targets r ∈ {0,5,…,50}%; carbon price scenarios {π₁,…,πₖ} (€/tonne).

**Notation:** r = carbon reduction target (%); Δr = step size (5 pp); π = carbon market price (€/t CO₂e); B(r) = E_baseline × (1 − r/100); Z(r) = optimal cost at target r; E(r) = optimal emissions at target r; λ̂(r) = finite-difference MAC at target r.

**Steps:**
1. Solve unconstrained cost MILP (B = ∞). Obtain Z₀, E₀ (baseline cost and emissions).
2. For each reduction target r ∈ {0, 5, 10, …, 50}:
   - Compute budget B(r) = E_baseline × (1 − r/100).
   - If E₀ ≤ B(r): classify target r as Regime 4 (co-benefit / non-binding); set Z(r) = Z₀, E(r) = E₀.
   - Otherwise: solve constrained MILP at B(r).
     - If infeasible: classify target r as Regime 5.
     - Otherwise: record Z(r) and E(r).
3. For each adjacent pair of feasible binding targets (r − Δr, r):
   - λ̂(r) = [Z(r) − Z(r − Δr)] / [E(r − Δr) − E(r)] × 1000  (€/t CO₂e)
4. For each (r, carbon price π):
   - Regime 1 if λ̂(r) < 0.90π
   - Regime 2 if 0.90π ≤ λ̂(r) ≤ 1.10π
   - Regime 3 if λ̂(r) > 1.10π
   - Regime 4 if E₀ ≤ B(r) (non-binding / co-benefit)
   - Regime 5 if MILP infeasible at B(r)
5. Identify r* = maximum feasible abatement target (largest r with feasible MILP status).

**Outputs:** MAC curve {λ̂(r)}, regime map {regime(r, π)}, infeasibility ceiling r*, decision recommendation per (r, π) pair.

**Complexity:** O(|𝓑| × T_MILP), where |𝓑| = 11 budget levels (0–50% in 5% steps) and T_MILP = 50–200 ms for n = 12–50 routes via CBC.

---

## 4. Optimization Model

### 4.1 Multi-Objective Formulation

Let G = (V, A) be the supply chain network, P = {ρ₁, ..., ρₙ} the route set, M = {truck, rail, ship, air} the transport mode set, and B ∈ ℝ₊ the carbon budget (kg CO₂e). The framework minimizes two objectives:

```
f₁(X) = Σρ∈P Σm∈M cρm · xρm               (total logistics cost, €)
f₂(X) = Σρ∈P Σm∈M êρm · xρm               (total CO₂e emissions, kg)
```

subject to: (C1) Σm∈M xρm = 1 ∀ρ ∈ P (one mode per route); (C2) Σρ∈P Σm∈M êρm · xρm ≤ B (carbon budget); (C3) mode feasibility (distance and infrastructure constraints); (C4) xρm ∈ {0, 1}.

### 4.2 Parametric MILP for MAC Estimation

For the decision framework (Section 3), the multi-objective problem is collapsed to a single-objective MILP by setting the weight of f₁ to 1 and treating f₂ as a hard constraint:

```
min   Σρ∈P Σm∈M cρm · xρm
s.t.  Σρ∈P Σm∈M êρm · xρm ≤ B(r)      [C2: carbon budget at reduction target r]
      Σm∈M xρm = 1        ∀ρ ∈ P       [C1: one mode per route]
      xρm = 0  if mode m infeasible for route ρ  [C3: mode feasibility]
      xρm ∈ {0, 1}                      [C4: binary assignment]
```

where B(r) = baseline_emissions × (1 − r/100) for reduction target r ∈ [0, 37]%. This is solved at each budget level r using PuLP (CBC solver). The finite-difference MAC is then computed from adjacent solutions as described in Section 3.2.

**Emission factors** (kg CO₂e per tonne-km): truck 0.0762 (HBEFA 4.2 HDV Euro VI), rail 0.0285 (Eurostat 2022 Spanish grid), ship 0.011 (Eurostat 2022 short-sea; IMO [14]), air 0.680 (ICAO CORSIA 2022).

**Emission model**: The six-factor physics-informed formula combines Grubb payload efficiency [12], COPERT speed correction [9], EN 16258 temperature correction [11], HBEFA congestion factor [10], bidirectional terrain, and coupled weather-congestion effects. This provides physically realistic emission estimates for the multi-objective case; it is not claimed to be field-validated (see Section 7.3).

---

## 5. Experimental Design

### 5.1 Network Structural Classes

The three network structural classes were designed to span the theoretically relevant range of modal-availability and cost-structure conditions that govern compliance regime — not to maximize geographic coverage. Each structural class is a controlled instantiation of the topology-driven regime predictions formulated in §3.3: the experiment tests whether each structural class lands in its predicted regime and remains there under parameter variation. Salamanca represents the **rail-limited domestic structural class**: modal alternatives exist (truck to rail) but carry a terminal cost premium predicted to keep MAC above any realistic near-term carbon price. Iberian represents the **maritime-accessible long-haul structural class**: ship is both lower-emission and lower-cost than truck on long-haul international segments, predicted to produce co-benefit decarbonization independent of carbon pricing. Frankfurt represents the **hub-limited redundancy structural class**: modest alternatives exist (truck to rail for medium-distance routes) but are quickly exhausted, predicted to create a hard ceiling on achievable emission reductions. Together, these three structural classes span the theoretical range from market-driven decarbonization (Iberian, predicted Regime 4) through constrained-but-feasible (Frankfurt, predicted Regimes 3–5 depending on budget) to allowance-dominated (Salamanca, predicted Regime 3 at all tested budget and price levels). They are not claimed to represent all European or global logistics network types, but they are chosen to test whether regime behavior is determined by structural class membership.

**Network 1 — Salamanca domestic** (12 routes, truck/rail): Twelve routes from Salamanca to major Spanish cities (63–510 km). Rail is available for routes ≥ 150 km (RENFE freight minimum), with a terminal cost of €680 per route shift. Route distances and cargo weights are adopted from the reference network of Sánchez-Pravos et al. [3]; modal cost rates (truck 0.110 €/(t·km), rail 0.055 €/(t·km) + €680 terminal) and emission factors (HBEFA 4.2, Eurostat 2022) are derived independently from published transport data rather than taken from [3]. This is a purely domestic, short-to-medium haul network where rail is infrastructure-constrained and carries a significant terminal premium.

**Network 2 — Iberian regional** (12 routes, truck/rail/ship): Twelve routes from Spanish coastal cities including long-haul maritime segments (Valencia–Hamburg 2,200 km; Algeciras–Genova 1,800 km). Ship mode is available for routes ≥ 400 km at 0.028 €/(t·km) + €750 terminal. This network includes routes where maritime transport is dramatically cheaper than road.

**Network 3 — Frankfurt European hub** (14 routes, truck/rail/air): Fourteen routes from Frankfurt to European destinations (280–1,800 km). Rail available for ≥ 150 km at 0.055 €/(t·km) + €680 terminal; air available for three express routes. EU-27 average rail emission factor (0.057 kg CO₂e/t·km) applied, reflecting the German electricity grid [7]. Hub-and-spoke structure with limited modal redundancy at high budget reduction targets.

### 5.2 Parametric Budget Sweep

Each network is solved at budget reduction levels r ∈ {0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50}% of the truck-only baseline. The MILP is solved with ets_price = 0 (pure logistics cost minimization with hard carbon budget). Finite-difference MAC is computed between adjacent 5% steps.

### 5.3 Decision-Regime Analysis

For each (network, reduction target r, carbon price π) combination, the decision regime is classified following Section 3.3. Carbon price scenarios: π ∈ {25, 50, 65, 75, 100, 150} €/tonne CO₂e. The EU ETS 2024 average (65 €/t) is the primary reference.

---

## 6. Results

Results are organized across two evidence tiers. The first tier (§6.1–§6.5) uses three network structural classes to establish the MAC curve shape, regime taxonomy, boundary conditions, and parameter sensitivity — existence-and-mechanism demonstrations that characterize regime behavior in controlled isolation. The second tier (§6.6) is a robustness study of the taxonomy's internal logic: 1,650 MILP solves across 150 randomly generated network variants — sampled within the family-defining parameter ranges — test whether each structural class's predicted regime remains stable under cost and emission parameter variation. Because the generated networks are sampled within the same structural-class constraints as the base cases, these results demonstrate internal consistency, not real-world regime frequencies. The key robustness statistics — foregrounded before the structural-class details — are: across 50 rail-limited domestic variants, 54% non-binding and 46% allowance-preferred at 20% budget — 0% shift-preferred in either case, median binding-case MAC 1,398 €/t (21× ETS); across 50 maritime-accessible variants, 100% non-binding; across 50 hub-limited variants, 52% infeasible at 20% budget (median maximum feasible abatement 15%). These results confirm that the regime predictions from §3.3 are stable within each structural class, not artifacts of the specific base-case parameterization.

### 6.1 Marginal Abatement Cost Curves (RQ1)

**Table 3.** Parametric budget sweep results — optimal cost and emissions across three networks (ets_price = 0).

**Network 1 — Salamanca domestic:**

| Reduction % | Optimal cost (€) | Emissions (kg) | Δcost% | Δemis% | MAC (€/t) | Shifts |
|-------------|-----------------|----------------|--------|--------|-----------|--------|
| 0% (baseline) | 4,654 | 3,224 | 0.0% | 0.0% | — | 0 |
| 5% | 4,773 | 2,737 | +2.6% | −15.1% | 245 | 1 |
| 10%–15% | 4,773 | 2,737 | +2.6% | −15.1% | non-binding | 1 |
| 20% | 5,059 | 2,396 | +8.7% | −25.7% | 837 | 2 |
| 25% | 5,059 | 2,396 | +8.7% | −25.7% | non-binding | 2 |
| 30% | 5,450 | 2,145 | +17.1% | −33.5% | 1,563 | 3 |
| 35% | 5,873 | 1,923 | +26.2% | −40.4% | 1,903 | 4 |
| 40% | 5,873 | 1,923 | +26.2% | −40.4% | non-binding | 4 |
| 45% | 6,319 | 1,719 | +35.8% | −46.7% | 2,193 | 5 |
| 50% | 6,857 | 1,596 | +47.4% | −50.5% | 4,366 | 6 |

**Network 2 — Iberian regional:**

| Reduction % | Optimal cost (€) | Emissions (kg) | Δcost% | Δemis% | MAC (€/t) | Shifts |
|-------------|-----------------|----------------|--------|--------|-----------|--------|
| Baseline (all truck) | 32,782 | 22,709 | — | — | — | 0 |
| 0% (unconstrained) | 14,515 | 5,202 | −55.7% | −77.1% | co-benefit | 5 |
| 5%–50% | 14,515 | 5,202 | −55.7% | −77.1% | non-binding | 5 |

**Network 3 — Frankfurt European hub:**

| Reduction % | Optimal cost (€) | Emissions (kg) | Δcost% | Δemis% | MAC (€/t) | Shifts |
|-------------|-----------------|----------------|--------|--------|-----------|--------|
| 0% (baseline) | 19,392 | 13,433 | — | — | — | 0 |
| 0%–15% (unconstrained optimum) | 15,963 | 11,287 | −17.7% | −16.0% | co-benefit | 4 |
| 20% | 16,418 | 10,733 | −15.3% | −20.1% | 822 | 7 |
| 25% | 19,216 | 10,048 | −0.9% | −25.2% | 4,086 | 14 |
| 30%+ | Infeasible | — | — | — | — | — |

**Key findings from the MAC curves:**

Fig. 2 shows the MAC curves and logistics cost trajectories for all three networks across the 0–50% budget range (see paper/figures/fig2_mac_curves.png). Fig. 3 shows the decision regime heatmaps across the full carbon price × budget matrix (see paper/figures/fig3_regime_heatmaps.png).

**Figure 2.** Marginal abatement cost curves and logistics cost trajectories for the three network archetypes across the 0–50% carbon-budget reduction range. Domestic (Salamanca): step-function MAC rising from 245 €/t CO₂e (first shift, 5% budget) to 4,366 €/t (sixth shift, 50% budget). Maritime (Iberian): logistics cost falls monotonically from the unconstrained baseline — co-benefit across all tested budgets. Hub (Frankfurt): step-wise MAC rising to 4,086 €/t CO₂e at 25%, infeasible thereafter. Dashed horizontal line: EU ETS 2024 price (65 €/t).

**Figure 3.** Decision-regime heatmaps across the full carbon price (π) × budget reduction (r) matrix for the three network archetypes. Each cell indicates the compliance regime: Regime 1 (mode shift preferred, λ̂ < 0.90π), Regime 2 (parity, ±10% of π), Regime 3 (allowance purchase preferred, λ̂ > 1.10π), Regime 4 (co-benefit, non-binding), or Regime 5 (infeasible). The vertical dashed line marks π = 65 €/t (EU ETS 2024); the horizontal dashed line marks r = 20% (SBTi near-term freight target).

**Finding 1 (RQ1): MAC is non-linear, step-function-shaped, and network-structure-dependent.** In the Salamanca truck-rail domestic network, MAC rises from 245 €/t (first mode shift at 5% budget) to 4,366 €/t (sixth shift at 50% budget) — an 18× increase. This step-function shape reflects the discrete integer structure [18]: MAC is flat (non-binding) between shift thresholds, then jumps when a new route must shift. The jump magnitudes differ because each additional route has a different logistics cost premium for rail.

**Finding 2 (RQ1): Network modal structure determines the entire MAC regime.** The Iberian maritime network shows co-benefit decarbonization: switching to ship on long international routes saves 55.7% in logistics cost while reducing emissions 77.1% from the truck-only baseline. No carbon pricing is needed — the private logistics optimum already achieves near-maximum emission reduction. The Frankfurt hub falls between: co-benefit for the first 16% reduction (cheap rail routes), then binding MAC of 822 €/t at 20%, and infeasibility above 25%.

*(LP relaxation duals on the carbon budget constraint were 0.0 in all 33 base-archetype solves — the three named networks × 11 budget levels — as expected for integer programmes [2, 25]; this is motivating context, not a novel finding.)*

### 6.2 Decision-Regime Analysis (RQ2)

**Table 4.** Decision regime at EU ETS 2024 price (65 €/t CO₂e) across network archetypes.

| Budget reduction | Salamanca | Iberian | Frankfurt |
|-----------------|-----------|---------|-----------|
| 0% | allowance preferred | co-benefit | co-benefit |
| 5% | allowance preferred (MAC 245 €/t) | co-benefit | co-benefit |
| 10%–15% | allowance preferred | co-benefit | co-benefit |
| 20% | allowance preferred (MAC 837 €/t) | co-benefit | allowance preferred (MAC 822 €/t) |
| 25% | allowance preferred (MAC 1,563–1,903 €/t) | co-benefit | allowance preferred (MAC 4,086 €/t) |
| 30%+ | allowance preferred (MAC 2,193–4,366 €/t) | co-benefit | infeasible |

**Finding 4 (RQ2): In the domestic truck-rail structural class, the network-specific MAC (245–4,366 €/t) exceeds the ETS price at all tested budget levels — consistent with firm-level abatement costs [38] and modal-price inelasticity findings [31], and now derived endogenously from network modal topology.** Salamanca MAC ranges from 245 €/t (3.8× ETS) at 5% reduction to 4,366 €/t (67× ETS) at 50% reduction; purchasing allowances is always cheaper than forcing mode shifts across all carbon price scenarios tested (25–150 €/t, Table 4). The contribution is not the abate-versus-buy conclusion — that conclusion is prior art — but its derivation from the endogenous network break-even carbon price B*(r) and its embedding in the five-regime taxonomy.

**Finding 5 (Boundary confirmation — Regime 4):** Co-benefit decarbonization (Regime 4) is a definitional boundary case: the solver reports a feasible unconstrained optimum that already satisfies the carbon budget, so the carbon constraint is non-binding. The taxonomy correctly classifies this as the most favorable compliance outcome. In the Iberian network, the unconstrained cost optimum achieves 77.1% emission reduction at 55.7% cost saving, confirmed in 100% of generated maritime-accessible variants. The managerial contribution is the explicit regime label: prior routing models report this as a constraint status (non-binding), not as an actionable compliance classification.

The break-even carbon price for mode shift varies by 2 orders of magnitude across archetypes: for Salamanca, the threshold is 245 €/t (3.8× ETS 2024); for Frankfurt at 20%, it is 822 €/t (12.6× ETS) — levels far above current or projected near-term ETS prices.

**Table 5.** Decision regime across carbon price scenarios — Salamanca domestic network.

| Budget % | MAC (€/t) | π=25 €/t | π=50 €/t | π=65 €/t | π=75 €/t | π=100 €/t | π=150 €/t |
|----------|----------|----------|----------|----------|----------|-----------|-----------|
| 5% | 245 | allowance | allowance | allowance | allowance | allowance | allowance |
| 20% | 837 | allowance | allowance | allowance | allowance | allowance | allowance |
| 30% | 1,563 | allowance | allowance | allowance | allowance | allowance | allowance |
| 35% | 1,903 | allowance | allowance | allowance | allowance | allowance | allowance |
| 45% | 2,193 | allowance | allowance | allowance | allowance | allowance | allowance |
| 50% | 4,366 | allowance | allowance | allowance | allowance | allowance | allowance |

Note: MAC > 150 €/t at all budget levels for Salamanca. Physical mode shift is not the economically preferred instrument at any realistically foreseeable carbon price under current terminal cost structures.

### 6.3 When Is the Framework Applicable? (Findings from Boundary Conditions)

**Finding 6 (Boundary confirmation — Regimes 4 and 5):** Regimes 4 and 5 are definitional boundary behaviors, confirmed to occur in the sampled network families. Regime 4 (non-binding) is confirmed when the unconstrained optimum satisfies the carbon budget — all Iberian variants. Regime 5 (infeasible) is confirmed when the MILP has no feasible solution at the target budget — 52% of hub-limited variants at 20%, with a hard ceiling at 25.2% for the Frankfurt base case regardless of carbon price. Both are reported as named managerial regime classifications rather than raw solver status codes, which is the taxonomy's practical contribution for these boundary cases: a solver reports "non-binding" or "infeasible"; the framework reports which compliance action (recognize co-benefit; trigger redesign) is warranted.

### 6.4 Budget-Step Robustness of the Finite-Difference MAC Method

Because MAC is estimated by finite difference, a methodological concern is whether the 5% step size creates artificial discontinuities in the MAC curve or spurious regime boundaries. We address this by running the parametric MILP sweep at three step sizes — 2.5%, 5%, and 10% — and comparing regime classifications at common budget levels {0%, 10%, 20%, 30%, 40%, 50%}.

**Table 6.** Budget-step robustness — decision regime at EU ETS 65 €/t across step sizes.

| Network | Budget % | Step 2.5% | Step 5% | Step 10% | Stable? |
|---------|----------|-----------|---------|----------|---------|
| Salamanca | 0–50% | allowance preferred | allowance preferred | allowance preferred | YES |
| Iberian | 0–50% | non-binding | non-binding | non-binding | YES |
| Frankfurt | 0–20% | allowance preferred | allowance preferred | allowance preferred | YES |
| Frankfurt | 30–50% | infeasible | infeasible | infeasible | YES |

**Finding 7 (Robustness): Regime classification is 100% stable across budget-step sizes.** Across 18 (network × budget level) cells, the regime classification at EU ETS 65 €/t is identical for 2.5%, 5%, and 10% budget steps. The MAC value differs in magnitude between step sizes (because a 10% step averages over a wider interval), but the resulting regime classification is unchanged. This confirms that the finite-difference method is robust to step-size choice over the tested range and that the 5% baseline step is not a methodological artifact.

### 6.5 Parameter Sensitivity of Carbon Compliance Regimes

To test whether the regime classifications observed in the three base networks are artifacts of specific parameterizations, we sweep four parameters most likely to affect the mode-shift vs allowance-purchase boundary: (1) rail terminal handling cost (€300–€1,200 per shipment), (2) truck cost rate (×0.75 to ×1.50 baseline), (3) rail cost rate (×0.50 to ×1.50 baseline), (4) rail emission factor (×0.50 to ×1.60 baseline). Each sweep is evaluated at a 20% budget reduction and six carbon price scenarios (25–150 €/t). Total: 240 sensitivity cells across Salamanca and Frankfurt (Iberian is excluded as a co-benefit archetype where sensitivity is not relevant to the compliance decision).

**Table 7.** Parameter sensitivity summary — Salamanca and Frankfurt at 20% budget reduction.

| Parameter | Variation | Salamanca MAC (€/t) | Salamanca regime at 65 €/t | Frankfurt MAC (€/t) | Frankfurt regime at 65 €/t |
|-----------|-----------|--------------------|--------------------------|--------------------|--------------------------|
| Rail terminal (baseline €680) | €300 (-56%) | non-binding | non-binding | non-binding | non-binding |
| | €500 (-26%) | 310 | allowance preferred | 88 | allowance preferred |
| | €680 (baseline) | 837 | allowance preferred | 822 | allowance preferred |
| | €900 (+32%) | 1,481 | allowance preferred | 2,015 | allowance preferred |
| | €1,200 (+76%) | 2,359 | allowance preferred | 3,641 | allowance preferred |
| Truck cost rate | ×0.75 | 1,413 | allowance preferred | 2,254 | allowance preferred |
| | ×1.00 (baseline) | 837 | allowance preferred | 822 | allowance preferred |
| | ×1.25 | 260 | allowance preferred | non-binding | non-binding |
| | ×1.50 | non-binding | non-binding | non-binding | non-binding |
| Rail cost rate | ×0.50 | 260 | allowance preferred | non-binding | non-binding |
| | ×1.00 (baseline) | 837 | allowance preferred | 822 | allowance preferred |
| | ×1.50 | 1,413 | allowance preferred | 2,254 | allowance preferred |
| Rail emission factor | ×0.50 | 644 | allowance preferred | non-binding | non-binding |
| | ×1.00 (baseline) | 837 | allowance preferred | 822 | allowance preferred |
| | ×1.30 | non-binding | non-binding | infeasible | infeasible |

**Finding 8 (Robustness): Sensitivity and generated-network tests confirm that the regime classification is a structural regularity, not a parameterization artifact.** Across 240 sensitivity cells, 72% are "allowance preferred," 22% are "non-binding" (co-benefit), 5% are "infeasible," and 1% (2 cells) are "shift preferred." No parameter combination within ±50% of baseline costs produces a "shift preferred" regime at 65 €/t in domestic networks. The "allowance preferred" regime transitions to "non-binding" only when parameters make rail cost-competitive without any carbon incentive — not when the carbon price alone crosses a threshold. The two "shift preferred" cells require both reduced rail terminal cost (€500, −26%) and carbon prices ≥ 100 €/t, confirming that infrastructure-cost reductions and substantially higher carbon prices are jointly required before mode shift becomes economically preferred.

### 6.6 Generated-Network Robustness

The generated networks are not intended to estimate real-world frequencies of carbon-compliance regimes. They are controlled robustness instances designed to test whether the regime taxonomy remains stable under variation in modal economics. For each archetype family, route distances, cargo weights, terminal costs, modal cost multipliers, emission factors, and modal availability were sampled within the ranges reported in Appendix A. The defining structural condition of each family was preserved: rail-limited domestic networks permit truck/rail choices only; maritime-accessible networks include long-haul ship options; and hub-limited networks include constrained rail availability, higher rail emission factors, and selected air options.

We generate 50 random networks per archetype family (150 networks total, 1,650 MILP solves). Regime is classified at 20% budget reduction and 65 €/t.

**Table 9.** Generated-network regime distribution (50 instances per archetype family, 20% budget, EU ETS 65 €/t).

| Archetype family | n | Non-binding / co-benefit | Allowance preferred | Shift preferred | Infeasible at 20% | Median MAC (binding cases) | Median max feasible |
|-----------------|---|--------------------------|---------------------|-----------------|-------------------|--------------------------|---------------------|
| Rail-limited domestic | 50 | 54.0% | 46.0% | 0.0% | 0.0% | 1,398 €/t | 50% |
| Maritime-accessible | 50 | 100.0% | 0.0% | 0.0% | 0.0% | — | 50% |
| Hub limited redundancy | 50 | 24.0% | 22.0% | 2.0% | 52.0% | 920 €/t | 15% |

Across 150 generated networks, no rail-limited domestic network enters the "shift preferred" regime at 65 €/t (0/50 = 0.0%); all 50 maritime networks are permanently non-binding/co-benefit (100.0%); and 52% of hub networks are infeasible at 20% because the hard abatement ceiling falls below the target. **Calibration anchor against real-network emission variation.** Heinold and Meisel [35] document that real European intermodal rail/road emission rates vary by up to 2.5× across operator types. Applying this range to the domestic archetype (±2.5× on the rail emission factor) shifts the truck-rail MAC range to approximately 130–11,000 €/t — still well above the 65 €/t ETS benchmark at every tested parameterization, suggesting the allowance-preferred regime is robust to real-world emission-factor uncertainty. This provides a partial real-network plausibility check; full field calibration with carrier-specific tachograph data remains a future-work priority (§7.5). The three named archetypes (Salamanca, Iberian, Frankfurt) are each representative of their family. Median binding MAC for domestic rail networks is 1,398 €/t — 21× EU ETS 2024 prices — ranging from 142 to 9,093 €/t across the generated family. Even the most favorable generated domestic network (lowest MAC at 142 €/t) remains above 65 €/t. The median maximum feasible abatement for hub-limited networks is only 15%, confirming that networks with European hub structure frequently exhaust modal alternatives before reaching a 20% reduction target.

### 6.6a Structural Propositions from Generated-Network Robustness

The generated-network robustness study is used to derive structural propositions rather than population frequencies. The results indicate that regime identity is governed primarily by modal availability, terminal-cost penalties, relative modal cost, emission-factor differences, and the maximum feasible abatement ceiling. Three propositions follow.

**Proposition 1 — Rail-limited domestic networks tend toward allowance preference when terminal-cost penalties dominate carbon-price levels.** In domestic truck–rail networks where rail availability is limited by distance thresholds and terminal handling costs remain high, the internal MAC of physical mode shift tends to exceed current carbon-market benchmark prices. Under these conditions, allowance purchase is the economically preferred compliance instrument unless rail terminal costs fall materially or the carbon price rises substantially above current levels. This is supported by 46% allowance-preferred and 0% shift-preferred outcomes across 50 generated domestic networks at 65 €/t (54% are non-binding/co-benefit at 20% budget — not shift-preferred, but not because of allowance cost); median binding-case MAC is 1,398 €/t (21× ETS).

**Proposition 2 — Maritime-accessible long-haul networks can enter a co-benefit regime when ship is both cheaper and cleaner than truck.** Where long-haul maritime options are available and ship transport has both lower cost and lower emission intensity than road transport, unconstrained cost minimization can already satisfy stringent carbon targets. In such cases, the carbon constraint is non-binding and the appropriate managerial conclusion is not forced mode shift or allowance purchase, but recognition of co-benefit decarbonization. All 50 generated maritime-accessible networks exhibit this property (100% non-binding at 20% budget).

**Proposition 3 — Hub-limited networks are constrained primarily by modal abatement capacity rather than carbon price.** In hub-and-spoke networks with limited modal redundancy, higher rail emission factors, or constrained rail availability, the binding limitation may be the maximum feasible abatement level rather than the market price of carbon. Once all feasible lower-emission modal alternatives are exhausted, tighter carbon targets become infeasible and the correct response is network redesign rather than marginal compliance optimization. This is supported by 52% infeasibility rates at 20% budget across 50 generated hub-limited networks, with median maximum feasible abatement of only 15%.

---

## 7. Discussion

### 7.1 Managerial Decision Rules

The decision framework generates four operational rules directly applicable to logistics managers:

**Rule 1 (Network Assessment Before Policy):** Before imposing a carbon budget, run the unconstrained cost-optimal routing. If MAC is undefined (co-benefit regime), the market already optimizes decarbonization. Set the carbon budget equal to the unconstrained emission level — no active compliance instrument is required.

**Rule 2 (MAC vs. ETS for Mode-Shift Decisions):** If MAC < ETS price: force mode shifts (the network's internal abatement is cheaper than the market). If MAC > ETS price: buy allowances (the market is cheaper). This comparison requires the parametric MILP and is specific to the network at the target budget level. Single-point calculations are insufficient; the regime may change as the budget tightens.

**Rule 3 (Hard Ceiling Check):** Before committing to a carbon reduction target, verify that the target is feasible by checking whether the MILP at the target budget has an optimal solution. If infeasible, the target exceeds the network's modal abatement capacity; supply-chain redesign or a less aggressive target is required.

**Supply Chain Design Implication (Regime 5 — Infeasibility as a Design Signal):** When the parametric MILP confirms Regime 5, neither mode-shift forcing nor allowance purchase resolves the shortfall — the constraint is structurally infeasible within the existing modal mix. This is not a solver failure but a diagnostic: the network lacks sufficient low-emission modal capacity. The appropriate response is supply chain redesign: extending rail or maritime access to binding road-only corridors, consolidating volumes to make rail terminal costs viable, rerouting OD pairs through corridors with low-carbon alternatives, or negotiating a phased target aligned with the feasible abatement ceiling. The framework's infeasibility threshold thus serves as a *supply chain design trigger* — it specifies not only that redesign is needed but the abatement level that redesign must unlock, a design-level output absent from conventional carbon-budget solvers that return only a feasibility status.

The framework's value is diagnostic precision: it prevents managers from applying the wrong compliance instrument to the wrong network. The MAC curve reveals which regime applies — the distinction that is invisible in a conventional carbon-budget MILP that reports only the optimal assignment.

**Table 8.** Strength of empirical claims and allowed generalization.

| Claim | Evidence strength | Allowed wording |
|-------|-------------------|-----------------|
| MAC is step-function-shaped in integer mode assignment | Strong: confirmed across 3 archetypes, 3 step sizes, 240 sensitivity cells | General mechanism for discrete mode assignment |
| Salamanca-like rail-limited networks remain "allowance preferred" above 65 €/t | Strong: no parameter combination in ±50% cost range shifts the regime | Archetype-level claim, conditional on current EU ETS prices |
| Maritime corridors show co-benefit decarbonization | Moderate: one archetype, supported by Liu et al. [27] | Condition-specific claim (requires ship < truck in cost AND emission) |
| Carbon pricing alone is redundant in all maritime networks | Weak: structural conditions required | Do not generalize without network-specific MAC analysis |
| Framework regime outcomes transfer across networks without recalibration | Weak | Do not claim; regime is network-specific and must be recomputed |
| Allowance purchase preferred may weaken under higher carbon-price scenarios (100–150 €/t) | Weak: changes at Frankfurt if rail terminal < €500 | Conditional: regime shifts at 100–150 €/t with rail infrastructure improvements |

### 7.2 Structural Propositions from MAC Regime Evidence

The regime taxonomy's diagnostic power derives from a central finding: network structure, not the carbon price level, is the primary governor of which compliance regime a network occupies. This is the framework's most actionable managerial implication — it means regime classification is largely determinable from network topology before the optimization is run. The four propositions below therefore function not only as post-hoc results summaries but as a priori diagnostic indicators: a practitioner can anticipate the likely regime from structural network properties (modal availability, terminal-cost structure, long-haul share, modal emission-factor gap) and use the parametric MILP to supply the specific MAC value that confirms the regime and quantifies the break-even carbon price. The three base archetypes and 150 generated networks support four such propositions. They are not universal laws; they are empirically grounded structural rules that should be re-tested when the framework is applied to a new corridor or network.

**Proposition 1 — Rail-limited domestic networks tend toward allowance preference when terminal-cost penalties dominate carbon-price levels.**
In domestic truck–rail networks where rail availability is limited and terminal handling costs are high relative to distance-based rail savings, the internal MAC of physical mode shift tends to exceed current carbon-market benchmark prices. Under these conditions, allowance purchase is the economically preferred compliance instrument unless rail terminal costs fall materially, road costs rise sharply, or carbon prices increase substantially. This is supported by 46% allowance-preferred and 0% shift-preferred outcomes across 50 generated domestic networks at 65 €/t (54% are non-binding/co-benefit at 20% budget — not shift-preferred, but not because of allowance cost); median binding-case MAC is 1,398 €/t (21× ETS).

**Proposition 2 (definitional boundary — Regime 4) — Maritime-accessible long-haul networks enter co-benefit decarbonization when the unconstrained cost optimum already satisfies the carbon budget.**
This is a definitional property of Regime 4: by design, when the lowest-cost mode is also the lowest-emission mode, unconstrained optimization satisfies any feasible budget without a carbon instrument. The taxonomy correctly classifies this as a named regime rather than a raw solver status. Confirmed in 100% of 50 generated maritime-accessible networks (100% non-binding at 20% budget).

**Proposition 3 (definitional boundary — Regime 5) — Hub-limited networks face target infeasibility when modal alternatives are exhausted before the budget target is met.**
This is a definitional property of Regime 5: the MILP is infeasible at the target budget because all lower-emission alternatives are deployed and total emissions still exceed the cap. The taxonomy correctly classifies this as a supply-chain design trigger. Confirmed by 52% infeasibility rates at 20% budget across 50 generated hub-limited networks, with median maximum feasible abatement of only 15%.

**Proposition 4 — The same carbon price can imply different compliance decisions across network archetypes.**
Because MAC is generated by discrete route-specific mode alternatives, a single carbon price does not have a uniform operational meaning across logistics networks. The same benchmark price may imply allowance purchase in rail-limited domestic networks, no action in co-benefit maritime networks, and infeasibility or redesign in hub-limited networks. This is the central reason that carbon-compliance decisions require network-specific MAC estimation rather than generic carbon-price thresholds.

**Table 10. Structural interpretation of MAC compliance regimes.**

| Structural condition | Expected regime | Managerial interpretation |
|---|---|---|
| Rail available but terminal-cost penalty exceeds distance-based savings | Allowance purchase preferred | Internal abatement is more expensive than market compliance |
| Long-haul maritime option is cheaper and cleaner than road | Co-benefit decarbonization | Cost minimization already reduces emissions |
| MAC lies within ±10% of carbon price | Parity zone | Strategic preference determines shift vs buy |
| Low-emission alternatives exist and MAC is below carbon price | Mode shift preferred | Physical abatement is cheaper than allowances |
| Modal alternatives exhausted before budget is met | Infeasible target | Network redesign or target relaxation required |

### 7.3 Theoretical Contribution

This paper extends the theory of marginal abatement cost curves — established in climate economics and partially applied in manufacturing scheduling [15] — to the intermodal supply chain routing context. The contribution is bounded: we do not claim to develop MAC curve theory, only to apply finite-difference estimation from parametric MILP to the intermodal mode-assignment problem and use the result to identify decision regimes.

The empirical finding that MAC is a step-function in integer routing models (rather than smooth as in continuous abatement cost curves) has implications for how logistics carbon budgets should be designed. Budget targets should be set at levels where feasible step-functions exist, not at arbitrary percentage targets that may fall in flat (non-binding) regions where the carbon budget has no marginal cost.

The co-benefit finding for the Iberian maritime network connects to a broader insight: in markets where low-emission transport modes (ship, rail) are cost-competitive, carbon pricing is redundant. Policy interventions aimed at driving modal shift should first diagnose whether the private market already delivers the desired outcome, and target subsidies or regulations at the segments (domestic, short-haul) where market failure exists.

### 7.4 Limitations and Boundary Conditions

**Archetype scope vs population.** Results are archetype-level rather than population-level. The three networks were chosen to represent structurally distinct modal conditions (rail-limited domestic, maritime-accessible long-haul, hub-and-spoke with limited redundancy) — not as a random sample of European logistics networks. The framework is general and the regime taxonomy is theoretically sound; the numerical regime outcomes (MAC ranges, transition thresholds) are network-specific and must be recomputed via parametric MILP for any new logistics network before managerial application.

**Synthetic archetype calibration.** The emission factors and logistics cost rates used here are drawn from published averages (HBEFA 4.2, Eurostat 2022) rather than from carrier-specific tachograph or ERP records. Heinold and Meisel [35] document substantial variation in carrier-specific emission rates and logistics costs across real European intermodal corridors — rail/road combined transport emission rates varied by a factor of up to 2.5× across operator types in their simulation — meaning route-level emission factors differ materially across carriers on the same mode. Against this benchmark, the three archetypes are controlled structural tests, not calibrated corridor models. The MAC ranges (245–4,366 €/t) are valid for the parameterizations tested; whether real-corridor MAC curves fall within or outside these ranges requires field calibration with actual carrier data. The generalizability claim is therefore archetype-structural, not corridor-universal: the regime taxonomy and regime-determination procedure are general, while the numerical thresholds are archetype-specific and should be re-estimated for any deployment context.

**Network scope.** The three networks used represent specific modal structures and distances. Results generalize to similarly structured networks (domestic rail-limited, maritime-corridor, inland hub) but should not be extrapolated to other contexts without running the parametric MILP for the specific network.

**Emission factor reliability.** Emission factors are drawn from HBEFA 4.2 (truck), Eurostat 2022 (rail, ship), and ICAO CORSIA (air). The physics-informed correction factors (speed, congestion, terrain, temperature) are not field-validated against telematics or measured emission records; they provide internally consistent estimates for comparative analysis only.

**Carbon market scope.** The EU ETS price is used as a benchmark carbon price for decision analysis, not as a claim that every modeled shipment is legally covered by EU ETS obligations. For Scope 3 emissions, voluntary targets, or non-EU jurisdictions, π should be replaced by the relevant internal carbon price, allowance price, carbon tax, or regulatory benchmark. The MAC framework remains unchanged; only the comparison price changes.

**MIP scale and solver.** The CBC solver via PuLP handles n = 12–50 route networks in 50–200 ms. Above n = 100, CBC solve times increase substantially; commercial MIP solvers (Gurobi, CPLEX) are recommended.

These limitations define the conditions under which the taxonomy should be applied, not invalidate it. The repeatable decision procedure — estimate the network-specific MAC curve through parametric MILP, compare it with the relevant carbon price, classify the resulting compliance regime — transfers to any new network; the specific MAC values do not.

### 7.5 Future Work

Three priorities emerge:

1. **Field validation**: Re-calibrate emission factors against truck tachograph or rail energy meter records. Validate cost models against actual logistics invoices for at least one real-world freight lane.

2. **Expanded network archetypes**: Extend to rail-only networks (central Europe), island/maritime-dependent networks, and US intermodal corridors with different modal cost structures.

3. **Real-time carbon pricing integration**: Adapt the framework for dynamic carbon market prices by re-solving the parametric MILP at each planning cycle, generating updated MAC curves and decision regime updates as ETS prices fluctuate.

---

## 8. Conclusion

Carbon-constrained logistics planning requires managers to compare the internal marginal cost of physical mode shifts against the external market price of carbon allowances. This comparison is straightforward in principle but inaccessible in practice: existing optimization models report optimal mode assignments without translating the marginal abatement cost of the emission constraint into an operational decision rule.

This paper develops a parametric marginal abatement cost decision framework for intermodal supply chain routing. The framework estimates MAC curves from finite differences of sequential parametric MILP solutions — a method robust to the known limitations of LP dual variables for mixed-integer programmes. Empirical results across three intermodal network archetypes characterize the decision landscape: domestic truck-rail networks exhibit MAC of 245–4,366 €/t (3.8–67× EU ETS 2024 prices), firmly in the allowance-purchase-preferred regime at all tested budget levels; maritime-accessible networks exhibit co-benefit decarbonization where mode shifts are already cost-optimal without any carbon pricing; hub-and-spoke networks face hard feasibility ceilings that limit physical abatement to 25% reduction before infeasibility.

The framework identifies three actionable regimes (mode shift preferred, parity, allowance purchase preferred) and two boundary conditions (co-benefit decarbonization, infeasibility) — each with a distinct managerial decision rule derived directly from the network's parametric MILP output.

The primary contribution is a supply-chain decision-analytics framework, not a generic algorithmic advance. Its value lies in converting parametric MILP-derived marginal abatement cost curves into actionable carbon-compliance regimes for intermodal logistics: shift modes when internal abatement is cheaper than market compliance, buy allowances when market compliance is cheaper, recognize co-benefit decarbonization when the constraint is non-binding, and identify infeasible targets when modal alternatives are exhausted. The resulting advancement is regime-level carbon decision analytics for intermodal logistics: instead of asking only which route assignment minimizes cost or emissions, the framework explains which carbon-compliance instrument is economically rational for a given network, target, and carbon price.

---

## Acknowledgements

No external funding was received for this research. The author thanks the maintainers of PuLP for open-source linear programming tooling.

---

## Data Availability

All code, datasets, and results are available at: **https://github.com/sthangavel/CARMA-ALGORITHM** (MIT License). Key scripts: `experiments/parametric_abatement.py` (MAC curve generation), `experiments/budget_step_robustness.py` (step-size robustness), `experiments/parameter_sensitivity.py` (parameter sensitivity sweep), `experiments/generated_network_robustness.py` (150-network robustness study), `experiments/generate_figure1.py` (Fig. 1 pipeline diagram), `experiments/generate_figures.py` (Fig. 2–3 generation), `algorithm/optimization/carbon_milp.py` (MILP solver). Generated figures: `paper/figures/fig1_carma_pipeline.png`, `paper/figures/fig2_mac_curves.png`, `paper/figures/fig3_regime_heatmaps.png`.

---

## CRediT Authorship

**Sivalingam Thangavel:** Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Writing — original draft, Writing — review & editing, Visualization, Project administration.

---

## Declaration of Competing Interest

The author declares no competing financial interests or personal relationships that could have influenced this work.

---

## Declaration of Generative AI and AI-Assisted Technologies

Generative AI tools were used during the preparation of this manuscript to assist with drafting, editing, and restructuring of text. The author reviewed and edited all AI-assisted content and takes full responsibility for the accuracy and integrity of the published work. No AI tools were used for data analysis, figure creation, or code development.

---

## References

[1] IEA, Global CO₂ emissions from transport by sub-sector in the Net Zero Scenario, 2000–2030, International Energy Agency, Paris, 2023. https://www.iea.org/data-and-statistics/charts/global-co2-emissions-from-transport-by-sub-sector-in-the-net-zero-scenario-2000-2030-2

[2] H.P. Williams, Model Building in Mathematical Programming, fifth ed., Wiley, Chichester, 2013.



[3] L. Sánchez-Pravos, J. Parra-Domínguez, S. Rodríguez González, P. Chamoso, A machine learning and evolutionary optimization framework for carbon-aware supply chain routing, Supply Chain Anal. 13 (2026) 100182. https://doi.org/10.1016/j.sca.2025.100182

[4] N.M. Alshabibi, et al., Multi-objective MILP for dynamic fleet scheduling with emission constraints, Sustainability 17 (2025) 4707. https://doi.org/10.3390/su17104707

[5] C. Shao, et al., NSGA-III for green intermodal freight transport with uncertain time-windows, Sustainability 14 (2022) 2985. https://doi.org/10.3390/su14052985

[6] T. Cui, Y. Shi, J. Wang, R. Ding, J. Li, K. Li, Practice of an improved many-objective route optimization algorithm in a multimodal transportation case under uncertain demand, Complex Intell. Syst. 11 (2025) 136. https://doi.org/10.1007/s40747-024-01725-4

[7] Ember, European Electricity Review 2024, Ember, London, 2024. https://ember-energy.org/latest-insights/european-electricity-review-2024/

[8] M. Ganjia, et al., Multi-objective sustainable supply chain scheduling with MILP-NSGA-II, Oper. Res. (2025). https://doi.org/10.1007/s12351-025-01013-0






[9] European Environment Agency, EMEP/EEA Air Pollutant Emission Inventory Guidebook 2019, EEA Report No. 13/2019, European Environment Agency, Copenhagen, 2019. https://www.eea.europa.eu/en/analysis/publications/emep-eea-guidebook-2019

[10] HBEFA, Handbook Emission Factors for Road Transport, INFRAS AG, Bern, 2026. https://www.hbefa.net

[11] CEN, EN 16258:2012 — Methodology for Calculation and Declaration of Energy Consumption and GHG Emissions of Transport Services, European Committee for Standardization, Brussels, 2012.

[12] R. Grubb, Road freight and fuel use: A review, Energy Policy 16 (1988) 433–440. https://doi.org/10.1016/0301-4215(88)90073-5

[13] T. Bektaş, G. Laporte, The pollution-routing problem, Transp. Res. Part B Methodol. 45 (2011) 1232–1250. https://doi.org/10.1016/j.trb.2011.02.004






[14] IMO, Fourth IMO Greenhouse Gas Study 2020, International Maritime Organization, London, 2020. https://www.imo.org/en/ourwork/environment/pages/fourth-imo-greenhouse-gas-study-2020.aspx


[15] A. Mencaroni, P. Leyman, B. Raa, S. De Vuyst, D. Claeys, Towards net-zero manufacturing: Carbon-aware scheduling for GHG emissions reduction, J. Clean. Prod. 529 (2025) 146787. https://doi.org/10.1016/j.jclepro.2025.146787

[16] R. Dekker, J. Bloemhof, I. Mallidis, Operations Research for green logistics — An overview of aspects, issues, contributions and challenges, Eur. J. Oper. Res. 219 (2012) 671–679. https://doi.org/10.1016/j.ejor.2011.11.010

[17] F. Kesicki, N. Strachan, Marginal abatement cost (MAC) curves: a call for caution, Clim. Policy 12 (2012) 219–236. https://doi.org/10.1080/14693062.2011.602059

[18] O. Kiuila, T.F. Rutherford, Piecewise smooth approximation of bottom-up abatement cost curves, Energy Econ. 40 (2013) 734–742. https://doi.org/10.1016/j.eneco.2013.09.011

[19] T. Kuosmanen, N. Kuosmanen, T. Sipiläinen, Shadow prices and marginal abatement costs: Convex quantile regression approach, Eur. J. Oper. Res. 289 (2021) 666–675. https://doi.org/10.1016/j.ejor.2020.07.030

[20] L.H. Kaack, P. Vaishnav, M.G. Morgan, I. Boukerrou, D. Bennett, Decarbonizing intraregional freight systems with a focus on modal shift, Environ. Res. Lett. 13 (2018) 083001. https://doi.org/10.1088/1748-9326/aad56c

[21] Y. Bouchery, A. Ghaffari, Z. Jemai, J. Fransoo, Cost, carbon emissions and modal shift in intermodal network design decisions, Int. J. Prod. Econ. 164 (2015) 197–207. https://doi.org/10.1016/j.ijpe.2014.11.017

[22] S. Misconel, C. Nienhaus, T. Deac, F. Haberstroh, J. Ruppert-Winkel, H.C. Gils, Step-wise marginal CO₂ abatement cost curves to determine least-cost decarbonization pathways for sector-coupled energy systems, J. Clean. Prod. 380 (2022) 134874. https://doi.org/10.1016/j.jclepro.2022.134874

[23] L. Ricci, A. Traverso, M. Troncia, Transport Sector GHG Mitigation Measures: Abatement Costs Application Review, Future Transp. 5 (2025) 44. https://doi.org/10.3390/futuretransp5020044

[24] L. Huang, P. Hu, W. Chen, The applicability of marginal abatement cost approach: A comprehensive review, J. Clean. Prod. 127 (2016) 59–71. https://doi.org/10.1016/j.jclepro.2016.04.013

[25] S. Kim, S. Cho, A shadow price in integer programming for management decision, Eur. J. Oper. Res. 37 (1988) 328–335. https://doi.org/10.1016/0377-2217(88)90336-8

[26] A. Crema, Average shadow price in a mixed integer linear programming problem, Eur. J. Oper. Res. 85 (1995) 625–635. https://doi.org/10.1016/0377-2217(93)E0353-T

[27] L. Liu, Z. Wan, Y. Wang, J. Wang, Co-benefits in carbon reduction from freight mode shifts under China's Clean Air Action, Environ. Res. Lett. 19 (2024) 054014. https://doi.org/10.1088/1748-9326/ad37b8

[28] E. Demir, W. Burgholzer, M. Hrušovský, E. Arıkan, W. Jammernegg, T. Van Woensel, Green intermodal freight transportation: bi-objective modelling and analysis, Int. J. Prod. Res. 57 (2019) 6162–6180. https://doi.org/10.1080/00207543.2019.1587186

[29] S. Mukherjee, S. Mukherjee, The average shadow price for MILPs with integral resource availability, Eur. J. Oper. Res. 169 (2006) 53–64. https://doi.org/10.1016/j.ejor.2004.05.012

[30] J. Flodén, R. Bäckström, Shipping in the EU emissions trading system: implications for mitigation, costs and modal split, Clim. Policy 24 (2024) 1–16. https://doi.org/10.1080/14693062.2024.2309143

[31] M. Boehm, F. Fröhlich, H. Kaack, M. Lutz, The potential of high-speed rail freight in Europe, Eur. Transp. Res. Rev. 13 (2021) 28. https://doi.org/10.1186/s12544-021-00484-4

[32] K.M.R. Hoen, T. Tan, J.C. Fransoo, G.J. van Houtum, Switching transport modes to meet voluntary carbon emission targets, Transp. Sci. 48 (2014) 592–608. https://doi.org/10.1287/trsc.2013.0481

[33] G. Glenk, et al., Constructing carbon abatement cost curves, Account. Rev. (2026), forthcoming. https://doi.org/[confirm before submission]

[34] T. Noguchi, Turnpike theorems and thresholds for carbon-priced modal split on capacity-constrained transport networks, Networks Spat. Econ. (2025). https://doi.org/[DOI must be confirmed before submission]

[35] A. Heinold, F. Meisel, Emission rates of intermodal rail/road and road-only transportation in Europe: A comprehensive simulation study, Transp. Res. Part D Transp. Environ. 65 (2018) 421–437. https://doi.org/10.1016/j.trd.2018.09.003

[36] A. Zakeri, F. Dehghanian, B. Fahimnia, J. Sarkis, Carbon pricing versus emissions trading: A supply chain planning perspective, Int. J. Prod. Econ. 164 (2015) 197–205. https://doi.org/10.1016/j.ijpe.2014.11.012

[37] X. Chen, G. Hao, Effects of carbon emission reduction policies on transportation mode selections with stochastic demand, Transp. Res. Part E Logist. Transp. Rev. 90 (2016) 196–205. https://doi.org/10.1016/j.tre.2015.11.008

[38] L. Rekker, M. Mulder, et al., Carbon abatement in the European chemical industry: assessing the feasibility of abatement technologies by estimating firm-level marginal abatement costs, Energy Econ. 126 (2023) 106943. https://doi.org/10.1016/j.eneco.2023.106943

[39] S. Lagouvardou, H.N. Psaraftis, Implications of the EU Emissions Trading System (ETS) on European container routes: A carbon leakage case study, Marit. Transp. Res. 3 (2022) 100059. https://doi.org/10.1016/j.martra.2022.100059

[40] A. Majumdar, et al., Network design for a decarbonised supply chain considering cap-and-trade policy of carbon emissions, Ann. Oper. Res. (2023). https://doi.org/[DOI must be confirmed before submission]

[41] E.S. Jenkins, Parametric mixed integer programming: An application to solid waste management, Manage. Sci. 28 (1982) 1270–1284. https://doi.org/10.1287/mnsc.28.11.1270

[42] T. Chen, et al., Low-carbon route optimization for multimodal freight transport under carbon tax policy, Socio-Econ. Plan. Sci. (2024). https://doi.org/[DOI must be confirmed before submission]

[43] Y. Yin, et al., Transition of multimodal transport network under different carbon price scenarios, Transp. Policy (2025). https://doi.org/[DOI must be confirmed before submission]

---

## Appendix A. Generated-Network Parameter Ranges

Parameter ranges used for the 150 stochastic robustness instances in §6.6. Each network is generated independently with a fixed random seed for reproducibility. Seeds 0–49 used for each family.

| Parameter | Rail-limited domestic | Maritime-accessible | Hub-limited redundancy |
|---|---|---|---|
| Number of routes | 8–16 | 8–16 | 10–18 |
| Route distance (km) | 60–550 (LogNormal, μ=ln 220, σ=0.65) | 400–3,000 (2–5 guaranteed long-haul ≥ 600 km) | 250–1,800 (LogNormal, μ=ln 500, σ=0.55) |
| Cargo weight (tonnes) | 5–25 (LogNormal, μ=ln 11, σ=0.45) | 5–25 (LogNormal, μ=ln 11, σ=0.45) | 5–25 (LogNormal, μ=ln 11, σ=0.45) |
| Rail terminal cost (€) | 350–950 (Uniform) | 350–950 (Uniform) | 350–950 (Uniform) |
| Ship terminal cost (€) | — | 400–1,200 (Uniform) | — |
| Truck cost rate | 0.80–1.20× baseline (Uniform) | 0.80–1.20× baseline (Uniform) | 0.80–1.20× baseline (Uniform) |
| Rail cost rate | 0.75–1.25× baseline (Uniform) | 0.75–1.25× baseline (Uniform) | 0.75–1.25× baseline (Uniform) |
| Ship cost rate | — | 0.75–1.25× baseline (Uniform) | — |
| Rail emission factor (kg/t-km) | 0.020–0.040 (Uniform) | 0.020–0.040 (Uniform) | 0.040–0.075 (Uniform, reflects German grid) |
| Ship emission factor (kg/t-km) | — | 0.008–0.016 (Uniform) | — |
| Rail availability | Available if distance ≥ rail_min_km (Uniform 100–220 km) | Available if distance ≥ 100 km | All routes rail-eligible; air on 10–30% of routes |
| Ship availability | Not available | Available on 2–5 guaranteed long-haul routes | Not available |

Baseline emission factors: truck 0.0762, rail 0.0285 (Eurostat 2022 Spanish grid), ship 0.011 kg CO₂e/t-km. Baseline cost rates per tonne-km: truck €0.10, rail €0.035, ship €0.008. Scripts: `experiments/generated_network_robustness.py`.
