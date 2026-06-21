# Exact Final Edits Before SCA Submission

**Manuscript:** *Marginal Abatement Cost as a Carbon Decision Signal in Intermodal Supply Chain Routing: A Parametric MILP Framework for Mode Shift, Allowance Purchase, and Departure Timing*  
**Target journal:** *Supply Chain Analytics* (Elsevier)  
**Purpose:** Exact manuscript edits to improve coherence, organization, clarity, central theme, SCA fit, and likely Reviewer 2 response.

---

## Overall Decision

The manuscript is now close to submission-ready. The central theme is coherent:

> **Parametric MILP estimates network-specific marginal abatement cost (MAC) curves, and those MAC curves become decision signals for choosing mode shift, allowance purchase, co-benefit decarbonization, or infeasibility response.**

The remaining work is not a full rewrite. It is a targeted cleanup to prevent reviewers from seeing the paper as:

1. an integrated-novelty paper,
2. an NSGA-III algorithm paper,
3. a stylized-case paper with overbroad claims,
4. or a manuscript with inconsistent notation.

Apply the edits below exactly.

---

# Edit 1 — Replace the Algorithm-Oriented Highlight

## Location

Highlights section.

## Current text

```markdown
- Exact-model-conditioned Pareto search improves trade-off coverage for tactical intermodal planning (n = 12–50, supporting contribution)
```

## Replace with

```markdown
- Supporting Pareto analysis shows the MAC-informed framework can improve trade-off coverage for tactical intermodal planning
```

## Reason

The current highlight pulls attention back to algorithm engineering. The replacement keeps the focus on MAC decision analytics while preserving the supporting computational result.

---

# Edit 2 — Rename “Table 0” as an Unnumbered Notation Box

## Location

Section 3.1, currently titled:

```markdown
**Table 0. Notation used in §3.**
```

## Replace with

```markdown
**Notation box for the MAC decision framework.**
```

## Reason

“Table 0” is nonstandard and looks unfinished. Since this is notation rather than a results table, make it an unnumbered box.

## Optional if journal requires numbering

If every table must be numbered, rename it as:

```markdown
**Table 1. Notation used in the MAC decision framework.**
```

Then renumber the current Table 1 and all later tables.

Recommended option: **use an unnumbered notation box** to avoid renumbering all tables.

---

# Edit 3 — Remove Route Symbol Conflict

## Problem

The manuscript uses `r` for two meanings:

1. carbon reduction target `r`;
2. route index `r`.

This can confuse reviewers because the MAC formula uses `r` as reduction target.

## Required rule

Use:

```text
ρ = route
r = carbon reduction target
π = carbon price
```

---

## Edit 3A — Section 4.1 Opening Definition

### Current text

```markdown
Let G = (V, E) be the supply chain network, R = {r₁, ..., rₙ} the route set, M = {truck, rail, ship, air} the transport mode set, and B ∈ ℝ₊ the carbon budget (kg CO₂e).
```

### Replace with

```markdown
Let G = (V, A) be the supply chain network, P = {ρ₁, ..., ρₙ} the route set, M = {truck, rail, ship, air} the transport mode set, and B ∈ ℝ₊ the carbon budget (kg CO₂e).
```

### Reason

Use `A` for arcs to avoid conflict with emissions `E`, and use `P`/`ρ` for routes to avoid conflict with reduction target `r`.

---

## Edit 3B — Section 4.1 Objective Functions

### Current text

```markdown
f₁(X) = Σᵣ Σₘ cᵣₘ · xᵣₘ
f₂(X) = Σᵣ Σₘ êᵣₘ · xᵣₘ
f₃(X) = Σᵣ Σₘ (dᵣ / vₘ) · xᵣₘ
f₄(X) = (1/|R|) Σᵣ CRI(r, m, θ) · xᵣₘ
```

### Replace with

```markdown
f₁(X) = Σρ∈P Σm∈M cρm · xρm
f₂(X) = Σρ∈P Σm∈M êρm · xρm
f₃(X) = Σρ∈P Σm∈M (dρ / vm) · xρm
f₄(X) = (1/|P|) Σρ∈P Σm∈M CRI(ρ, m, θ) · xρm
```

