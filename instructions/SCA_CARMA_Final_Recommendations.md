# Final Recommendations for SCA Resubmission

**Manuscript:** *Marginal Abatement Cost as a Carbon Decision Signal in Intermodal Supply Chain Routing: A Parametric MILP Framework for Mode Shift, Allowance Purchase, and Departure Timing*  
**Target journal:** *Supply Chain Analytics* (Elsevier)  
**Purpose:** Final remediation recommendations before resubmission after the SCA desk rejection.

---

## 1. Executive Verdict

The current manuscript is **substantially stronger** than the earlier DCCT/CARMA version. The central contribution is now framed correctly as a **parametric marginal-abatement-cost (MAC) carbon decision analytics framework**, not as a generic algorithmic contribution.

The paper is now suitable in concept for *Supply Chain Analytics*, but it should **not be resubmitted yet**. The remaining weakness is empirical credibility. The current three-network evidence is useful, but it still looks like a structured demonstration rather than a sufficiently robust validation. SCA will likely expect stronger evidence that the observed regimes are not artifacts of the chosen examples.

**Current readiness:** 8.5 / 10  
**Desk-reject risk:** moderate  
**Reviewer rejection risk:** moderate unless robustness evidence is added  
**Recommended action:** add a robustness package before resubmission.

---

## 2. Core Contribution to Preserve

The main contribution should remain:

> This paper develops a marginal-abatement-cost-based carbon decision analytics framework that uses parametric MILP to estimate network-specific MAC curves and translates those curves into operational carbon compliance regimes for intermodal routing: mode shift preferred, parity, allowance purchase preferred, co-benefit decarbonization, and infeasible target.

This is the strongest SCA-facing contribution. It directly addresses the previous editor criticism that the old manuscript was too focused on algorithm engineering and not enough on supply-chain analytics insight.

The manuscript should consistently emphasize:

1. **Decision analytics**, not algorithm novelty.
2. **Parametric MAC**, not solver shadow price.
3. **Network-specific carbon compliance regimes**, not generic claims about all logistics networks.
4. **Managerial decision rules**, not only computational performance metrics.

---

## 3. Terminology Rule

Do **not** call the primary contribution “shadow-price-based” in the manuscript title, abstract, cover letter, or highlights.

Use:

> Parametric marginal-abatement-cost-based carbon decision analytics

You may say:

> The framework is motivated by the economic interpretation of carbon shadow prices, but operationalizes the signal through finite-difference marginal abatement cost because mixed-integer routing models do not provide reliable LP dual prices.

Reason: the manuscript correctly states that CBC reported LP shadow prices of zero for all tested carbon budget constraints. Therefore, calling the actual method “shadow-price-based” invites a technical rejection. The safe and accurate framing is **MAC-based**, **shadow-price motivated**.

---

## 4. What Has Been Fixed Successfully

| Previous weakness | Current status |
|---|---|
| Title overclaimed shadow-price novelty | Fixed: title now leads with MAC and parametric MILP |
| Abstract overemphasized DCCT/NSGA-III | Fixed: abstract now leads with MAC decision regimes |
| Contribution hierarchy unclear | Fixed: primary contribution is MAC decision framework |
| Regime taxonomy inconsistent | Fixed: five regimes are now separated into core economic and boundary regimes |
| Novelty grounding weak | Much improved: literature now includes MAC curves, integer step functions, modal shift, ETS comparisons |
| Archetype logic absent | Fixed: Salamanca, Iberian, and Frankfurt are justified as structural archetypes |
| Algorithm engineering too dominant | Mostly fixed: exact-model-conditioned Pareto search is now supporting only |

---

## 5. Remaining Critical Weakness

The empirical evidence is still too limited for broad claims.

The current manuscript uses three archetypes:

1. Salamanca domestic truck-rail network.
2. Iberian regional truck-rail-ship network.
3. Frankfurt European hub truck-rail-air network.

This is a good start. However, a skeptical SCA reviewer may ask:

> Are these regime conclusions robust, or are they artifacts of three hand-built examples?

The manuscript must show that the findings survive parameter uncertainty, cost uncertainty, emission-factor uncertainty, budget-step uncertainty, and generated-network variation.

---

## 6. Minimum Robustness Package Before Resubmission

Before resubmitting to SCA, add the following five items.

### 6.1 MAC Step-Function Figures

Add a figure showing MAC behavior for each network.

**Recommended figure:**

