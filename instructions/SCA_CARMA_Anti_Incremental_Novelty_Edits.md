# Final Anti-Incremental-Novelty Revision Instructions for SCA

**Manuscript:** *Marginal Abatement Cost as a Carbon Decision Signal in Intermodal Supply Chain Routing: A Parametric MILP Framework for Mode Shift, Allowance Purchase, and Departure Timing*  
**Target journal:** *Supply Chain Analytics* (Elsevier)  
**Purpose:** Exact edits to reduce “incremental/integrated novelty” risk and strengthen the paper’s scientific advancement before submission.

---

## Executive Verdict

The manuscript is now strong, methods-journal-appropriate, and unusually clear about its own novelty boundaries. The repeated disclaimers that the paper is **not a new parametric MILP method** are correct and should be preserved.

The remaining risk is not that the paper is weak. The risk is that Reviewer 2 may classify the paper as an **integration of existing components**:

- parametric MILP / sequential solves,
- finite-difference MAC,
- carbon-price comparison,
- MILP/MOEA hybrid search,
- dynamic carbon-intensity scheduling.

To avoid this, the manuscript must make one thing unmistakable:

> The scientific advancement is not the integration itself. The advancement is the **supply-chain decision object** created by the integration: a network-specific MAC-based carbon compliance regime taxonomy for intermodal routing.

The final revision should therefore do three things:

1. Defuse the closest prior-art overlaps explicitly.
2. Convert the regime taxonomy into structural propositions.
3. Calibrate the shadow-price / duality claim so it is technically defensible.

---

# 1. Add a “Closest Prior Art and Differentiation” Paragraph

## Why this is necessary

The weakest novelty joints are:

1. **Lagouvardou 2022** — carbon-price turning point / routing decision under EU ETS.
2. **Mukherjee 2006** — discrete-step or average shadow-price logic in MILP.
3. **Vijay 2010** — ILP/MAC or emissions-constrained optimization with MAC-style interpretation.
4. **Feng 2025** — if verified, possible perturbation/MILP shadow-price method.

If these are absent or cited only indirectly, Reviewer 2 may say:

> The authors are rediscovering existing parametric IP / MAC / carbon-price threshold ideas.

The fix is to cite and distinguish them openly.

---

## Exact edit location

Add this paragraph near the end of **Section 2.5 Research Gap and Positioning**, immediately before Table 1.

---

## Exact text to add

```markdown
The closest prior work clarifies the boundary of the present contribution. Lagouvardou and Psaraftis [add ref.] analyze how EU ETS carbon prices can alter container-route and hub-choice decisions, demonstrating that carbon-price turning points can affect transport-network structure. Their analysis is policy- and route-choice oriented, whereas the present paper derives a network-specific MAC curve from an intermodal-routing MILP and converts it into a repeated operational regime classification. Mukherjee and Mukherjee [42] and related integer-programming shadow-price work establish that discrete optimization models require alternatives to naïve LP dual interpretation, including average or marginal-unit shadow-price concepts. The present paper does not claim to invent such sensitivity analysis; it adapts the finite-difference logic to carbon-constrained intermodal routing and uses the resulting MAC as a managerial compliance signal. Vijay et al. [add ref., verify] similarly motivate the connection between integer optimization and MAC-style abatement analysis, but do not develop a five-regime taxonomy for mode shift, allowance purchase, co-benefit decarbonization, and infeasible targets across intermodal network archetypes. Thus, the contribution is not a new parametric optimization method, but a supply-chain decision-analytics synthesis that turns network-specific MAC estimates into operational carbon-compliance guidance.
```

---

## Required caution

Do **not** cite Vijay 2010 or Feng 2025 unless the exact bibliographic details are verified:

- author names,
- title,
- journal/conference,
- year,
- DOI or stable URL,
- direct relevance to MAC / ILP / logistics / shadow pricing.

If verification is incomplete, use this safer wording instead:

```markdown
Related integer-programming and abatement-cost studies establish the components of this approach, but they do not develop the intermodal-routing compliance-regime taxonomy proposed here.
```

---

# 2. Recast Contribution 2 as Established-Method Adaptation

## Problem

Contribution 2 can still look methodological if the reader interprets finite-difference MAC estimation as the claimed novelty.

## Required fix

Contribution 2 must explicitly say:

- parametric integer programming is established;
- finite-difference estimation is not new in itself;
- the contribution is applying it to intermodal-routing carbon compliance and making it auditable/actionable.

---

## Exact edit location

Section 1.4, Contribution 2.

---

## Replace Contribution 2 with

