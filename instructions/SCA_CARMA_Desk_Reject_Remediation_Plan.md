# Remediation Plan for SCA Desk Rejection  
**Manuscript:** *Dual-Channel Certificate Transfer for Carbon-Aware Supply Chain Routing: Using the MILP Shadow Price as Economic and Evolutionary Optimization Signal*  
**Target journal:** Supply Chain Analytics (Elsevier)  
**Decision type:** Desk rejection / not sent to peer review  
**Purpose of this document:** Diagnose why the manuscript failed at editorial screening and define a concrete rebuild plan.

---

## 1. Executive Diagnosis

The manuscript was not rejected because the computational idea is useless. It was rejected because the paper **oversold an algorithmic integration as a major supply-chain analytics contribution** and did not give the editor enough evidence that the work advances supply chain management theory or practice beyond performance gains from a hybrid MILP–MOEA implementation.

The editor’s message is unusually clear. The rejection rests on three main failures:

1. **Analytical novelty is judged incremental.**  
   The editor sees DCCT as a known type of hybrid optimization strategy: use mathematical-programming output to initialize or guide a heuristic/metaheuristic. The dual use of the primal solution and shadow price is interesting, but the paper does not prove that this changes supply-chain theory, decision logic, or managerial practice in a generalizable way.

2. **The paper is over-engineered and under-focused.**  
   Too many named modules, acronyms, propositions, policy claims, emissions-model details, and algorithmic claims compete for attention: DCCT, CARMA, CAPS, SPRD, PIEM, CRI, CI scheduling, EU ETS calibration, HOS constraints, dynamic carbon intensity, MoE, ablation, propositions. The editor could not easily identify the one central contribution.

3. **The empirical basis is too narrow for broad propositions.**  
   The paper uses synthetic/constructed route cases and internal emission-model validation, then makes broad claims about carbon-pricing equilibrium, policy, and managerial decision-making. That is exactly the kind of leap editors reject before review.

Bottom line: **a cosmetic revision will fail again.** The manuscript needs a strategic rebuild.

---

## 2. What SCA Expected

SCA is not simply looking for “an optimization algorithm that performs better.” It expects a paper to contribute to the forefront of supply chain management using analytics, OR, modeling, simulation, statistics, data science, or decision science. That means the paper must do at least one of the following convincingly:

- introduce a supply-chain decision problem that existing analytics cannot handle;
- provide a new analytical construct that changes how supply-chain decisions are evaluated;
- generate a validated decision framework with clear managerial implications;
- demonstrate generalizable insight across realistic supply-chain settings;
- connect methodology to supply-chain theory, not only algorithmic performance.

Your current manuscript mostly says: **“I combine MILP shadow price and NSGA-III reference direction conditioning and get better IGD.”**  
That is not enough for SCA. That reads as an evolutionary-computation implementation improvement, not a supply-chain analytics contribution.

---

## 3. Desk-Rejection Comment → Real Meaning → Required Fix

| Editor concern | What it really means | Required remediation |
|---|---|---|
| “Does not meet SCA’s publication standards” | The paper did not cross the threshold for novelty, clarity, and contribution at desk stage. | Rebuild contribution around a supply-chain decision construct, not an algorithm wrapper. |
| “Interesting integration… but not sufficiently significant methodological advance” | MILP-to-metaheuristic information transfer sounds familiar. | Stop claiming DCCT is fundamentally new unless you compare against exact hybrid optimization literature and show a new decision-theoretic role. |
| “Implementation strategy for improving search efficiency” | Editor sees DCCT as a performance hack. | Reposition the paper around **shadow-price-based carbon decision support**, not search speed. |
| “Benchmark comparisons… but methodological contribution remains incremental” | Better IGD/HV is not a publishable supply-chain contribution by itself. | Add evidence that λ* changes managerial decisions: buy allowance vs shift mode vs delay departure vs redesign network. |
| “Specialized terminology, acronyms, internally defined concepts” | The manuscript feels self-invented and noisy. | Cut acronyms aggressively. Keep one named framework maximum. |
| “Categorical novelty claims without sufficient analytical justification” | Statements like “nobody has done this” are dangerous. | Replace novelty claims with bounded claims and literature-mapped contrasts. |
| “Narrative shifts between algorithmic details, managerial interpretations, and policy implications” | The paper lacks a stable spine. | Choose one spine: **carbon-constrained intermodal decision support using endogenous marginal abatement cost**. |
| “Practical implications remain narrow and highly dependent on experimental setting” | Current case studies are not strong enough. | Add real or semi-real data, sensitivity experiments, and out-of-sample scenarios. |
| “Broader propositions… not supported by sufficiently extensive empirical evidence” | The propositions overclaim. | Remove or downgrade propositions to scenario-specific findings unless validated across many networks. |
| “Does not demonstrate new theoretical insights” | The paper lacks SCM theory contribution. | Anchor to carbon abatement cost curves, shadow-price decision thresholds, trade-off governance, or sustainable transport procurement theory. |