### Reason

This removes notation conflict and makes the fourth objective consistent with mode-indexed decisions.

---

## Edit 3C — Section 4.1 Constraints

### Current text

```markdown
(C1) Σₘ xᵣₘ = 1 ∀r
(C2) Σᵣ Σₘ êᵣₘ · xᵣₘ ≤ B
(C4) xᵣₘ ∈ {0, 1}
```

### Replace with

```markdown
(C1) Σm∈M xρm = 1 ∀ρ ∈ P
(C2) Σρ∈P Σm∈M êρm · xρm ≤ B
(C4) xρm ∈ {0, 1}
```

---

## Edit 3D — Section 4.2 MILP Formulation

### Current text

```markdown
min   Σᵣ Σₘ cᵣₘ · xᵣₘ
s.t.  Σᵣ Σₘ êᵣₘ · xᵣₘ ≤ B(r)
      Σₘ xᵣₘ = 1        ∀r
      xᵣₘ = 0  if mode infeasible
      xᵣₘ ∈ {0, 1}
```

### Replace with

```markdown
min   Σρ∈P Σm∈M cρm · xρm
s.t.  Σρ∈P Σm∈M êρm · xρm ≤ B(r)
      Σm∈M xρm = 1        ∀ρ ∈ P
      xρm = 0             if mode m is infeasible for route ρ
      xρm ∈ {0, 1}
```

---

# Edit 4 — Soften the “No Prior Work” Claim

## Location

Section 2.2 or 2.5.

## Current text

```markdown
No prior intermodal routing paper, to our knowledge, constructs a parametric MAC curve from sequential MILP solves and uses it to generate mode-shift vs allowance-purchase decision thresholds.
```

## Replace with

```markdown
To the best of our knowledge, prior intermodal routing studies have not used sequential MILP-derived MAC curves to classify mode-shift versus allowance-purchase decisions across network archetypes.
```

## Reason

This is still strong but less absolute. It avoids inviting a reviewer to find a borderline counterexample.

---

# Edit 5 — Strengthen the SCA Decision-Analytics Framing in the Abstract

## Location

End of abstract.

## Current final sentence

```markdown
The framework contributes a decision-analytic use of parametric MAC curves for sustainable logistics planning and clarifies, empirically, the network structural conditions under which physical mode shift, allowance purchase, or market-driven decarbonization are the rational compliance choice.
```

## Replace with

```markdown
The framework contributes a supply-chain decision-analytics method that converts parametric MAC curves into actionable carbon-compliance regimes, clarifying when physical mode shift, allowance purchase, co-benefit decarbonization, or network redesign is the rational response.
```

## Reason

This better matches *Supply Chain Analytics* scope and makes the contribution sound like decision analytics rather than only carbon modeling.

---

# Edit 6 — Move or Reframe RQ3 to Avoid Integrated-Novelty Risk

## Location

Section 1.3 Research Questions.

## Current RQ3

```markdown
RQ3. Does using exact-model information (certified primal solution and parametric MAC estimate) improve the quality of Pareto trade-off discovery for carbon-constrained routing, beyond standard multi-objective baselines?
```

## Replace with

```markdown
RQ3. As a supporting analysis, can exact-model information improve Pareto trade-off discovery after MAC-based regime classification has identified the decision-relevant region?
```

## Reason

This keeps RQ3 but makes it subordinate to the MAC decision framework.

---

# Edit 7 — Clarify Contribution 3 Is Optional / Supporting

## Location

Section 1.4 Contributions, Contribution 3.

## Current text

```markdown
Using the certified MILP primal solution to seed the NSGA-III population and the MAC estimate to concentrate reference directions improves Pareto front approximation in small-to-medium tactical networks (n = 12–50 routes). This contribution is deliberately bounded: the benefit weakens at larger networks and does not justify the computational overhead if single-objective routing suffices.
```

## Replace with

```markdown
After the MAC regime is classified, the certified MILP primal solution and MAC estimate can also support Pareto trade-off exploration by seeding NSGA-III and concentrating reference directions toward decision-relevant regions. This is a supporting implementation result, not a required component of the primary framework. The benefit is bounded to small-to-medium tactical networks (n = 12–50 routes), weakens at larger networks, and does not justify additional computational overhead when single-objective regime classification is sufficient.
```