```markdown
2. **Parametric MILP adaptation for finite-difference MAC estimation in integer supply-chain routing** (methodological adaptation). Parametric integer-programming and finite-difference sensitivity analysis are established operations-research tools. This paper adapts that logic to carbon-constrained intermodal mode assignment, where naïve solver-reported LP relaxation duals are unreliable as managerial shadow prices. The contribution is not a new parametric MILP method; it is the use of sequential MILP-derived MAC as a transparent, auditable, and solver-independent carbon-compliance signal for discrete logistics networks.
```

---

## Add immediately after the contribution list

```markdown
The contribution hierarchy is therefore intentional. The primary novelty is the MAC-based compliance regime taxonomy. The parametric MILP procedure is the estimation engine, and the Pareto-search experiment is a supporting decision-exploration component. The paper should be evaluated as a supply-chain decision-analytics contribution rather than as a new optimization algorithm.
```

---

# 3. Calibrate the “LP Duals Are Zero” Claim

## Problem

The current claim may be read as too strong:

> LP duals do not work for MIP.

A technically aggressive reviewer may respond:

> MIP sensitivity, perturbation methods, integer fixing, average shadow prices, and marginal-unit shadow prices exist.

The safe claim is narrower and more defensible:

> Naïve solver-reported LP-relaxation duals are unreliable and non-auditable for managerial MAC interpretation in integer mode-assignment models.

---

## Exact edit location

Section 1.2 and Section 3.2.

---

## Replace overly broad wording

### Avoid

```markdown
LP duals do not work for mixed-integer programmes.
```

### Use

```markdown
Naïve solver-reported LP-relaxation duals are not reliable managerial MAC estimates for mixed-integer mode-assignment models.
```

---

## Exact replacement paragraph for Section 3.2

```markdown
This approach does not rely on naïve solver-reported LP-relaxation duals. In mixed-integer mode-assignment models, such duals are not reliable managerial MAC estimates because the integer optimal-value function is non-smooth and changes only when discrete assignments change. More sophisticated integer-programming sensitivity concepts exist, including average shadow prices, marginal-unit shadow prices, and perturbation-based methods. However, these approaches are not routinely exposed as transparent, auditable outputs in standard logistics MILP workflows. The finite-difference MAC used here is therefore not presented as a new sensitivity-analysis theory, but as a practical, solver-independent estimator of the network’s incremental abatement cost across adjacent carbon-budget levels.
```

---

## Exact replacement for the CBC sentence

### Current risky version

```markdown
CBC reported LP shadow prices of 0.0 for all carbon budget constraints across all three tested networks. This confirms that parametric finite-difference MAC is the appropriate method for integer supply chain models and should replace LP dual reporting in practice.
```

### Replace with

```markdown
In the experiments, the CBC/PuLP workflow reported zero LP relaxation dual values for the carbon-budget constraints, even when tightening the budget forced costly mode shifts. This illustrates the practical risk of treating solver-reported relaxation duals as managerial MAC estimates in integer routing models. The finite-difference MAC provides a transparent alternative because it is computed directly from observed changes in optimal integer solutions.
```

---

# 4. Elevate the Regime Taxonomy into Structural Propositions

## Why this matters

A taxonomy alone may be seen as descriptive. A proposition turns it into a scientific result.

The propositions should link regime occurrence to network structure:

- modal availability,
- long-haul share,
- terminal-cost penalty,
- grid emission factor,
- modal abatement ceiling.

---

## Exact edit location

Add a new subsection after generated-network robustness or in the Discussion.

Recommended location:

```markdown
### 7.2 Structural Propositions from MAC Regime Evidence
```

Then renumber the current theoretical contribution section if needed.

---

## Add this opening paragraph

```markdown
The regime taxonomy becomes analytically useful when linked to structural properties of the logistics network. The three base archetypes and 150 generated networks suggest that regime occurrence is governed less by the carbon budget alone than by modal availability, relative modal cost, terminal-cost penalties, emission-factor differentials, and maximum feasible abatement capacity. The following propositions summarize the structural conditions observed in the experiments. They are not universal laws; they are empirically supported decision propositions that should be re-tested when the framework is applied to a new network.
```

---

## Add Proposition 1

```markdown
**Proposition 1 — Rail-limited domestic networks tend toward allowance preference when terminal-cost penalties dominate carbon-price levels.**  
In domestic truck–rail networks where rail availability is limited and terminal handling costs are high relative to distance-based rail savings, the internal MAC of physical mode shift tends to exceed current carbon-market benchmark prices. Under these conditions, allowance purchase is the economically preferred compliance instrument unless rail terminal costs fall materially, road costs rise sharply, or carbon prices increase substantially.
```

