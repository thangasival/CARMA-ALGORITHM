# Top 3 Acceptance-Improving Fixes for the SCA Manuscript

**Manuscript:** *Marginal Abatement Cost as a Carbon Decision Signal in Intermodal Supply Chain Routing: A Parametric MILP Framework for Mode Shift, Allowance Purchase, and Departure Timing*  
**Target journal:** *Supply Chain Analytics* (Elsevier)  
**Purpose:** Convert the latest validation comments into exact manuscript revision guidance.

---

## Executive Verdict

The proposed “Top 3 fixes” are valid and high impact, but they must be framed carefully.

The most important adjustment is to avoid presenting parametric MILP / finite-difference MAC estimation as a new method. The stronger and safer novelty claim is:

> **The paper synthesizes established parametric integer-programming logic with intermodal routing and carbon-price comparison to create a supply-chain decision-analytics framework for carbon compliance regimes.**

This converts a likely Reviewer 2 objection into a strength. Instead of appearing unaware that parametric integer programming is established, the manuscript should explicitly ground itself in that literature and make clear that the novelty lies in **how the method is used for logistics carbon compliance decisions**.

---

# Fix 1 — Re-baseline the Novelty Claims

## Why this is highest impact

A skeptical reviewer may say:

> Parametric MILP and sequential solves are not new. This is established operations-research methodology.

That objection is valid unless the manuscript explicitly acknowledges prior parametric integer-programming theory.

The manuscript should therefore **not** claim that the methodological novelty is “parametric MILP.” Instead, it should claim that the paper uses parametric MILP as an established tool to construct **network-specific MAC curves** and convert those curves into **operational carbon-compliance regimes**.

---

## Required change to Contribution 2

### Current risk

If Contribution 2 sounds like this:

```markdown
We introduce finite-difference marginal abatement cost estimation for integer supply chain models.
```

it may be attacked as overstated.

### Safer revised Contribution 2

Use this wording:

```markdown
**Parametric MILP adaptation for finite-difference MAC estimation in intermodal routing** (methodological adaptation). Building on established parametric integer-programming logic, the paper applies sequential MILP solves to estimate finite-difference marginal abatement cost curves for carbon-constrained intermodal routing. The novelty is not parametric MILP itself, but its use as an auditable carbon-compliance signal in a discrete logistics network where LP relaxation duals are unreliable.
```

---

## Revised contribution hierarchy

The contribution hierarchy should be:

1. **C1 — Primary novelty:** MAC-based carbon compliance regime taxonomy for intermodal routing.
2. **C2 — Methodological adaptation:** parametric MILP / finite-difference MAC applied to discrete logistics mode assignment.
3. **C3 — Supporting implementation:** exact-model-conditioned Pareto search after regime classification.

Do not present the paper as an integrated novelty combining MILP + MAC + NSGA-III + dynamic carbon intensity. Present it as one central contribution:

> **MAC-based carbon compliance regime classification for intermodal supply-chain routing.**

---

## Citations to add or verify for Fix 1

Add citations that show parametric integer programming and value-function analysis are established.

### Must verify and cite

| Citation | Why it matters |
|---|---|
| Jenkins, L. (1982), parametric mixed-integer programming / RHS and objective variation | Establishes parametric MILP precedent |
| Jenkins, L. (1990), review of parametric integer programming | Shows the method family is mature |
| Blair and Jeroslow, integer/mixed-integer value functions | Supports non-smooth / discrete value-function argument |
| Kim and Cho (1988), shadow price in integer programming | Already relevant to MIP shadow-price limitations |
| Crema / Mukherjee and Mukherjee, average shadow price in MILP | Shows workaround exists but is not practical for this paper’s logistics use case |

### Important note

Use **Blair and Jeroslow** if that is the precise value-function reference. Do not cite “Blair” vaguely.

---

## Exact paragraph to add in Section 2 or Section 3.2

```markdown
The finite-difference procedure used here is not claimed as a new parametric optimization method. Parametric integer programming and value-function analysis are established in operations research. The methodological issue in this paper is different: carbon-constrained intermodal routing is a discrete mode-assignment problem, so the managerial marginal abatement signal cannot be recovered reliably from LP relaxation duals. The framework therefore adapts established parametric MILP logic to estimate the network-specific finite-difference MAC and uses that MAC as the decision variable for carbon compliance regime classification.
```

