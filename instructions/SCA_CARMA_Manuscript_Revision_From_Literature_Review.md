# Manuscript Revision Plan: Integrating the Literature Review Memo into the SCA Submission

**Target manuscript:** *Marginal Abatement Cost as a Carbon Decision Signal in Intermodal Supply Chain Routing: A Parametric MILP Framework for Mode Shift, Allowance Purchase, and Departure Timing*  
**Target journal:** *Supply Chain Analytics* (Elsevier)  
**Purpose:** Convert the literature-review memo into concrete manuscript revisions that strengthen novelty grounding, contribution framing, and reviewer defensibility.

---

## 1. Executive Recommendation

The manuscript is now correctly framed around **parametric marginal abatement cost (MAC) decision analytics**, not generic carbon-aware routing and not DCCT/MOEA algorithm novelty.

The literature-review memo is useful, but it should **not** be pasted directly into the manuscript. It should be converted into a cleaner scholarly Section 2 revision and a tighter contribution-positioning argument.

The strongest revised contribution should remain:

> This paper develops a parametric MAC-based carbon decision analytics framework for intermodal supply-chain routing. The framework estimates network-specific marginal abatement cost curves from sequential MILP solves and translates them into carbon compliance regimes: mode shift preferred, parity, allowance purchase preferred, co-benefit decarbonization, and infeasible target.

The manuscript should position itself as filling the missing bridge between three literatures:

1. **Carbon-constrained intermodal routing optimization** — rich literature, but mostly reports optimal assignments and Pareto fronts.
2. **MAC curve methodology** — mature in energy, industry, and policy, but underdeveloped in freight routing.
3. **Integer-programming duality / shadow price limitations** — shows why LP duals are unreliable for MIP and why finite-difference MAC is necessary.

---

## 2. Immediate Fix Before Revising Section 2

The literature memo contains one conceptually reversed sentence.

### Problematic sentence

> producing a network-specific and budget-specific break-even carbon price below which mode shift is preferred and above which allowance purchase is preferred.

### Corrected sentence

> producing a network-specific and budget-specific break-even carbon price **above which physical mode shift is preferred and below which allowance purchase is preferred**.

### Reason

If the carbon market price `π` is greater than the internal MAC, then physical abatement is cheaper than buying allowances. If `π` is below MAC, buying allowances is cheaper.

Use this corrected logic consistently throughout the revised manuscript.

---

## 3. What to Add to the Manuscript

Do **not** add every citation from the memo. Add only the papers that directly strengthen the SCA contribution.

### Priority citations to integrate

| Priority | Citation | Why it matters | Where to add |
|---:|---|---|---|
| 1 | Hoen et al. (2014), *Transportation Science* | Closest conceptual ancestor: mode switching to meet voluntary carbon targets; emissions-profit frontier but no MAC decision rule | Section 2.1 or 2.2 |
| 2 | Martinez-Ferguson et al. (2026) | Current intermodal freight decarbonization OR review; supports field-level gap | Section 2.1 |
| 3 | Ricci et al. (2025) | Transport-sector abatement-cost review; supports claim that freight MAC remains underdeveloped | Section 2.2 |
| 4 | Guo et al. (2025/2026), *Management Science* | Modern support for discrete-market / integer-duality limitations | Section 2.3 or Section 3.2 |
| 5 | Lagouvardou and Psaraftis (2022) | EU ETS routing-choice / carbon leakage case; supports break-even carbon-price logic | Section 2.4 |
| 6 | Longva et al. (2024) | Shipping MAC curves; supports maritime MAC context | Section 2.4 or co-benefit discussion |
| 7 | Martin et al. (2023) | High transport abatement costs; helps justify why MAC can exceed ETS by large multiples | Section 2.4 |
| 8 | Rotaris et al. (2022) or Dong et al. (2020) | Co-benefit / cheaper-and-greener freight mode examples | Section 2.5 or Regime 4 discussion |
| 9 | Aucamp and Steinberg (1982) | LP degeneracy and shadow-price unreliability; optional but useful | Section 3.2 |
| 10 | Sen et al. (2008) | Shadow prices with indivisibilities; optional but useful | Section 3.2 |

---

## 4. Recommended Revised Section 2 Structure