---

## Add Proposition 2

```markdown
**Proposition 2 — Maritime-accessible long-haul networks can enter co-benefit decarbonization when low-carbon modes are also cost-saving.**  
When long-haul maritime options are available and ship transport is both lower-cost and lower-emission than road transport, unconstrained cost minimization can already satisfy stringent carbon targets. In this structure, the carbon constraint is non-binding and the appropriate managerial conclusion is not forced abatement or allowance purchase, but recognition of co-benefit decarbonization.
```

---

## Add Proposition 3

```markdown
**Proposition 3 — Hub-limited networks are constrained by feasible abatement capacity before carbon-price comparison becomes decisive.**  
In hub-and-spoke networks with limited modal redundancy, constrained rail availability, or high rail emission factors, the maximum feasible emission reduction may be reached before the target budget is satisfied. Once all feasible lower-emission alternatives are exhausted, tighter carbon targets become infeasible and the appropriate response is network redesign, infrastructure change, or target relaxation rather than marginal compliance optimization.
```

---

## Add Proposition 4 if space allows

```markdown
**Proposition 4 — The same carbon price can imply different compliance decisions across network archetypes.**  
Because MAC is generated by discrete route-specific mode alternatives, a single carbon price does not have a uniform operational meaning across logistics networks. The same benchmark price may imply allowance purchase in rail-limited domestic networks, no action in co-benefit maritime networks, and infeasibility or redesign in hub-limited networks. This is the central reason that carbon-compliance decisions require network-specific MAC estimation rather than generic carbon-price thresholds.
```

---

# 5. Add a Structural-Proposition Summary Table

## Exact edit location

After the propositions.

---

## Add this table

```markdown
**Table X. Structural interpretation of MAC compliance regimes.**

| Structural condition | Expected regime | Managerial interpretation |
|---|---|---|
| Rail available but terminal-cost penalty exceeds distance-based savings | Allowance purchase preferred | Internal abatement is more expensive than market compliance |
| Long-haul maritime option is cheaper and cleaner than road | Co-benefit decarbonization | Cost minimization already reduces emissions |
| MAC lies within ±10% of carbon price | Parity zone | Strategic preference determines shift vs buy |
| Low-emission alternatives exist and MAC is below carbon price | Mode shift preferred | Physical abatement is cheaper than allowances |
| Modal alternatives exhausted before budget is met | Infeasible target | Network redesign or target relaxation required |
```

---

# 6. Add a “What Incumbent Methods Cannot Produce” Paragraph

## Why this matters

This directly addresses the “incremental novelty” objection.

Existing carbon-aware routing methods can produce:

- route assignments,
- emission totals,
- cost-emission Pareto fronts,
- modal shares.

Your framework produces:

- network-specific MAC,
- break-even carbon price,
- compliance regime label,
- infeasibility ceiling,
- co-benefit boundary.

---

## Exact edit location

End of Section 2.5, after the closest prior art paragraph.

---

## Add

```markdown
This distinction matters because incumbent carbon-aware routing methods can identify low-emission route assignments or Pareto fronts, but they do not directly answer the compliance question faced by a logistics manager: at this target and carbon price, should the firm shift modes, buy allowances, do nothing because the target is already met, or redesign the network because the target is infeasible? The proposed framework adds this missing decision layer by converting sequential MILP outputs into a MAC value, a break-even carbon price, and a regime label.
```

---

# 7. Add a “Scientific Advancement” Sentence in the Introduction

## Exact edit location

End of Section 1.4 Contributions.

---

## Add

```markdown
The scientific advancement is the regime-level interpretation of carbon-constrained routing outcomes: the paper moves from optimizing assignments under carbon constraints to explaining when different carbon-compliance regimes arise from network structure.
```

---

# 8. Tighten the Abstract to Avoid Integrated-Novelty Framing

## Problem

If the abstract says the paper “combines” too many components, it sounds integrated and incremental.

## Required abstract emphasis

The abstract should emphasize:

- decision problem,
- network-specific MAC,
- compliance regimes,
- structural conditions.

It should not emphasize:

- NSGA-III,
- dynamic carbon intensity,
- “hybrid” algorithm.

---

## Exact replacement for final abstract sentence

```markdown
The framework contributes a supply-chain decision-analytics method that converts parametric MILP-derived MAC curves into actionable carbon-compliance regimes and identifies the network structures under which physical mode shift, allowance purchase, co-benefit decarbonization, or network redesign is the rational response.
```

---