## Reason

This removes remaining integrated-novelty risk.

---

# Edit 8 — Reorder Section 6 So MAC Robustness Comes Before Pareto Search

## Current order

```markdown
6.1 MAC curves
6.2 Decision-regime analysis
6.3 Boundary conditions
6.4 Pareto front quality
6.5 Departure timing
6.6 Budget-step robustness
6.7 Parameter sensitivity
6.8 Generated-network robustness
```

## Recommended order

```markdown
6.1 MAC curves
6.2 Decision-regime analysis
6.3 Boundary conditions
6.4 Budget-step robustness
6.5 Parameter sensitivity
6.6 Generated-network robustness
6.7 Departure timing
6.8 Supporting Pareto front quality from exact-model conditioning
```

## Reason

The current Section 6.4 interrupts the main MAC evidence. Move Pareto search after all MAC robustness evidence so the reader sees it as secondary.

## Required renaming

Rename:

```markdown
### 6.4 Pareto Front Quality from Exact-Model Conditioning (RQ3)
```

to:

```markdown
### 6.8 Supporting Pareto Front Quality from Exact-Model Conditioning (RQ3)
```

---

# Edit 9 — Reduce the Number of “Findings”

## Problem

The manuscript currently has 17 findings. That is too many and makes the paper feel fragmented.

## Required fix

Keep only 9 findings.

## Recommended merged structure

```markdown
Finding 1: MAC curves are step-function-shaped and network-structure-dependent.
Finding 2: Modal structure determines compliance regime.
Finding 3: LP duals are unreliable; finite-difference MAC is required.
Finding 4: At current ETS prices, rail-limited domestic mode shift remains allowance-preferred.
Finding 5: Maritime-accessible networks can exhibit co-benefit decarbonization.
Finding 6: Hub networks can face hard modal abatement ceilings.
Finding 7: Regime classification is robust to budget-step size.
Finding 8: Sensitivity and generated-network tests confirm regime stability under controlled variation.
Finding 9: Exact-model-conditioned Pareto search is useful only as supporting trade-off exploration.
```

## Reason

This makes the results read like one coherent argument rather than many disconnected observations.

---

# Edit 10 — Add Generated-Network Design Details

## Location

Section 6.8 or Appendix A.

## Add this paragraph

```markdown
The generated networks are not intended to estimate real-world frequencies of carbon-compliance regimes. They are controlled robustness instances designed to test whether the regime taxonomy remains stable under variation in modal economics. For each archetype family, route distances, cargo weights, terminal costs, modal cost multipliers, emission factors, and modal availability were sampled within the ranges reported in Appendix A. The defining structural condition of each family was preserved: rail-limited domestic networks permit truck/rail choices only; maritime-accessible networks include long-haul ship options; and hub-limited networks include constrained rail availability, higher rail emission factors, and selected express/air options.
```

## Add Appendix A table

```markdown
## Appendix A. Generated-Network Parameter Ranges

| Parameter | Rail-limited domestic | Maritime-accessible | Hub-limited redundancy |
|---|---:|---:|---:|
| Number of routes | 12–50 | 12–50 | 12–50 |
| Route distance | 60–550 km | 400–2,500 km | 250–1,800 km |
| Cargo weight | [insert range] | [insert range] | [insert range] |
| Rail terminal cost | €300–€1,200 | €300–€1,200 | €300–€1,200 |
| Ship terminal cost | — | €250–€1,500 | — |
| Truck cost multiplier | 0.75–1.50× baseline | 0.75–1.50× baseline | 0.75–1.50× baseline |
| Rail cost multiplier | 0.50–1.50× baseline | 0.50–1.50× baseline | 0.50–1.50× baseline |
| Ship cost multiplier | — | 0.75–1.50× baseline | — |
| Rail emission factor multiplier | 0.50–1.60× baseline | 0.50–1.60× baseline | 0.50–1.60× baseline |
| Ship emission factor multiplier | — | 0.70–1.30× baseline | — |
| Rail availability rule | available above route-distance threshold | available above route-distance threshold | limited availability |
| Ship availability rule | not available | available on long-haul/coastal routes | not available |
```