---

# Fix 2 — Convert the 150-Instance Robustness Study into Structural Propositions

## Why this matters

The generated-network robustness study should not look like “extra experiments.” It should become **structural supply-chain analytics evidence**.

The purpose of the 150 generated networks is not to estimate real-world frequency. It is to identify the modal/topological conditions under which each carbon-compliance regime arises.

---

## Add a proposition subsection

Add this after the generated-network robustness section, or inside the Discussion.

Recommended heading:

```markdown
### Structural Propositions from Generated-Network Robustness
```

---

## Proposition 1 — Rail-limited domestic networks

```markdown
**Proposition 1 — Rail-limited domestic networks tend toward allowance preference when terminal-cost penalties dominate carbon-price levels.**  
In domestic truck–rail networks where rail availability is limited by distance thresholds and terminal handling costs remain high, the internal MAC of physical mode shift tends to exceed current carbon-market benchmark prices. Under these conditions, allowance purchase is the economically preferred compliance instrument unless rail terminal costs fall materially or the carbon price rises substantially above current levels.
```

### Interpretation

This supports the Salamanca and rail-limited generated-network findings.

---

## Proposition 2 — Maritime-accessible long-haul networks

```markdown
**Proposition 2 — Maritime-accessible long-haul networks can enter a co-benefit regime when ship is both cheaper and cleaner than truck.**  
Where long-haul maritime options are available and ship transport has both lower cost and lower emission intensity than road transport, unconstrained cost minimization can already satisfy stringent carbon targets. In such cases, the carbon constraint is non-binding and the appropriate managerial conclusion is not forced mode shift or allowance purchase, but recognition of co-benefit decarbonization.
```

### Interpretation

This supports the Iberian and maritime-generated-network findings.

---

## Proposition 3 — Hub-limited networks

```markdown
**Proposition 3 — Hub-limited networks are constrained primarily by modal abatement capacity rather than carbon price.**  
In hub-and-spoke networks with limited modal redundancy, higher rail emission factors, or constrained rail availability, the binding limitation may be the maximum feasible abatement level rather than the market price of carbon. Once all feasible lower-emission modal alternatives are exhausted, tighter carbon targets become infeasible and the correct response is network redesign rather than marginal compliance optimization.
```

### Interpretation

This supports the Frankfurt and hub-limited generated-network findings.

---

## Paragraph to add before propositions

```markdown
The generated-network study is not intended to estimate population frequencies of carbon-compliance regimes. Instead, it is used as a controlled structural test of the regime taxonomy. By varying distance, modal availability, terminal costs, modal cost rates, and emission factors within each archetype family, the study identifies the modal-economic conditions under which the five regimes arise.
```

---

# Fix 3 — Add Missing Comparators and Positioning Paragraph in Section 2

## Why this matters

The literature review must show that the paper is aware of:

1. the intermodal freight decarbonization OR literature;
2. parametric integer-programming theory;
3. carbon-price / routing break-even studies;
4. logistics-sector MAC studies.

This prevents the paper from being dismissed as an integration of known tools without adequate positioning.

---

## Comparators to add

### 1. Martinez-Ferguson et al. 2026

Use for:

```markdown
intermodal freight decarbonization OR review
```

Purpose:

```markdown
Positions the paper inside the OR/intermodal transport decarbonization map.
```

Use cautiously:

```markdown
Recent reviews of intermodal freight decarbonization confirm that optimization models are widely used to study mode shift, but the literature remains focused on routing, modal assignment, and emissions outcomes rather than network-specific MAC-based compliance regime classification.
```

---

### 2. Lagouvardou and Psaraftis 2022

Use for:

```markdown
EU ETS / carbon-price-induced routing or hub-choice logic
```

Purpose:

```markdown
Supports the idea that carbon prices can change transport-network decisions and that break-even thresholds are corridor-specific.
```

---

### 3. Wu et al. 2025

Use for:

```markdown
broad logistics-sector MAC context
```

Important caution:

```markdown
Use Wu et al. only as evidence that logistics-sector MAC estimation is emerging. Do not present it as a direct methodological comparator unless it derives MAC from intermodal-routing MILP.
```

Suggested wording:

```markdown
Recent logistics-sector MAC studies estimate abatement costs at aggregate industry or regional levels, but they do not derive a route-network-specific MAC curve from an intermodal routing MILP or convert that curve into an operational allowance-purchase versus mode-shift decision rule.
```