# 9. Strengthen the Generated-Network Study as Evidence, Not Sample

## Exact edit location

Start of Section 6.8.

---

## Replace or add

```markdown
The generated networks are not intended to estimate the real-world frequency of each regime. They are controlled structural robustness tests. Their purpose is to determine whether the five-regime taxonomy remains stable when the modal economics of each archetype are perturbed. The results therefore support structural interpretation rather than statistical population inference.
```

---

# 10. Add a Short Reviewer-2 Defense in Limitations

## Exact edit location

End of Section 7.3 Limitations.

---

## Add

```markdown
A possible concern is that the framework integrates established components: parametric MILP, finite-difference sensitivity analysis, carbon-price comparison, and intermodal routing. This is correct, but it is not the claimed scientific advancement. The claimed advancement is the compliance-regime interpretation produced by that integration. The framework transforms optimization outputs into a decision object that incumbent methods do not provide: a network-specific MAC, a break-even carbon price, a regime label, and an infeasibility ceiling.
```

---

# 11. Add a Decision-Output Comparison Table

## Why this helps

This table makes the advancement visible.

---

## Exact edit location

End of Section 2.5 or beginning of Discussion.

---

## Add

```markdown
**Table X. Decision outputs produced by prior routing models versus the proposed framework.**

| Output | Conventional carbon-aware routing | Bi-objective / Pareto routing | Proposed MAC-regime framework |
|---|---:|---:|---:|
| Optimal route or mode assignment | Yes | Yes | Yes |
| Cost and emission totals | Yes | Yes | Yes |
| Pareto trade-off front | No / limited | Yes | Supporting only |
| Network-specific MAC | No | No | Yes |
| Break-even carbon price | No | No | Yes |
| Mode-shift vs allowance-purchase rule | No | No | Yes |
| Co-benefit/non-binding regime identification | Usually implicit | Usually implicit | Explicit |
| Infeasible-target diagnosis | Solver status only | Solver status only | Explicit managerial regime |
```

---

# 12. Revise the Conclusion to State Advancement Clearly

## Current risk

Conclusion may still sound like “we converted curves into decisions,” which is good but can be stronger.

---

## Add this final sentence

```markdown
The resulting advancement is regime-level carbon decision analytics for intermodal logistics: instead of asking only which route assignment minimizes cost or emissions, the framework explains which carbon-compliance instrument is economically rational for a given network, target, and carbon price.
```

---

# 13. Final Anti-Incremental-Novelty Checklist

Before submission, confirm the manuscript does all of the following:

- [ ] States that parametric MILP is established, not new.
- [ ] States that finite-difference MAC is an adaptation, not a new sensitivity theory.
- [ ] Directly distinguishes Lagouvardou 2022.
- [ ] Directly distinguishes Mukherjee 2006.
- [ ] Adds Vijay 2010 only if verified.
- [ ] Adds Feng 2025 only if verified.
- [ ] Presents the five regimes as a taxonomy linked to network structure.
- [ ] Adds structural propositions from the 150 generated networks.
- [ ] States what prior routing methods cannot produce.
- [ ] Shows the new decision object: MAC + break-even price + regime label + infeasibility ceiling.
- [ ] Keeps NSGA-III as supporting only.
- [ ] Uses EU ETS as a benchmark price, not a universal legal-coverage claim.
- [ ] Uses bounded claims: archetype-level, not universal.
- [ ] Avoids “new method” language.
- [ ] Avoids “we integrate X, Y, Z” as the main novelty.
- [ ] Ends with the compliance-regime contribution, not algorithmic performance.

---

## Final Recommended Novelty Statement

Use this as the safest final novelty framing:

```markdown
The novelty of this paper is not parametric MILP, finite-difference sensitivity analysis, or carbon-price comparison in isolation. The novelty is the supply-chain decision-analytics synthesis: deriving a network-specific MAC curve from carbon-constrained intermodal-routing MILP and converting it into an operational compliance-regime taxonomy that identifies when mode shift, allowance purchase, co-benefit decarbonization, or network redesign is the rational response.
```

---

## Final Recommendation

Yes, there are additional edits beyond the current top three that can reduce incremental novelty risk. The most important is to make the scientific advancement visible as a **regime-level decision object**, not as an integration of tools.

The paper should be submitted only after adding:

1. a closest-prior-art differentiation paragraph,
2. structural propositions,
3. calibrated duality/shadow-price language,
4. a table showing what incumbent methods cannot produce,
5. a final conclusion sentence stating the regime-level advancement.

This will make the manuscript much harder for Reviewer 2 to dismiss as incremental integration.