Replace `[insert range]` with the actual weight ranges used in your scripts.

## Reason

Reviewer 2 will ask how the 150 generated networks were generated. This appendix prevents that objection.

---

# Edit 11 — Clarify EU ETS Is Used as a Benchmark, Not a Legal Coverage Claim

## Location

Section 7.3 Limitations, “Carbon market scope.”

## Current text

```markdown
Comparison to EU ETS prices assumes the network's emissions are covered by EU ETS Phase IV scope. For Scope 3 emissions or non-EU jurisdictions, the comparison carbon price must be adjusted to the relevant market or regulatory instrument.
```

## Replace with

```markdown
The EU ETS price is used as a benchmark carbon price for decision analysis, not as a claim that every modeled shipment is legally covered by EU ETS obligations. For Scope 3 emissions, voluntary targets, or non-EU jurisdictions, π should be replaced by the relevant internal carbon price, allowance price, carbon tax, or regulatory benchmark. The MAC framework remains unchanged; only the comparison price changes.
```

## Reason

This pre-empts Reviewer 2 criticism about ETS legal scope.

---

# Edit 12 — Improve Section 6 Opening

## Location

Start of Section 6.

## Current text

```markdown
Because the three named networks are archetypes rather than representative samples, the empirical objective is not to estimate population-wide logistics behavior.
```

## Replace with

```markdown
Because the three named networks are archetypes rather than representative samples, the empirical objective is not to estimate population-wide logistics behavior or the frequency of each regime in practice. The objective is to test whether the MAC-based regime taxonomy behaves coherently under structurally distinct modal conditions and remains stable under controlled perturbations of modal cost, emission factors, carbon prices, and budget-step size.
```

## Reason

This directly addresses likely Reviewer 2 concern about stylized data.

---

# Edit 13 — Strengthen the Main-Theme Sentence in the Conclusion

## Location

Final paragraph of conclusion.

## Current text

```markdown
The primary contribution is a decision-analytic framework, not a generic algorithmic advance. Its value is in converting computationally generated marginal abatement cost curves into actionable logistics management decisions under carbon constraints.
```

## Replace with

```markdown
The primary contribution is a supply-chain decision-analytics framework, not a generic algorithmic advance. Its value lies in converting parametric MILP-derived marginal abatement cost curves into actionable carbon-compliance regimes for intermodal logistics: shift modes when internal abatement is cheaper than market compliance, buy allowances when market compliance is cheaper, recognize co-benefit decarbonization when the constraint is non-binding, and identify infeasible targets when modal alternatives are exhausted.
```

## Reason

This closes the manuscript with the central main theme.

---

# Edit 14 — Add a Reviewer 2 Defense Paragraph in Discussion

## Location

End of Section 7.3 Limitations and Boundary Conditions.

## Add

```markdown
These limitations do not invalidate the regime taxonomy; they define the conditions under which it should be applied. The numerical MAC values reported here should not be transferred directly to other logistics networks. Instead, the contribution is the repeatable decision procedure: estimate the network-specific MAC curve through parametric MILP, compare it with the relevant carbon price, and classify the resulting compliance regime. Any new geography, carrier mix, fuel market, or regulatory environment should therefore be evaluated by rerunning the framework rather than importing the numerical thresholds reported in this study.
```

## Reason

This pre-empts the most likely reviewer concern: “Your data are stylized; why should we trust generalization?”

---

# Edit 15 — Verify Repository Claims

## Location

Data Availability section.

## Current claim

The manuscript lists:

```markdown
experiments/parametric_abatement.py
experiments/budget_step_robustness.py
experiments/parameter_sensitivity.py
experiments/generate_figures.py
experiments/scalability_benchmark.py
experiments/demo_carma.py
algorithm/optimization/carbon_milp.py
paper/figures/fig2_mac_curves.pdf
paper/figures/fig3_regime_heatmaps.pdf
```

## Required action

Before submission, verify that every listed file actually exists in the GitHub repository.

## If all files exist, keep as is.