Replace the current literature review with a more explicit four-part structure.

```markdown
## 2. Literature Review and Positioning

### 2.1 Carbon-Constrained Intermodal Routing and Modal-Shift Optimization
Purpose: Show that carbon-aware routing is mature, but existing studies stop at optimal assignment, Pareto fronts, or modal shares.

### 2.2 Marginal Abatement Cost Curves and the Freight Gap
Purpose: Show that MAC curves are mature in climate/energy policy but underused in freight-routing decision analytics.

### 2.3 Integer Programming, Shadow Prices, and the Need for Finite-Difference MAC
Purpose: Justify why LP duals are not enough for discrete mode-assignment models.

### 2.4 Carbon Prices, Allowance Purchase, and Break-Even Mode-Shift Decisions
Purpose: Connect MAC to EU ETS and explain why the paper compares internal abatement cost with external allowance price.

### 2.5 Co-Benefit Decarbonization and Boundary Regimes
Purpose: Ground Regime 4 with prior evidence showing cost-saving emission reductions in freight contexts.

### 2.6 Positioning and Research Gap
Purpose: State exactly what prior work does not do and what this paper contributes.
```

---

## 5. Draft Replacement Prose for Section 2

The following text can be inserted into the manuscript after trimming for length.

### 2.1 Carbon-Constrained Intermodal Routing and Modal-Shift Optimization

```markdown
Carbon-constrained freight routing has developed into a substantial stream of supply-chain optimization research. Early intermodal models established the cost–emissions trade-off in freight network design and showed that modal shift can reduce emissions without necessarily imposing proportional cost penalties. Subsequent studies introduced carbon taxes, emission caps, cap-and-trade mechanisms, and multi-objective formulations into intermodal routing and service-network design. These models typically use MILP, robust optimization, fuzzy programming, or evolutionary algorithms to identify lower-emission assignments across truck, rail, inland waterway, and maritime modes.

The limitation of this literature is not absence of optimization. The limitation is interpretability of the carbon constraint. Most studies report optimal assignments, emissions, cost changes, or Pareto fronts, but they do not extract the marginal cost of the imposed carbon constraint and translate it into a compliance decision rule. For example, Bouchery et al. show that a carbon-optimal level of modal shift exists and that maximizing modal shift is not necessarily cost- or carbon-optimal, but they do not derive the MAC curve that identifies the marginal cost of each additional shift. Hoen et al. construct an emissions–profit frontier for voluntary carbon targets through mode switching, but the frontier is not converted into a network-specific break-even carbon price or allowance-purchase rule. Demir et al. and related bi-objective intermodal studies similarly reveal cost–emission trade-offs but stop short of estimating the endogenous marginal abatement cost of the logistics network.
```

### 2.2 Marginal Abatement Cost Curves and the Freight Gap

```markdown
Marginal abatement cost (MAC) curves are widely used in climate-policy and energy-system analysis to rank abatement options by their cost per unit of CO₂e reduction. Their core decision logic is simple: when the internal MAC of an abatement option is below the prevailing carbon price, physical abatement is economically preferred; when MAC exceeds the carbon price, market-based compliance is cheaper. Kesicki and Strachan caution that MAC curves must be used carefully because they are sensitive to baselines, option interactions, uncertainty, and non-financial implementation barriers. Huang et al. similarly emphasize that bottom-up engineering MAC curves are most appropriate when the decision-maker is evaluating concrete technological or operational options.

Despite their importance in climate policy, MAC curves remain underdeveloped in freight-routing analytics. Recent transport-sector reviews indicate that freight-specific abatement-cost applications are much less developed than passenger-transport and energy-sector applications. Existing freight studies often treat carbon price as an exogenous scenario parameter, but do not compute the network's endogenous break-even carbon price from the routing model itself. This paper addresses that missing direction: rather than asking how a given carbon price changes routing, it asks what internal MAC the logistics network generates at each carbon budget level, and then compares that MAC to the external carbon price.
```

### 2.3 Integer Programming, Shadow Prices, and Finite-Difference MAC

