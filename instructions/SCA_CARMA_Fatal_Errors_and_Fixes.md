# Fatal Errors and Required Fixes Before SCA Submission

**Manuscript:** *Marginal Abatement Cost as a Carbon Decision Signal in Intermodal Supply Chain Routing: A Parametric MILP Framework for Mode Shift, Allowance Purchase, and Departure Timing*  
**Target journal:** *Supply Chain Analytics* (Elsevier)  
**Purpose:** Final technical correction checklist before resubmission.

---

## Executive verdict

The manuscript is now directionally strong and much closer to SCA expectations. The main contribution is no longer weak algorithm engineering; it is now a **parametric marginal-abatement-cost (MAC) decision analytics framework** for carbon compliance choices in intermodal supply-chain routing.

However, the manuscript should **not** be submitted until the following fatal issues are corrected.

---

# Fatal Error 1 — MAC Formula Sign Is Wrong

## Current problem

The current finite-difference MAC formula is written as:

```text
λ̂(B) = [Z(B − ΔB) − Z(B)] / [E(B − ΔB) − E(B)]
```

This produces the wrong sign for costly abatement.

If `B − ΔB` is a tighter carbon budget than `B`, then:

```text
Z(B − ΔB) > Z(B)
E(B − ΔB) < E(B)
```

Therefore:

```text
Numerator   = positive
Denominator = negative
λ̂           = negative
```

That contradicts the manuscript's reported positive MAC values, such as:

- 245 €/t
- 837 €/t
- 4,366 €/t

Those reported values are economically correct, but the written formula is not.

## Required fix

Replace the formula with:

```text
λ̂(B, ΔB) = [Z(B − ΔB) − Z(B)] / [E(B) − E(B − ΔB)]
```

This gives a positive MAC when tighter carbon budgets increase cost and reduce emissions.

## Cleaner version using reduction target notation

Because the paper uses reduction levels such as 0%, 5%, 10%, and 20%, the cleaner notation is:

```text
λ̂(r) = [Z(r) − Z(r − Δr)] / [E(r − Δr) − E(r)]
```

where:

```text
r      = carbon reduction target
Δr     = reduction step, e.g., 5 percentage points
Z(r)   = optimal logistics cost at reduction target r
E(r)   = optimal emissions at reduction target r
```

This version is easier for reviewers to understand because tighter budgets correspond to larger `r`.

## Replacement text for Section 3.2

Use the following paragraph:

```markdown
Let `Z(r)` denote the minimum logistics cost at carbon reduction target `r`, and let `E(r)` denote the resulting total network emissions. For a reduction-step size `Δr`, the finite-difference marginal abatement cost is:

λ̂(r) = [Z(r) − Z(r − Δr)] / [E(r − Δr) − E(r)]

This measures the incremental logistics cost required to move from the looser budget `r − Δr` to the tighter budget `r`. The numerator is the additional cost incurred by tightening the budget; the denominator is the additional emission reduction achieved. Thus, λ̂ is positive when abatement is costly, zero or undefined when the constraint is non-binding, and negative when the tighter assignment reduces both cost and emissions.
```

---

# Fatal Error 2 — Incorrect Citation in Finding 13

## Current problem

Finding 13 says the two “shift preferred” cells occur at carbon prices ≥100 €/t and states that this is:

```text
consistent with ETS 2 scenarios projected for 2030 [4]
```

This is wrong.

Reference `[4]` is:

```text
Q. Zhang, H. Li, MOEA/D: A multiobjective evolutionary algorithm based on decomposition,
IEEE Trans. Evol. Comput. 11 (2007) 712–731.
```

That has nothing to do with ETS 2 or projected carbon prices.

This is a high-risk citation error. A reviewer or editor can catch it immediately, and it will damage trust in the manuscript.

## Required fix

Either remove the ETS 2 statement or add a correct ETS 2 / carbon price scenario source.

## Safe option — remove the sentence

Replace:

```text
The two "shift preferred" cells occur in Frankfurt at reduced rail terminal cost (€500, −26% below baseline) and carbon prices ≥ 100 €/t, consistent with ETS 2 scenarios projected for 2030 [4].
```

with:

```text
The two "shift preferred" cells occur in Frankfurt at reduced rail terminal cost (€500, −26% below baseline) and carbon prices ≥ 100 €/t, indicating that infrastructure-cost reductions and substantially higher carbon prices are jointly required before physical mode shift becomes economically preferred in this archetype.
```

## Stronger option — add a proper ETS/carbon price reference

If you want to keep the ETS 2/carbon-price projection claim, add a real source and renumber references.

Possible wording:

```text
The two "shift preferred" cells occur in Frankfurt at reduced rail terminal cost (€500, −26% below baseline) and carbon prices ≥ 100 €/t. This indicates that mode shift becomes economically preferred only under a combined scenario of lower rail terminal costs and substantially higher carbon prices.
```

Do not mention ETS 2 unless the manuscript adds a verified source.

---

# Major Fix 3 — Algorithm 1 Step 2 Is Too Broad

## Current problem

Algorithm 1 currently says:

```text
Solve unconstrained cost MILP (B = ∞). Obtain Z₀, E₀.
If E₀ < target: classify as Regime 4 (co-benefit). Stop.
```

This is logically incomplete.

The unconstrained solution may satisfy a 20% carbon target but not a 50% target. Therefore the co-benefit check must be applied separately for each budget target.

## Required fix

Replace Step 2 with target-specific logic.

## Corrected Algorithm 1 skeleton