---

### 4. Feng 2025

## Important warning

Do **not** cite Feng 2025 unless the exact title, journal, DOI, and relevance are verified.

Suggested note for manuscript preparation:

```markdown
Feng 2025 should be added only after bibliographic verification. If the paper is not directly about logistics MAC, parametric integer programming, carbon-price routing, or intermodal decarbonization, exclude it.
```

---

## One-sentence differentiator for Section 2.5

Use this exact sentence:

```markdown
To the best of our knowledge, this is the first intermodal-routing study to derive a network-specific MAC curve from parametric MILP and convert it into an operational carbon-compliance regime taxonomy covering mode shift, allowance purchase, co-benefit decarbonization, and infeasible targets.
```

If you want an even safer version:

```markdown
To the best of our knowledge, prior intermodal-routing studies have not derived network-specific MAC curves from parametric MILP and converted them into an operational carbon-compliance regime taxonomy covering mode shift, allowance purchase, co-benefit decarbonization, and infeasible targets.
```

Recommended version: **use the safer version.**

---

# Revised Top 3 Fixes — Final Version

Use this refined wording in your internal checklist:

```markdown
## Top 3 Fixes That Most Improve Acceptance Odds

1. **Re-baseline the novelty claims.**  
   Recast Contribution 2 as an application/adaptation of established parametric integer-programming theory, not as a new parametric MILP method. Add Jenkins, Blair and Jeroslow, and related value-function/parametric IP citations. Lead with Contribution 1 as the real novelty: synthesizing network-specific MAC curves into an operational carbon-compliance regime taxonomy.

2. **Convert the 150-instance robustness study into structural propositions.**  
   Use Appendix A to state when each regime arises under modal-availability and topology conditions. This turns robustness evidence from “extra experiments” into generalizable supply-chain analytics insight and strengthens the advancement beyond tool integration.

3. **Add missing comparators and a positioning paragraph in Section 2.**  
   Cite Martinez-Ferguson et al. 2026 for the OR/intermodal freight decarbonization map, Lagouvardou and Psaraftis 2022 for carbon-price-induced routing decisions, and Wu et al. 2025 only as broad logistics-MAC context. Add the differentiator: prior intermodal-routing studies have not derived network-specific MAC curves from parametric MILP and converted them into operational carbon-compliance regime taxonomy.
```

---

# Exact Manuscript Edits

## Edit A — Contribution framing

Add this after the contribution list:

```markdown
The paper is therefore not positioned as a new parametric MILP method. Parametric integer-programming analysis is established. The contribution is the supply-chain decision-analytics synthesis: using parametric MILP-derived MAC curves to classify operational carbon-compliance regimes in intermodal logistics.
```

---

## Edit B — Section 2 positioning paragraph

Add this at the end of Section 2.5:

```markdown
The literature therefore leaves a specific decision-analytics gap. Intermodal routing models show how carbon constraints or prices change routing outcomes, while MAC studies estimate abatement costs at sectoral or technology levels. What remains underdeveloped is the middle layer: deriving a network-specific MAC curve from an intermodal-routing MILP and using it to determine whether a logistics manager should shift modes, buy allowances, recognize co-benefit decarbonization, or redesign the network because the target is infeasible. This paper addresses that gap.
```

---

## Edit C — Appendix A proposition bridge

Add this before the generated-network table or in the Discussion:

```markdown
The generated-network robustness study is used to derive structural propositions rather than population frequencies. The results indicate that regime identity is governed primarily by modal availability, terminal-cost penalties, relative modal cost, emission-factor differences, and the maximum feasible abatement ceiling.
```

---

## Edit D — Reviewer 2 defense sentence

Add this in Limitations:

```markdown
The numerical MAC thresholds reported in this study should not be transferred directly to other logistics networks. The generalizable contribution is the decision procedure and regime taxonomy; the numerical regime boundaries must be recomputed for each network using its own modal alternatives, costs, emissions, and relevant carbon price.
```

---

# Final Recommendation

These three fixes are valid and should be implemented.

The only caution is citation verification. Do not add “Feng 2025” unless it is confirmed and directly relevant. The safe acceptance-oriented framing is:

> **Established method, new decision-analytics synthesis.**

That is the cleanest way to satisfy Reviewer 2 while preserving the manuscript’s novelty.