---

## 4. Biggest Problems in the Current Manuscript

### 4.1 The title signals algorithm novelty, not supply-chain contribution

Current title:

> Dual-Channel Certificate Transfer for Carbon-Aware Supply Chain Routing: Using the MILP Shadow Price as Economic and Evolutionary Optimization Signal

Problem: It screams “algorithm mechanism.” For SCA, the more compelling object is not “DCCT.” It is the **managerial use of the endogenous carbon shadow price**.

Better title direction:

> Carbon Shadow Prices as Decision Signals in Intermodal Supply Chain Routing: A Hybrid Optimization Framework for Mode Shift, Carbon Allowance, and Departure Timing Decisions

This moves the contribution from “we invented DCCT” to “we use shadow prices to structure carbon-constrained logistics decisions.”

### 4.2 Too many frameworks

Current manuscript contains:

- DCCT
- CARMA
- CAPS
- SPRD
- PIEM
- CRI
- CI scheduling
- MoE calibration
- ETS calibration
- HOS scenario
- multiple propositions
- scalability extrapolation

That is not richness. It is clutter. The editor could not tell what matters.

Recommended cut:

| Keep | Demote | Remove or appendix |
|---|---|---|
| Carbon shadow price decision logic | NSGA-III seeding and reference direction details | CAPS/SPRD branding |
| MILP + MOEA as implementation | PIEM as emissions-estimation module | MoE calibration claims |
| ETS allowance vs mode shift comparison | CI departure scheduling as secondary extension | HOS regulatory proposition |
| Managerial threshold rules | Ablation as robustness check | Big claims about equilibrium |

### 4.3 The manuscript overclaims theory from thin experiments

The paper currently claims:

- λ* ≈ EU ETS signals carbon-pricing equilibrium.
- Mode shifts are economically self-justifying.
- DCCT reduces risk of selecting dominated trade-offs.
- HOS regulation only slightly reduces savings.
- DCCT applies broadly beyond routing.

These may be interesting, but they are not adequately supported. The experiments are too small and partly synthetic. Also, the manuscript itself admits that λ* is floored/calibrated to EU ETS in some tests, which weakens the most important claim: that λ* is an endogenous shadow price.

This is a fatal issue. If λ* does not vary naturally with budget tightness, then the strongest conceptual claim collapses.

### 4.4 The current novelty comparison is too narrow

The manuscript compares mainly against a small set of SCA papers and carbon-aware routing work. That is insufficient. The editor is clearly thinking about the broader hybrid optimization literature: warm starts, matheuristics, Lagrangian-guided heuristics, adaptive reference vectors, exact-heuristic hybrids, and decomposition-based multi-objective optimization.

You must show:

- what existing matheuristics already do;
- what existing dual-guided heuristics already do;
- what existing adaptive reference-direction MOEAs already do;
- why your use of λ* is not merely another version of those.

Without that, “DCCT” will keep being seen as incremental.

---

## 5. Recommended Strategic Pivot

Do not resubmit the same paper as “DCCT/CARMA.” Rebuild it as a **shadow-price decision analytics paper**.

### New core research question

> How can the endogenous shadow price of a carbon-constrained logistics optimization model be used as a managerial decision signal for choosing among mode shift, carbon allowance purchase, and departure-time adjustment in intermodal supply chains?

This is more SCA-friendly because it is about supply-chain decision analytics, not only algorithm mechanics.