**Fig. 2. Parametric MAC curves across network archetypes**

Panel structure:

- Fig. 2a — Salamanca domestic truck-rail MAC step function.
- Fig. 2b — Iberian maritime co-benefit regime.
- Fig. 2c — Frankfurt abatement ceiling and infeasibility.

Recommended axes:

- x-axis: carbon reduction target (%).
- left y-axis: optimal logistics cost (€).
- right y-axis: MAC (€/t CO₂e).
- markers: mode-shift thresholds.
- shaded area: non-binding or infeasible regions.

Purpose: visually prove that MAC is step-function-shaped because of integer mode assignment.

---

### 6.2 Decision-Regime Heatmaps

Add regime heatmaps for all three networks.

**Recommended figure:**

**Fig. 3. Carbon compliance regime maps by carbon price and budget target**

Axes:

- x-axis: carbon price, e.g., €25, €50, €65, €75, €100, €150, €250, €500/t.
- y-axis: budget reduction, e.g., 0–50%.
- cell color: decision regime.

Suggested colors:

- Green: mode shift preferred.
- Yellow: parity.
- Red: allowance purchase preferred.
- Blue: co-benefit decarbonization.
- Gray: infeasible.

Purpose: show that the regime results hold across policy scenarios, not just the EU ETS 65 €/t baseline.

---

### 6.3 Parameter Sensitivity Table

Add a new results subsection:

**6.6 Robustness of Carbon Compliance Regimes**

Run sensitivity sweeps for the parameters most likely to change the decision regime.

| Parameter | Recommended values |
|---|---|
| Rail terminal cost | €300, €500, €680, €900, €1,200 |
| Ship terminal cost | €250, €500, €750, €1,000, €1,500 |
| Truck cost rate | −25%, baseline, +25%, +50% |
| Rail cost rate | −25%, baseline, +25% |
| Ship cost rate | −25%, baseline, +25%, +50% |
| Rail emission factor | −30%, baseline, +30%, +60% |
| Ship emission factor | −30%, baseline, +30% |
| Carbon price | €25, €50, €65, €75, €100, €150, €250, €500/t |
| Budget step size | 2.5%, 5%, 10% |

Report a table like this:

| Network | Baseline regime at 20% | % scenarios same regime | Most sensitive parameter | Flip threshold |
|---|---:|---:|---|---:|
| Salamanca | Allowance preferred | TBD | Rail terminal cost | TBD |
| Iberian | Co-benefit | TBD | Ship cost rate | TBD |
| Frankfurt | Allowance / infeasible boundary | TBD | Rail emission factor / modal availability | TBD |

Purpose: prove that regime classification is not a single-parameter artifact.

---

### 6.4 Generated-Network Robustness

Three named networks are not enough. Add a controlled generated-instance experiment.

Generate at least **30 networks per archetype family**. Better: 50–100 per family.

| Archetype family | Minimum instances | Vary |
|---|---:|---|
| Rail-limited domestic | 30–100 | distance, cargo weight, terminal cost, rail availability |
| Maritime-accessible long-haul | 30–100 | ship distance, ship cost, port access, terminal cost |
| Hub-and-spoke limited redundancy | 30–100 | rail availability, air availability, rail emission factor, route distance |

For each generated network, run:

1. Unconstrained cost MILP.
2. Parametric budget sweep from 0–50%.
3. MAC calculation.
4. Regime classification at EU ETS 65 €/t.
5. Maximum feasible abatement calculation.

Report:

| Archetype family | Co-benefit | Mode shift preferred | Allowance preferred | Infeasible above target | Median MAC €/t |
|---|---:|---:|---:|---:|---:|
| Rail-limited domestic | TBD | TBD | TBD | TBD | TBD |
| Maritime-accessible | TBD | TBD | TBD | TBD | TBD |
| Hub-and-spoke | TBD | TBD | TBD | TBD | TBD |

Purpose: transform the evidence from “three examples” to “archetype-level empirical regularities.”

---

### 6.5 Budget-Step Robustness

Because MAC is estimated by finite difference, reviewers may ask whether the 5% step size creates artificial jumps.

Run the parametric sweep at:

- 2.5% step.
- 5% step.
- 10% step.

Report:

| Network | 2.5% step regime | 5% step regime | 10% step regime | Stable? |
|---|---|---|---|---|
| Salamanca | TBD | Allowance | TBD | TBD |
| Iberian | TBD | Co-benefit | TBD | TBD |
| Frankfurt | TBD | Allowance / infeasible | TBD | TBD |