```markdown
A natural way to estimate the marginal cost of a carbon constraint would be to use the shadow price of the emission-budget constraint. This approach is valid in continuous linear programming, where the dual variable of a binding constraint measures the local change in the optimal objective value caused by relaxing the constraint. However, intermodal routing is a discrete mode-assignment problem, and mixed-integer programs do not provide reliable marginal shadow prices in the same sense. The integer optimal-value function is non-convex and piecewise constant; LP-relaxation duals can be zero, undefined, or misleading at the integer optimum. Classical work on shadow prices in integer programming and average shadow prices confirms this limitation, and recent work on discrete-market duality reinforces that conventional strong-duality logic does not transfer cleanly to indivisible decisions.

For this reason, the present paper does not use LP duals as the operational signal. Instead, it estimates MAC by finite differences from sequential MILP solves. At each carbon reduction target, the MILP is solved exactly; the additional cost and additional emission reduction between adjacent targets produce the finite-difference MAC. This method is consistent with step-wise MAC construction in bottom-up engineering models and avoids relying on solver-reported LP relaxation duals. In the experiments, CBC reports zero LP shadow prices for all carbon-budget constraints, while the finite-difference MAC correctly identifies positive mode-shift thresholds, co-benefit regions, and infeasibility boundaries.
```

### 2.4 Carbon Prices, Allowance Purchase, and Break-Even Mode-Shift Decisions

```markdown
The comparison between internal abatement cost and external carbon price is well established in carbon-market analysis but rarely operationalized at the logistics-network level. EU ETS and related carbon-price mechanisms create an observable market cost of compliance. A logistics manager facing a carbon target therefore has two broad options: physically reduce emissions through mode shifts, or purchase allowances when internal abatement is more expensive than market compliance. The relevant managerial threshold is the network-specific break-even carbon price: above this price, physical abatement is preferred; below it, allowance purchase is preferred.

Recent transport and maritime ETS studies show that these break-even thresholds are highly mode- and corridor-specific. Some shipping or container-route decisions change only at carbon prices far above current allowance levels, while other network decisions flip at lower prices depending on route structure and modal availability. This supports the central premise of the present paper: carbon compliance cannot be determined from a generic carbon price alone. The network's own MAC curve must be estimated first.
```

### 2.5 Co-Benefit Decarbonization and Boundary Regimes

```markdown
A further limitation of simple carbon-price reasoning is that some logistics networks exhibit co-benefit decarbonization: lower-emission modes are already cost-competitive, so cost minimization alone reduces emissions without any carbon constraint or allowance price. Prior freight studies document such win–win outcomes in specific modal-shift contexts, including waterway, maritime, and combined-transport settings. These cases correspond to negative or undefined MAC: the carbon constraint is non-binding because the unconstrained cost-optimal solution already satisfies the emission target.

The present paper formalizes this case as a boundary regime rather than treating it as a failed MAC calculation. If the unconstrained MILP already satisfies a target budget, the correct managerial recommendation is not to force additional mode shifts or purchase allowances, but to recognize that the market structure already delivers the desired decarbonization level. Conversely, when all feasible modal alternatives are exhausted and the MILP becomes infeasible, the framework identifies a hard abatement ceiling, indicating that the target requires network redesign rather than marginal compliance decisions.
```

### 2.6 Positioning and Research Gap

```markdown
The preceding literature shows that the building blocks of this paper exist separately. Intermodal routing models optimize cost and emissions but rarely convert the carbon constraint into a managerial compliance signal. MAC curves compare abatement options to carbon prices, but are mainly used in energy, industry, and aggregate transport-policy analysis rather than network-specific freight routing. Integer-programming theory explains why conventional shadow prices are unreliable for discrete mode-assignment problems, but this insight is not operationalized in sustainable logistics decision support.

This paper contributes by combining these threads into a parametric MAC-based carbon decision analytics framework for intermodal supply-chain routing. The framework estimates the network-specific MAC curve from sequential MILP solves and converts that curve into five carbon compliance regimes: mode shift preferred, parity, allowance purchase preferred, co-benefit decarbonization, and infeasible target. The contribution is therefore not another carbon-aware routing algorithm; it is a decision-analytic method for interpreting the marginal cost of carbon constraints in discrete logistics networks.
```

---

## 6. Required Updates to Existing Manuscript Sections

### Abstract

Keep the current abstract, but add one sentence that makes the literature gap clearer:

```markdown
While prior intermodal routing studies report optimal assignments or Pareto fronts under carbon constraints, they rarely estimate the network-specific marginal abatement cost curve needed to decide whether physical mode shift is cheaper than carbon-market compliance.
```

Place this after the first or second sentence.

---

### Introduction, Section 1.2

Add one bridge sentence after explaining why LP duals are unreliable:

```markdown
This distinction matters because a solver-reported dual value and a decision-useful MAC are not the same object in a mixed-integer routing model; the former is a relaxation artifact, while the latter must be inferred from changes in optimal integer solutions across budget levels.
```

---

### Contributions, Section 1.4

Add the following clarification:

```markdown
The paper is shadow-price-motivated but not shadow-price-dependent: it begins from the economic interpretation of a carbon shadow price, then replaces unreliable MIP duals with finite-difference MAC estimated from parametric MILP solutions.
```

This prevents reviewers from saying: “You criticize shadow prices but still call the paper shadow-price based.”

---

### Section 3.2

Ensure the formula remains the corrected version:

```markdown
λ̂(r) = [Z(r) − Z(r − Δr)] / [E(r − Δr) − E(r)]
```

Do not revert to the earlier sign-error version.

---

### Section 3.3

Clarify the break-even logic:

```markdown
For a given target `r`, the finite-difference MAC λ̂(r) is the break-even carbon price. If the market carbon price π exceeds λ̂(r), physical mode shift is cheaper than purchasing allowances. If π is below λ̂(r), allowance purchase is cheaper than forcing internal abatement.
```

---

### Section 6.7 / Finding 13

Keep the safer version without unsupported ETS 2 claims:

```markdown
The two "shift preferred" cells occur in Frankfurt at reduced rail terminal cost (€500, −26% below baseline) and carbon prices ≥100 €/t, indicating that infrastructure-cost reductions and substantially higher carbon prices are jointly required before physical mode shift becomes economically preferred in this archetype.
```

---

### Table 8

Replace:

```markdown
Allowance purchase preferred holds at ETS 2 carbon prices (100–150 €/t)
```

with:

```markdown
Allowance-purchase preference may weaken under higher carbon-price scenarios (100–150 €/t)
```

Allowed wording:

```markdown
Conditional: regime can shift at 100–150 €/t when rail infrastructure costs are reduced.
```

---

## 7. Citation-Gap Table to Add Internally During Revision

Use this working table to decide where each new paper belongs.

| Manuscript claim | Add citation support |
|---|---|
| Carbon-aware intermodal routing is mature but assignment-focused | Bouchery et al.; Demir et al.; Hoen et al.; Martinez-Ferguson et al. |
| Prior routing papers do not derive a network-specific MAC decision rule | Hoen et al.; Bouchery et al.; Ricci et al.; Martinez-Ferguson et al. |
| MAC curves are established but require caution | Kesicki & Strachan; Huang et al.; Vogt-Schilb et al. |
| Bottom-up discrete models produce step-wise MAC curves | Kiuila & Rutherford; Misconel et al. |
| MIP shadow prices are unreliable for discrete mode assignment | Williams; Kim & Cho; Crema; Mukherjee & Mukherjee; Guo et al.; Sen et al. |
| Carbon price vs internal abatement cost is the correct decision comparison | Kesicki & Strachan; Lagouvardou & Psaraftis; Flodén et al.; Martin et al. |
| Co-benefit decarbonization exists in freight contexts | Liu et al.; Rotaris et al.; Dong et al. |
| High MAC values in freight are plausible | Martin et al.; Flodén et al.; Boehm et al. |

---

## 8. References to Add or Verify

Add these only if they are correctly verified with DOI, journal, volume, and pages.

### Must add

1. Hoen, K.M.R., Tan, T., Fransoo, J.C., van Houtum, G.J. (2014). Switching transport modes to meet voluntary carbon emission targets. *Transportation Science*, 48(4), 592–608. https://doi.org/10.1287/trsc.2013.0481

2. Ricci, L., Traverso, A., Troncia, M. (2025). Transport sector GHG mitigation measures: abatement costs application review. *Future Transportation*.  
   **Action:** verify final article number, volume, and DOI before adding.