### New primary contribution

The primary contribution should be:

> A carbon shadow-price decision framework that converts the MILP dual value of a binding emissions constraint into operational thresholds for intermodal mode shifting, carbon-market comparison, and trade-off selection.

The hybrid MILP–MOEA mechanism becomes the computational engine, not the theoretical contribution.

### New secondary contribution

> A bounded hybrid optimization implementation that uses the primal MILP solution and shadow-price information to improve Pareto-front approximation for carbon-constrained routing.

This keeps DCCT, but demotes it.

### New empirical contribution

> Evidence across multiple realistic network archetypes showing when the shadow-price rule changes decisions relative to cost-only, emissions-only, ETS-only, and standard multi-objective optimization baselines.

That is the evidence SCA needs.

---

## 6. Revised Paper Architecture

### Proposed new title

**Carbon Shadow Prices as Decision Signals in Intermodal Supply Chain Routing: A Hybrid Optimization Framework for Mode Shift, Allowance Purchase, and Departure Timing**

Alternative shorter title:

**Shadow-Price Decision Analytics for Carbon-Constrained Intermodal Routing**

### Revised abstract structure

The abstract should stop leading with DCCT. It should follow this logic:

1. Carbon-constrained logistics decisions require managers to choose between physical abatement and market-based carbon compliance.
2. Existing routing models often compute shadow prices but rarely translate them into managerial decision rules.
3. This paper develops a shadow-price decision analytics framework for intermodal routing.
4. A MILP produces the primal routing solution and the marginal carbon abatement cost; a multi-objective search explores cost–emissions–time–reliability trade-offs.
5. Experiments across network archetypes test when λ* supports mode shift, allowance purchase, or departure-time adjustment.
6. Results show the conditions under which the shadow-price rule is reliable, and where it breaks down.
7. The contribution is a decision framework, not merely a faster optimizer.

### Revised section outline

1. **Introduction**
   - Problem: logistics managers need carbon decisions under emissions constraints.
   - Gap: optimization models compute shadow prices but do not turn them into operational decision thresholds.
   - Research questions.
   - Contributions, bounded and modest.

2. **Literature Review**
   - Carbon-constrained supply chain optimization.
   - Shadow prices and marginal abatement cost in operations decisions.
   - Hybrid MILP–metaheuristic/matheuristic methods.
   - Multi-objective routing and Pareto decision support.
   - Positioning table.

3. **Decision Framework**
   - Managerial decision problem.
   - Carbon budget constraint and λ* interpretation.
   - Decision rules:
     - if λ* < carbon market price → physical mode shift is economically attractive;
     - if λ* ≈ market price → indifference/parity zone;
     - if λ* > market price → allowance purchase or alternative abatement should be considered;
     - if CI savings are material and feasible → departure timing adjustment.
   - Assumptions and boundary conditions.

4. **Optimization Model**
   - MILP formulation.
   - Multi-objective extension.
   - Use of primal and dual information.
   - Reduce algorithm branding.

5. **Experimental Design**
   - Network archetypes.
   - Carbon budget sweep.
   - Carbon price sweep.
   - Mode availability sweep.
   - Demand/weight uncertainty.
   - Baselines.

6. **Results**
   - Shadow-price behavior across budgets.
   - Decision-regime maps.
   - Comparison with baselines.
   - Pareto-front quality as supporting evidence.
   - Sensitivity and failure cases.

7. **Discussion**
   - Theoretical contribution to supply-chain carbon decision analytics.
   - Practical decision rules.
   - Where the method should not be used.
   - Limitations.

8. **Conclusion**

---

## 7. Required Technical Fixes Before Resubmission Anywhere

### 7.1 Fix λ* computation

This is the highest-priority fix.

Current problem: the manuscript says the solver returns λ*=0.065 in several cases, and also says this is tied to an ETS calibration floor. That undermines the claim that λ* is an endogenous marginal abatement cost.

Required action:

- Run the MILP without embedding the ETS price as a floor or objective coefficient that mechanically fixes λ*.
- Report the true dual/shadow price of the carbon constraint.
- Show λ* varies with:
  - carbon budget tightness;
  - network topology;
  - mode availability;
  - shipment weight;
  - carbon-intensity profile;
  - reliability constraints.