Purpose: defend the finite-difference MAC method.

---

## 7. Optional but High-Value Addition: Regime Driver Model

If time allows, add a simple explanatory model using generated networks.

Dependent variable:

- carbon compliance regime class.

Candidate explanatory features:

- average route distance,
- share of routes with rail available,
- share of routes with ship available,
- average rail/truck cost ratio,
- average ship/truck cost ratio,
- terminal cost as % of route cost,
- emission reduction potential,
- modal redundancy index,
- carbon budget tightness.

Possible models:

- multinomial logistic regression,
- decision tree,
- random forest feature importance,
- ANOVA with partial dependence plots.

Do not oversell prediction. Use the model to explain **which network features drive each regime**.

Recommended table:

| Driver | Expected effect |
|---|---|
| Higher rail terminal cost | Increases MAC; favors allowance purchase |
| Longer maritime-accessible distance | Lowers cost and emissions; favors co-benefit |
| Higher modal redundancy | Increases feasible abatement ceiling |
| Tighter budget | Increases MAC and infeasibility risk |
| Lower rail emission factor | Expands mode-shift-preferred region |

Purpose: strengthen the analytics contribution beyond optimization demonstration.

---

## 8. Claim Boundaries

Do not use broad claims. Use bounded, evidence-consistent claims.

| Risky claim | Safer claim |
|---|---|
| Carbon pricing is ineffective for domestic logistics. | In the rail-limited domestic archetype tested here, MAC remains above EU ETS prices under evaluated sensitivity ranges, implying allowance purchase is economically preferred unless terminal costs fall or carbon prices rise materially. |
| Maritime transport always creates co-benefit decarbonization. | Maritime-accessible long-haul routes can produce co-benefit decarbonization when ship is both lower-cost and lower-emission than truck. |
| The framework generalizes to all logistics networks. | The framework is general, but regime outcomes are network-specific and must be recomputed for each network. |
| LP shadow price is the decision signal. | The framework is shadow-price motivated but uses finite-difference MAC because LP duals are unreliable for MIP. |
| DCCT is the main novelty. | Exact-model-conditioned Pareto search is a supporting implementation for trade-off exploration. |

Add a table to the Discussion:

**Table X. Strength of empirical claims and allowed generalization**

| Claim | Evidence strength | Allowed wording |
|---|---|---|
| MAC is step-function-shaped in integer mode assignment | Strong after step-function plots | General mechanism for discrete mode assignment |
| Salamanca-like rail-limited networks often exceed ETS prices | Moderate/strong after sensitivity | Archetype-level claim |
| Maritime corridors can show co-benefit decarbonization | Moderate | Condition-specific claim |
| Carbon pricing is redundant in all maritime networks | Weak | Do not claim |
| Framework applies to any network without recalibration | Weak | Do not claim |

---

## 9. Manuscript Edits by Section

### Abstract

Keep the abstract focused on:

- carbon compliance decision problem,
- parametric MAC estimation,
- regime taxonomy,
- three archetypes,
- robustness/sensitivity if added.

Avoid detailed NSGA-III language in the abstract. One sentence is enough if needed.

### Introduction

Preserve the current contribution structure. Add one paragraph explaining that the paper tests whether regime outcomes are structural rather than example-specific using sensitivity and generated-instance robustness.

### Literature Review

The current literature review is much stronger. Keep the added MAC/logistics literature. Ensure every new citation appears in the reference list and every reference is cited in text.

### Methodology

Add a clear algorithm box:

**Algorithm 1. MAC-based carbon compliance regime classification**

Inputs:

- route set,
- feasible modes,
- mode costs,
- emission factors,
- budget targets,
- carbon price scenarios.

Steps:

1. Solve unconstrained cost MILP.
2. Check co-benefit condition.
3. Solve parametric MILP across budget levels.
4. Compute finite-difference MAC.
5. Compare MAC to carbon price.
6. Classify regime.
7. Report recommendation.

Outputs:

- MAC curve,
- regime map,
- recommended compliance action,
- infeasibility threshold.

### Results

Add:

- MAC step-function plots,
- regime heatmaps,
- sensitivity table,
- generated-instance robustness table,
- budget-step robustness table.

### Discussion

Add:

- claim-boundary table,
- regime driver interpretation,
- stronger managerial implications.