```markdown
1. Solve unconstrained cost MILP (`B = ∞`). Obtain `Z₀`, `E₀`.

2. For each carbon reduction target `r ∈ {0, 5, 10, …, 50}`:
   - Compute budget `B(r) = E_baseline × (1 − r/100)`.
   - If `E₀ ≤ B(r)`, classify target `r` as Regime 4 (co-benefit / non-binding) and set `Z(r)=Z₀`, `E(r)=E₀`.
   - Otherwise, solve the constrained MILP at `B(r)`.
   - If infeasible, classify target `r` as Regime 5.
   - Otherwise, record `Z(r)` and `E(r)`.

3. For adjacent feasible binding targets, compute:

   λ̂(r) = [Z(r) − Z(r − Δr)] / [E(r − Δr) − E(r)] × 1000 €/t

4. For each carbon price `π`, classify:
   - Regime 1 if `λ̂(r) < 0.90π`
   - Regime 2 if `0.90π ≤ λ̂(r) ≤ 1.10π`
   - Regime 3 if `λ̂(r) > 1.10π`
   - Regime 4 if unconstrained emissions already satisfy `B(r)`
   - Regime 5 if no feasible solution exists.
```

---

# Major Fix 4 — Variable Notation Ambiguity

## Current problem

The manuscript uses `p` for two different concepts:

1. budget reduction percentage, e.g., 20%;
2. carbon price, e.g., 65 €/t.

This is confusing and can create formula ambiguity.

## Required fix

Use separate notation:

```text
r  = carbon reduction target, e.g., 20%
π  = carbon price, e.g., 65 €/t CO₂e
B(r) = carbon budget at reduction target r
λ̂(r) = marginal abatement cost at reduction target r
```

## Replacement notation table

Add this to Section 3 or Section 4:

| Symbol | Meaning |
|---|---|
| `r` | Carbon reduction target (%) |
| `Δr` | Budget-step size, e.g., 5 percentage points |
| `π` | Carbon market price (€/t CO₂e) |
| `B(r)` | Carbon budget at reduction target `r` |
| `Z(r)` | Optimal logistics cost at target `r` |
| `E(r)` | Optimal emissions at target `r` |
| `λ̂(r)` | Finite-difference marginal abatement cost at target `r` |

---

# Minor Fixes Before Submission

## 1. Avoid saying “shadow-price-based” in title, abstract, and cover letter

The manuscript correctly explains that LP/MIP shadow prices are unreliable. Therefore, the paper should not be marketed as “shadow-price-based.”

Use:

```text
MAC-based carbon decision analytics
```

or:

```text
parametric marginal-abatement-cost-based carbon decision analytics
```

You may say:

```text
The framework is motivated by the economic interpretation of carbon shadow prices but operationalizes the signal through finite-difference marginal abatement cost because mixed-integer routing models do not provide reliable LP dual prices.
```

## 2. Ensure the abstract does not overclaim generality

Avoid:

```text
Domestic truck-rail mode shift is uneconomic.
```

Use:

```text
In rail-limited domestic truck-rail archetypes tested here, mode shift remains uneconomic at current EU ETS prices under the evaluated terminal-cost and emission-factor ranges.
```

## 3. Make generated-network robustness reproducible

The manuscript now reports 150 generated networks and 1,650 MILP solves. Ensure the repository contains:

```text
experiments/generated_network_robustness.py
experiments/parameter_sensitivity.py
experiments/budget_step_robustness.py
paper/figures/fig2_mac_curves.pdf
paper/figures/fig3_regime_heatmaps.pdf
```

If those files are not actually present, remove or revise the Data Availability claim.

## 4. Check table numbering

The manuscript currently has many added tables. Before submission, verify that table references are sequential and that every table is cited in the text before it appears.

Especially check:

- Table 6 — budget-step robustness
- Table 7 — parameter sensitivity
- Table 8 — claim strength
- Table 9 — generated-network robustness

---

# Corrected Core Contribution Statement

Use this exact contribution statement in the introduction or cover letter:

```text
This paper develops a parametric MAC-based carbon decision analytics framework for intermodal supply-chain routing. The framework estimates network-specific marginal abatement cost curves from sequential MILP solves and translates them into carbon compliance regimes: mode shift preferred, parity, allowance purchase preferred, co-benefit decarbonization, and infeasible target. The contribution is not a generic algorithmic advance in MILP or MOEA design, but a decision-analytic conversion of integer optimization outputs into actionable carbon-compliance choices.
```

---

# Submission Readiness After Fixes

## Current status

```text
SCA desk-reject risk: low to moderate
Reviewer rejection risk: moderate
Technical readiness: not ready until fatal errors are fixed
```

## Submit only after confirming

- [ ] MAC formula sign corrected in Section 3.2.
- [ ] MAC formula corrected in Algorithm 1.
- [ ] Incorrect ETS 2 citation `[4]` removed or replaced with a verified source.
- [ ] Algorithm 1 co-benefit check applied per target budget, not globally.
- [ ] `r` and `π` notation separated throughout the paper.
- [ ] “Shadow-price-based” wording removed from title, abstract, and cover letter.
- [ ] Data Availability matches files actually present in repository.
- [ ] Table and figure numbering checked.
- [ ] All broad claims bounded to archetype-level evidence.

---

## Final recommendation

The revised manuscript is now viable as an SCA decision-analytics submission **after technical cleanup**. The contribution is strongest when framed as:

```text
parametric MAC-based carbon compliance regime classification for intermodal supply-chain routing
```

not as:

```text
shadow-price-based optimization
```

Fix the formula and citation errors before submission. Those are not cosmetic issues; they directly affect analytical credibility.