Minimum evidence needed:

| Experiment | Required output |
|---|---|
| Budget sweep: 0–50% reduction | λ* curve; identify non-binding, binding, infeasible regions |
| Carbon price sweep | decision threshold between physical abatement and allowance purchase |
| Mode availability sweep | λ* response when rail/ship options are removed |
| Demand/weight sensitivity | λ* stability under load variation |
| Network archetype comparison | λ* differences by geography and modal structure |

If λ* is flat, DCCT is not a shadow-price framework. It is just a fixed parameter.

### 7.2 Add realistic data grounding

Synthetic data is acceptable for method development only if the claims are methodological and bounded. But SCA rejected the manuscript partly because practical implications were too narrow.

Minimum upgrade:

- Use real distances from OpenStreetMap/OSRM or verified intercity route distances.
- Use actual rail/ship availability rules where possible.
- Use public emission factors clearly.
- Use real hourly grid carbon intensity profiles from known data sources.
- Create at least 3–5 network archetypes:
  - Iberian regional network;
  - Rotterdam European hub;
  - US intermodal corridor;
  - island/maritime-dependent network;
  - rail-constrained network.

Better upgrade:

- Add one real-world public logistics dataset or semi-public freight lane dataset.
- Validate at least part of PIEM using external benchmark emission calculators or published emission factors.

### 7.3 Reduce or remove PIEM claims

PIEM is currently distracting. It is not validated against real telematics, so it cannot carry strong claims.

Recommended treatment:

- Keep PIEM as an emissions-estimation layer.
- Move formula details to appendix.
- Remove “ML-ready 15 features” as a highlighted contribution unless you validate predictive performance on real observations.
- Remove MoE MAPE as a main result if the target is synthetic. Synthetic-target MAPE looks weak and possibly circular.

Say this instead:

> We use a physics-informed emission estimator to maintain consistency across route, payload, speed, congestion, and weather scenarios. The estimator is not presented as a field-validated emissions predictor.

### 7.4 Downgrade algorithm-performance claims

Do not make “better IGD” the main story. Keep it as supporting evidence.

Required changes:

- Report statistical robustness: multiple seeds, not seed=42 only.
- Include confidence intervals or distributions.
- Compare with more relevant baselines:
  - MILP-only weighted-sum;
  - ε-constraint MILP;
  - random NSGA-III;
  - warm-start-only;
  - dual-guided-only;
  - adaptive reference-vector method if feasible;
  - MOEA/D.
- Stop arguing that HV is “wrong.” Say HV and IGD emphasize different qualities. The editor will not like categorical dismissal of a standard metric.

### 7.5 Remove broad propositions or recast as findings

Current “Propositions” sound theoretical but are empirically thin.

Replace:

> Proposition 4: λ* ≈ EU ETS signals carbon-pricing equilibrium.

With:

> Finding 4: In the Rotterdam scenario, λ* approaches the EU ETS benchmark, indicating a parity condition between modeled internal abatement cost and market allowance price under the tested assumptions.

That is defensible.

### 7.6 Add a limitation-first discussion

The editor explicitly asked for clearer assumptions, limitations, and methodological boundaries. Add a subsection early or in discussion:

- λ* is meaningful only when the carbon constraint is binding.
- λ* from MILP solvers can be delicate in integer models; explain how it is computed.
- If using LP relaxation duals, say so.
- If using MIP shadow prices from a fixed optimal basis or post-optimal analysis, explain.
- Carbon-market comparison is valid only when the emissions scope, geography, and regulatory coverage align.
- CI departure scheduling applies only to electrified or electricity-dependent transport portions.
- The approach is not appropriate for highly dynamic real-time routing without re-optimization.

---

## 8. Critical Methodological Issue: Shadow Prices in MILP

This must be handled carefully. In linear programming, shadow prices are well-defined dual variables. In integer programming, shadow prices are not always directly meaningful in the same way because integrality makes the value function non-convex and discontinuous.

Your manuscript currently talks about “MILP shadow price λ*” as if it is straightforward. A sharp reviewer will attack this.

You need one of the following defensible positions:

### Option A — Use LP relaxation duals explicitly