## If some files do not exist, replace with

```markdown
All code, datasets, and results required to reproduce the experiments will be made available in the public repository upon acceptance. The replication package includes scripts for parametric MAC estimation, budget-step robustness, parameter sensitivity, generated-network robustness, figure generation, multi-objective benchmarking, and departure-timing analysis.
```

## Reason

If the repo does not contain the listed files, reviewers may treat the data availability statement as inaccurate.

---

# Edit 16 — Correct Remaining `p` Labels in Tables

## Location

Table 4.

## Current header

```markdown
p=25 €/t | p=50 €/t | p=65 €/t | p=75 €/t | p=100 €/t | p=150 €/t
```

## Replace with

```markdown
π=25 €/t | π=50 €/t | π=65 €/t | π=75 €/t | π=100 €/t | π=150 €/t
```

## Reason

Carbon price is now `π`, not `p`.

---

# Edit 17 — Make SCA Scope Explicit in Introduction

## Location

End of Section 1.4 Contributions or start of Section 1.5 Scope.

## Add

```markdown
The paper is positioned as supply-chain analytics because the output is not only an optimized route assignment, but a repeatable decision rule linking optimization outputs to managerial carbon-compliance actions. The analytical object is the compliance regime, not the route plan alone.
```

## Reason

This reinforces fit with *Supply Chain Analytics* and prevents the manuscript from being read as only a transportation optimization paper.

---

# Edit 18 — Tighten Section 2.3 and 2.4 Headings

## Current headings

```markdown
### 2.3 Hybrid Exact-Heuristic Methods
### 2.4 Multi-Objective Routing and Pareto Decision Support
```

## Replace with

```markdown
### 2.3 Exact-Heuristic Search as Supporting Decision Exploration
### 2.4 Pareto Front Quality Metrics for Supporting Trade-Off Analysis
```

## Reason

This makes the algorithm discussion visibly secondary.

---

# Edit 19 — Add a Sentence Before Section 2.3

## Location

End of Section 2.2, before Section 2.3.

## Add

```markdown
Because the primary contribution is the MAC-based compliance regime rather than a new evolutionary algorithm, the exact-heuristic literature is reviewed only to position the supporting Pareto-search component.
```

## Reason

This directly controls integrated-novelty risk.

---

# Edit 20 — Final Reviewer 2 Checklist

Before submission, confirm:

- [ ] Main theme is MAC decision analytics, not DCCT/CARMA or NSGA-III.
- [ ] Abstract mentions MAC regimes, not algorithm novelty.
- [ ] Highlights do not overemphasize exact-model-conditioned Pareto search.
- [ ] “Table 0” is removed or renamed.
- [ ] Route notation uses `ρ`, reduction target uses `r`, carbon price uses `π`.
- [ ] All remaining `p=` carbon price labels are changed to `π=`.
- [ ] Pareto results appear after MAC robustness or are clearly labeled as supporting.
- [ ] Findings are reduced or grouped.
- [ ] Generated-network rules are included in Appendix A or repository.
- [ ] EU ETS is described as a benchmark price, not universal legal coverage.
- [ ] Data Availability matches the actual GitHub repository.
- [ ] Claims are bounded to archetype-level evidence.
- [ ] “No prior work” wording is softened.
- [ ] The final conclusion explicitly states the compliance-regime decision logic.

---

## Final Submission Recommendation

After these edits, the manuscript should be submitted as a **Supply Chain Analytics research article** with the following contribution statement:

```markdown
This paper develops a parametric MAC-based carbon decision analytics framework for intermodal supply-chain routing. The framework estimates network-specific marginal abatement cost curves from sequential MILP solves and converts them into actionable carbon-compliance regimes: mode shift preferred, parity, allowance purchase preferred, co-benefit decarbonization, and infeasible target. The contribution is not a generic algorithmic advance, but a decision-analytic conversion of integer optimization outputs into managerial carbon-compliance guidance.
```

Do not present the paper as an integrated novelty combining MILP, MAC, NSGA-III, carbon intensity, and emission modeling. Present it as one clear contribution:

> **MAC-based carbon compliance regime classification for intermodal supply-chain routing.**