3. Martinez-Ferguson, M. et al. (2026). Decarbonizing freight through intermodal transport: an operations research perspective — Part I. *Future Transportation*.  
   **Action:** verify final article number, volume, and DOI before adding.

4. Guo, C. et al. (2025/2026). Copositive duality for discrete energy markets. *Management Science*.  
   **Action:** verify volume, issue, pages, and DOI before adding.

### Strongly recommended

5. Lagouvardou, S., Psaraftis, H.N. (2022). Implications of the EU emissions trading system on European container routes: a carbon leakage case study. *Maritime Transport Research*.  
   **Action:** verify DOI.

6. Longva, T. et al. (2024). Marginal abatement cost curves for CO₂ emission reduction from shipping to 2050. *Maritime Transport Research*.  
   **Action:** verify DOI.

7. Martin, J. et al. (2023). Carbon abatement costs for renewable fuels in hard-to-abate transport sectors. *Advances in Applied Energy*.  
   **Action:** verify DOI.

8. Rotaris, L. et al. (2022). Combined transport: cheaper and greener — a successful Italian case study. *Research in Transportation Business & Management*.  
   **Action:** verify DOI.

### Optional

9. Aucamp, D., Steinberg, D. (1982). The computation of shadow prices in linear programming. *Journal of the Operational Research Society*.  
   **Use only if expanding the LP-duality discussion.**

10. Sen, S. et al. (2008). Start-up prices and shadow prices for resource allocation models with indivisibilities.  
   **Use only if expanding the indivisibility/duality discussion.**

---

## 9. Language to Avoid

Do not use these phrases in the manuscript:

```markdown
the bridge is essentially empty
Consensus returned
per the skill's rules
Start Here
Search terms
Boolean strings
must cite verbatim
```

These are research-process notes, not manuscript prose.

Also avoid overly categorical claims such as:

```markdown
No prior work has ever done this.
Carbon pricing is ineffective for domestic logistics.
Maritime routes always produce co-benefit decarbonization.
```

Use bounded language:

```markdown
To the best of our knowledge, prior intermodal routing studies have not converted parametric MILP-derived MAC curves into a carbon compliance regime taxonomy.
```

```markdown
In the rail-limited domestic archetypes tested here, mode shift remains uneconomic at current EU ETS prices under the evaluated terminal-cost and emission-factor ranges.
```

```markdown
Maritime-accessible routes may exhibit co-benefit decarbonization when ship is both cheaper and cleaner than truck.
```

---

## 10. Final Manuscript Revision Checklist

Before resubmission, complete the following:

- [ ] Add Hoen et al. (2014) and distinguish your MAC curve from their emissions–profit frontier.
- [ ] Add Ricci et al. (2025) and Martinez-Ferguson et al. (2026) to support the freight-MAC/intermodal-OR gap.
- [ ] Add Guo et al. or another strong discrete-duality citation to reinforce why LP shadow prices are unreliable in MIP.
- [ ] Add at least one EU ETS / shipping / break-even carbon-price paper, such as Lagouvardou and Psaraftis or Flodén et al.
- [ ] Add at least one co-benefit freight paper, such as Liu, Rotaris, or Dong.
- [ ] Correct the break-even logic: mode shift preferred when carbon price exceeds MAC; allowance purchase preferred when carbon price is below MAC.
- [ ] Keep the corrected finite-difference MAC formula.
- [ ] Remove unsupported ETS 2 claims unless a verified source is added.
- [ ] Replace all leftover `p` notation with `r` for reduction target and `π` for carbon price.
- [ ] Ensure all new references are validated with DOI, article number, and page range before submission.
- [ ] Keep algorithm engineering as a supporting contribution only.

---

## 11. Final Recommendation

The literature memo should be used to revise the manuscript, especially Section 2 and the contribution-positioning paragraphs. The highest-value improvement is not adding more citations mechanically, but showing that:

1. Prior freight-routing papers optimize emissions but do not compute MAC decision regimes.
2. MAC curves exist but are rarely applied to network-specific freight-routing decisions.
3. MIP duals are unreliable, so finite-difference MAC is methodologically justified.
4. Comparing MAC to carbon price yields the practical decision rule: mode shift, allowance purchase, co-benefit, or infeasible target.

This revision will make the SCA contribution much harder to dismiss as incremental algorithm engineering.