Say:

> λ* is obtained from the LP relaxation of the carbon-constrained assignment model at the optimal integer solution neighborhood and is interpreted as a local marginal value, not a global derivative of the integer value function.

This is honest but weakens the claim.

### Option B — Use ε-constraint finite differences

Compute:

> λ̂(B) = [Z(B + ΔB) − Z(B)] / ΔB

This is often more defensible for integer models. It estimates marginal abatement cost by resolving the MILP at slightly relaxed/tightened carbon budgets.

Recommended approach:

Use finite-difference marginal abatement cost as the primary “shadow price” and call solver duals supplementary.

This would make the paper much stronger.

### Option C — Use parametric MILP

Solve across budget levels and estimate piecewise marginal costs. This creates a proper abatement-cost curve.

Best SCA-friendly version:

> Instead of relying on a single solver-reported dual value, we construct a carbon abatement cost curve from parametric MILP solves and use its local slope as the decision signal.

This is much better than the current λ* claim.

---

## 9. Revised Contribution Statement

Use something like this:

> This study contributes to supply chain analytics by developing a shadow-price decision framework for carbon-constrained intermodal routing. Rather than treating the carbon constraint only as a feasibility requirement, the framework converts the marginal value of the emissions budget into a decision signal for mode-shift investment, carbon allowance comparison, and departure-time adjustment. Methodologically, the framework combines parametric MILP-based marginal abatement estimation with multi-objective Pareto exploration. Empirically, it maps decision regimes across carbon-budget tightness, carbon-price levels, modal availability, and network archetypes. The contribution is not a generic claim that hybrid MILP–MOEA methods are new; it is a decision-analytic use of endogenous carbon abatement cost to support sustainable logistics planning.

This is the level of humility and focus needed.

---

## 10. Revised Research Questions

Replace the current contribution framing with these:

**RQ1.** How does the marginal abatement cost of a carbon-constrained intermodal routing network change with carbon-budget tightness, modal availability, and network structure?

**RQ2.** When does the endogenous marginal abatement cost support physical mode shifting rather than market-based carbon allowance purchase?

**RQ3.** Does using exact-model information improve the quality of Pareto trade-off discovery enough to support managerial decision-making, beyond standard multi-objective baselines?

**RQ4.** Under what operational conditions does carbon-intensity-aware departure timing materially improve emissions outcomes?

These research questions are better aligned with SCA.

---

## 11. Revised Hypotheses / Findings Structure

Use “findings,” not “propositions,” unless you develop real theory.

Suggested findings:

- **Finding 1:** Marginal abatement cost is non-linear and regime-dependent; it increases sharply when low-carbon modes become saturated or unavailable.
- **Finding 2:** Physical mode shift is economically preferred when marginal abatement cost is below the relevant carbon price; allowance purchase becomes preferable above that threshold.
- **Finding 3:** Exact-model-informed Pareto search improves front coverage mainly in small-to-medium tactical networks, but the effect weakens or changes at larger scales.
- **Finding 4:** Departure-time adjustment provides secondary emissions savings only when the electrified component is substantial and scheduling flexibility exists.
- **Finding 5:** The framework fails or becomes unreliable when the carbon constraint is non-binding, modal alternatives are absent, or shadow-price estimates are flat/unstable.

This is much more credible.

---

## 12. Evidence Package Needed

Before sending to any strong journal, build this evidence package.

### 12.1 Minimum experiment matrix

| Dimension | Levels |
|---|---|
| Network size | 12, 25, 50, 100 routes |
| Network type | regional, port-hub, inland rail, maritime, rail-constrained |
| Carbon budget reduction | 0, 5, 10, 20, 30, 40, 50% |
| Carbon price | 0, 25, 50, 75, 100, 150 €/t |
| Mode availability | full, no rail, no ship, truck-only fallback |
| Demand/load variation | low, medium, high |
| Reliability disruption | none, moderate, high |
| CI flexibility | 0h, ±2h, ±4h, ±8h |
| Random seeds | at least 20 |

### 12.2 Minimum tables