### Limitations

Keep the current limitations. Add:

> Results are archetype-level rather than population-level. The framework is general, but the regime classification is not transferable without rerunning the parametric MILP for the specific logistics network.

---

## 10. Suggested New Paragraph for Section 6

Add this near the beginning of the Results section:

> Because the three named networks are archetypes rather than representative samples, the empirical objective is not to estimate population-wide logistics behavior. The objective is to test whether the MAC-based regime taxonomy is stable under structurally distinct modal conditions and under plausible perturbations of terminal costs, modal cost rates, emission factors, carbon prices, and budget step sizes. We therefore supplement the three base networks with sensitivity sweeps and generated-network robustness tests. This design evaluates whether the identified regimes are structural consequences of modal economics rather than artifacts of a single parameterization.

---

## 11. Suggested Managerial Contribution Paragraph

Add this to the Discussion:

> The managerial value of the framework is not that it provides a universally optimal carbon strategy, but that it prevents managers from applying the wrong instrument to the wrong network. In a rail-limited domestic network, forcing mode shift may impose an internal abatement cost far above the carbon market price, making allowance purchase economically rational. In a maritime-accessible long-haul network, the cost-optimal solution may already decarbonize the network, making active carbon pricing unnecessary. In a limited-redundancy hub network, the framework identifies the hard abatement ceiling beyond which no feasible modal reassignment can satisfy the target. These distinctions are invisible in a conventional carbon-budget MILP that reports only the optimal assignment.

---

## 12. Recommended Final Submission Positioning

Submit only after adding the robustness package.

Recommended cover-letter framing:

> This manuscript responds directly to the need for supply-chain decision analytics under carbon constraints. Rather than proposing another carbon-aware routing algorithm, the paper develops a parametric MILP framework that converts marginal abatement cost curves into operational carbon compliance regimes. The contribution is decision-analytic: it identifies when a logistics manager should shift modes, purchase carbon allowances, exploit co-benefit decarbonization, or recognize that a budget target is infeasible under current modal alternatives.

Do not frame the paper as:

- DCCT,
- CARMA,
- shadow-price optimization,
- NSGA-III improvement,
- evolutionary optimization novelty.

Frame it as:

- MAC-based carbon decision analytics,
- parametric MILP for integer logistics networks,
- carbon compliance regime classification,
- sustainable logistics decision support.

---

## 13. Final Pre-Submission Checklist

Do not submit until all items below are complete.

| Item | Status |
|---|---|
| Title uses MAC, not shadow price | Done |
| Abstract leads with decision analytics | Done |
| Contribution hierarchy demotes NSGA-III | Done |
| Literature review grounds MAC and logistics gap | Mostly done |
| Regime taxonomy is internally consistent | Done |
| Archetype logic is explained | Done |
| MAC step-function figures added | Done — paper/figures/fig2_mac_curves.pdf |
| Regime heatmaps added | Done — paper/figures/fig3_regime_heatmaps.pdf |
| Parameter sensitivity table added | Done — §6.7, Table 7 (240 cells, 72% allowance preferred) |
| Generated-network robustness added | Done — §6.8, Table 9 (50×3=150 networks, 1,650 MILP solves); rail:0% shift_preferred, maritime:100% co-benefit, hub:52% infeasible below 20% |
| Budget-step robustness added | Done — §6.6, Table 6 (18/18 stable, 100%) |
| Claim-boundary table added | Done — §7.1, Table 8 |
| All new references validated with DOI/URL | Done — [30]-[44] added with DOIs |
| Cover letter reframed around MAC decision analytics | Required |
| Data/code availability updated for new robustness scripts | Done |

---

## 14. Bottom-Line Recommendation

The manuscript is now conceptually viable for *Supply Chain Analytics*, but the evidence must be strengthened before resubmission.

The minimum acceptable empirical upgrade is:

1. MAC step-function plots for the three networks.
2. Regime heatmaps for budget × carbon price.
3. Sensitivity analysis for terminal costs, modal cost rates, emission factors, and budget step size.
4. Generated-network robustness with at least 30 instances per archetype family.
5. Claim-boundary table defining exactly what can and cannot be generalized.

With those additions, the paper moves from:

> A good framework illustrated on three examples

To:

> A credible SCA decision-analytics paper with archetype-level validation and robustness evidence

That is the difference between another desk-reject risk and a paper likely to enter peer review.