1. Model notation and assumptions.
2. Literature positioning: carbon routing, matheuristics, shadow price, carbon market decision rules.
3. Network archetype definitions.
4. Baseline comparison.
5. Marginal abatement cost by budget and network.
6. Decision-regime table: shift vs allowance vs mixed.
7. Pareto quality with statistical significance.
8. Sensitivity and failure cases.
9. Managerial decision rules.
10. Limitations and boundary conditions.

### 12.3 Minimum figures

1. Conceptual decision framework.
2. Parametric abatement cost curve.
3. Decision-regime heatmap: λ̂ vs carbon price and budget.
4. Pareto fronts for representative network.
5. Baseline comparison under budget tightness.
6. Failure-case plot where λ̂ is unstable or non-binding.
7. Managerial workflow diagram.

---

## 13. Manuscript-Level Surgery

### Delete or move to appendix

- Long DCCT pseudo-code unless necessary.
- Theorem-heavy presentation unless the theorems are strengthened.
- “O(1) convergence” claim. This sounds overstated.
- Synthetic MoE MAPE as a main result.
- SCA-corpus “0/14” table. It looks weak and can irritate editors because it appears cherry-picked.
- Claims that MOEA/D’s HV is “inflated” or “not better.” Use balanced language.
- Broad “equilibrium” language unless supported by parametric evidence.

### Rewrite

- Abstract.
- Introduction.
- Contributions.
- Literature review.
- Discussion.
- Conclusion.

### Keep

- MILP + multi-objective routing setup.
- Carbon-price comparison idea.
- Budget tightness sweep.
- Ablation study, but expanded and statistically validated.
- CI scheduling, only as secondary module.
- Realistic intermodal case studies.

---

## 14. Suggested New Abstract

> Carbon-constrained logistics planning requires managers to decide whether emissions reductions should be achieved through physical mode shifts, carbon allowance purchase, or operational timing adjustments. Existing optimization models often impose carbon budgets but rarely translate the marginal value of those constraints into decision rules. This study develops a shadow-price decision analytics framework for intermodal supply chain routing. A parametric carbon-budget MILP is used to estimate marginal abatement costs across budget levels, while a multi-objective routing model explores cost, emissions, time, and reliability trade-offs. The resulting marginal abatement signal is compared with external carbon-price benchmarks to identify decision regimes in which mode shifting, allowance purchase, or mixed strategies are economically preferred. Computational experiments across multiple intermodal network archetypes show that marginal abatement costs are strongly regime-dependent, increasing when low-carbon modes become capacity-limited or unavailable. Exact-model-informed Pareto search improves trade-off coverage in small-to-medium tactical networks, but its benefit is conditional on network structure and budget tightness. The study contributes a decision-analytic interpretation of carbon shadow prices for sustainable logistics planning and clarifies the boundary conditions under which such signals are reliable.

This abstract is more publishable than the current one because it is not trying to sell an acronym.

---

## 15. Suggested New Introduction Contribution Paragraph

> This paper makes three contributions. First, it develops a shadow-price decision framework for carbon-constrained intermodal routing, converting the marginal cost of an emissions budget into operational rules for mode-shift, allowance-purchase, and timing decisions. Second, it estimates marginal abatement cost through parametric MILP analysis, addressing the limitations of relying on a single solver-reported dual value in mixed-integer models. Third, it evaluates whether exact-model information improves multi-objective trade-off discovery across network archetypes, budget levels, and modal-availability conditions. The contribution is deliberately bounded: the proposed framework is intended for tactical intermodal planning problems with identifiable modal alternatives and binding emissions constraints; it is not a universal real-time routing method.

This directly addresses the editor’s complaint about overclaiming.

---

## 16. Journal Strategy

### Do not immediately resubmit to SCA

A desk rejection at SCA means the editor has already formed a view that the current paper does not fit the journal’s threshold. Resubmitting a lightly revised version is a bad move.

Only consider SCA again if:

- title and framing are fundamentally changed;
- λ* issue is fixed using parametric MILP or finite-difference marginal abatement cost;
- experiments are expanded;
- claims are moderated;
- the manuscript clearly contributes to supply-chain decision analytics, not algorithm engineering.

### Better near-term target journals

Depending on how much you revise:

1. **Cleaner Logistics and Supply Chain**  
   Good fit if the paper focuses on sustainable logistics and carbon-aware decision rules.

2. **Transportation Research Part D**  
   Better if you strengthen emissions modeling and policy relevance with real transport data.

3. **Computers & Industrial Engineering**  
   Better if the algorithmic hybrid optimization contribution remains central.

4. **Expert Systems with Applications**  
   Better if ML/MOEA/decision-support performance remains central.

5. **Applied Soft Computing**  
   Better if DCCT remains primarily an evolutionary optimization mechanism.

6. **Sustainable Futures / Transportation Engineering**  
   Better if you want faster, applied sustainability route.

### Best strategic choice

If you want SCA-level relevance, rebuild around **shadow-price decision analytics**.  
If you want faster publication, retarget to an algorithm/application journal and keep DCCT as the main contribution.

---

## 17. Concrete 30-Day Remediation Plan

### Week 1 — Reframing and model correction

- Rewrite title, abstract, RQs, and contribution statement.
- Decide whether the primary paper is:
  - SCA-style decision analytics; or
  - algorithmic hybrid optimization.
- Remove acronym overload.
- Fix λ* computation:
  - implement finite-difference marginal abatement cost;
  - or implement parametric MILP budget sweep.
- Remove ETS floor from λ* calculation.

### Week 2 — New experiments

- Build budget sweep: 0–50%.
- Build carbon price sweep: 0–150 €/t.
- Build mode availability scenarios.
- Run at least 20 random seeds for MOEA results.
- Add at least one larger network: n=100.
- Generate marginal abatement curves.

### Week 3 — Rewrite results and discussion

- Replace propositions with findings.
- Add decision-regime heatmaps.
- Add failure cases.
- Move algorithm details to appendix.
- Add statistical robustness.
- Add limitation-first framing.

### Week 4 — Full manuscript rebuild

- Rewrite Introduction and Literature Review.
- Replace “DCCT novelty” with “shadow-price decision analytics.”
- Tighten conclusion.
- Prepare new cover letter explicitly explaining how the paper now addresses SCA concerns.
- Run references and DOI validation again.
- Prepare clean figures.

---

## 18. Cover Letter Strategy for a Rebuilt Submission

Do not say “we fixed the desk rejection.” Say:

> The manuscript has been substantially reframed from an algorithm-centered hybrid optimization paper into a supply-chain decision analytics study of carbon shadow prices in intermodal routing. The revised paper uses parametric MILP-based marginal abatement estimates, expanded scenario analysis, and decision-regime mapping to support mode-shift and carbon-market decisions.

This tells the editor it is a new paper, not a patched version.

---

## 19. High-Risk Claims to Avoid

Avoid these unless heavily supported:

- “No prior work has done this.”
- “Carbon-pricing equilibrium.”
- “Self-justifying mode shifts” as a general statement.
- “O(1) convergence” as a broad claim.
- “MOEA/D is biased / inferior.”
- “The framework generalizes to all supply chain problems.”
- “PIEM is accurate” without real validation.
- “MILP shadow price” without explaining integer-model dual limitations.

Safer phrasing:

- “To our knowledge, prior carbon-aware routing studies have not operationalized marginal abatement cost as a decision signal in this way.”
- “In the tested scenario, λ̂ falls below the selected carbon-price benchmark.”
- “The result suggests a parity condition under the modeled assumptions.”
- “Exact-solution seeding improves discovery of the certified extreme by construction.”
- “IGD and HV emphasize different aspects of approximation quality.”

---

## 20. Final Recommendation

The current manuscript should not be resubmitted as-is. The editor’s rejection is not a formatting complaint; it is a contribution complaint.

The strongest salvage path is:

1. **Stop selling DCCT as the main novelty.**
2. **Make shadow-price-based carbon decision analytics the main contribution.**
3. **Replace solver-reported λ* with parametric MILP or finite-difference marginal abatement cost.**
4. **Expand experiments into decision-regime evidence, not just algorithm benchmarks.**
5. **Remove acronym clutter and broad policy propositions.**
6. **Write the paper for supply-chain managers and analytics scholars, not evolutionary-computation reviewers.**

If you do this, the paper can become substantially stronger. If you only revise wording and add citations, it will likely be desk rejected again.
