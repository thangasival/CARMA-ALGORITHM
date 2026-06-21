# CARMA v3 — Consolidated Redline for Fully Defensible Framing

**Manuscript:** `CARMA_manuscript_v3.md` (Marginal Abatement Cost as a Carbon Decision Signal in Intermodal Supply Chain Routing)
**Target:** Supply Chain Analytics (Elsevier)
**Purpose of this redline:** Close the remaining novelty-defense gaps in one pass so the four contribution claims (decision rule, taxonomy, managerial implication, and the synthesis "insight") survive a hard reviewer holding the closest prior art in hand.

---

## Orientation: what is already done vs. what this redline adds

A prior revision already applied the first round of edits. The following are **already present in v3** and require no change:

- §1.4 leads with the regime taxonomy and the counter-orthodox "4–67× ETS" finding (line 65), with the contribution hierarchy framed as synthesizing novelty that rises above integration (line 75).
- Glenk et al. is already cited as **[46]** and walled off in §1.4 (line 75) and §2.2 (lines 105, 109).
- Misconel **[35]** is already positioned as the step-MAC mechanism precedent (lines 107, 109).
- The abstract and Highlights are already hedged ("Experiments across three archetypes show…", "can improve") and do **not** overuse "validated."

**What remains undone — and what this redline supplies — is the entire second tier of prior art surfaced by the independent re-run.** Four specific exposures, each puncturable by a single uncited paper:

1. **Noguchi (2025), *Networks and Spatial Economics*** — formalizes carbon-price *regime thresholds on multimodal networks* plus the emissions-as-shadow-price envelope identity. This is the single most dangerous omission: it pre-figures the *conceptual* core of the taxonomy. **Make-or-break citation.**
2. **Rekker et al. (2023), *Energy Economics*** — firm-level MILP/DDF-derived MAC ≫ carbon price ⇒ buy allowances. This is the manuscript's "allowance-preferred regime" result, in chemicals. Shows the *decision rule* is not new in kind.
3. **Lagouvardou et al. (2022), *Maritime Transport Research*** — per-network carbon-price *turning point* rendering a routing reconfiguration cost-effective. The break-even-price-for-a-network logic, in maritime.
4. **Threshold lineage — Zakeri (2015), Chen (2016), Majumdar (2023)** — "inflection points" / "mode-shift thresholds" / sub-threshold carbon procurement under carbon pricing. Establishes that the *threshold-regime idea* is long-standing, so the §2.5 gap claim cannot stand unqualified.

Plus one wording fix: §1.4 contribution 1 still says the archetypes "empirically validate" the framework — soften to "illustrate / instantiate" to survive the external-validity objection (Heinold & Meisel show real intermodal emission rates vary strongly by corridor).

New references are numbered **[47]–[50]**, continuing from the current last entry **[46]**.

---

## EDIT 1 — §1.4, contribution 1: soften "empirically validate" (line 69)

**Rationale:** Three synthetic archetypes do not constitute empirical validation against the real-network emission-rate variation documented by Heinold & Meisel [48]. "Validated" is the exact word a hard reviewer attacks. Reframe as illustration/instantiation and bound generalizability.

**FIND (delete):**

> 1. **A network-structure-conditioned carbon-compliance regime taxonomy for intermodal routing** (primary). The framework converts parametric MILP-derived MAC into five operational regimes and, across three network archetypes, maps the regime boundaries over budget levels and carbon-price scenarios and characterizes the structural conditions — modal availability, long-haul share, abatement ceiling — that determine which regime a network occupies. The managerial payload is the counter-orthodox finding that physical mode shift is the rational response only for a structurally identifiable subset of networks; for others, allowance purchase, co-benefit recognition, or network redesign dominates.

**REPLACE WITH (insert):**

> 1. **A network-structure-conditioned carbon-compliance regime taxonomy for intermodal routing** (primary). The framework converts parametric MILP-derived MAC into five operational regimes and, on three network archetypes used as structured illustrations rather than empirical validation cases, maps the regime boundaries over budget levels and carbon-price scenarios and characterizes the structural conditions — modal availability, long-haul share, abatement ceiling — that determine which regime a network occupies. Because realized emission rates and abatement costs vary strongly across corridors and countries [48], the archetype results are presented as existence-and-mechanism demonstrations whose external magnitudes require corridor-specific calibration; the transferable claim is the regime structure, not the specific MAC values. The managerial payload is the counter-orthodox finding that physical mode shift is the rational response only for a structurally identifiable subset of networks; for others, allowance purchase, co-benefit recognition, or network redesign dominates.

---

## EDIT 2 — §1.4, closing positioning paragraph: add the threshold-concept wall (after line 75)

**Rationale:** The current line 75 walls off only the *MAC-construction* twins (Glenk, Misconel). It does not address the *regime-threshold concept*, which Noguchi formalizes for multimodal networks and which Zakeri/Chen pre-figure. Without this, "an empirical regime taxonomy that unifies compliance outcomes which prior work treats in isolation" overclaims conceptual novelty. Insert a new paragraph immediately **after** the paragraph ending "…not as a new optimization method." (line 75) and **before** "The paper is therefore not positioned as a new parametric MILP method…" (line 77).

**INSERT (new paragraph):**

> The taxonomy's conceptual base — that a carbon price partitions a transport network into discontinuous decision regimes — is not itself new, and the paper does not claim it to be. Zakeri et al. [49] identify inflection points at which carbon pricing and trading schemes shift the cost–emission response of a supply chain, and Chen et al. [50] derive explicit mode-shifting thresholds under alternative carbon-emission-reduction policies. Most directly, Noguchi [47] proves, for carbon-priced modal split on capacity-constrained multimodal networks, that the steady optimal modal mix changes discontinuously across a finite set of carbon-price thresholds, and that the marginal value of the carbon weight equals steady-state emissions — the shadow-price identity that motivates a MAC reading. That work is, however, purely theoretical and demonstrated on a synthetic network: it establishes the *existence* of regime thresholds but does not construct the network's MAC curve, compare it to an observable allowance market, or instantiate empirical archetypes. The contribution here is therefore not the discovery of regime thresholds but their *operationalization* for intermodal routing: deriving the MAC curve that locates the thresholds, naming the five resulting regimes, and tying each to identifiable network structure so that a practitioner can classify a given network rather than prove that a classification exists.

---

## EDIT 3 — §2.2, extend the MAC-twin wall to include Rekker (line 109)

**Rationale:** Line 109 currently walls off Misconel and Glenk. Rekker et al. is a closer empirical twin to the headline result — firm-level MAC well above the carbon price, so firms prefer allowances — and is uncited. Append to the existing paragraph at line 109 (after "…rather than a single abatement-level recommendation.").

**FIND (end of line 109 paragraph):**

> …The present contribution is the transposition of this MAC-versus-market decision logic to the intermodal routing layer, where the break-even carbon price emerges endogenously from the network's discrete modal alternatives and partitions (network, budget) points into distinct compliance regimes rather than a single abatement-level recommendation.

**REPLACE WITH (append one sentence pair):**

> …The present contribution is the transposition of this MAC-versus-market decision logic to the intermodal routing layer, where the break-even carbon price emerges endogenously from the network's discrete modal alternatives and partitions (network, budget) points into distinct compliance regimes rather than a single abatement-level recommendation. The same MAC-versus-price logic, and the same qualitative conclusion that underpins the allowance-preferred regime, has been established empirically at the firm level: Rekker et al. [51] estimate a median marginal abatement cost of 429 €/t for European chemical producers — far above prevailing carbon prices — and conclude that most firms therefore prefer to purchase allowances rather than abate internally. The domestic truck-rail result reported here (MAC 245–4,366 €/t, 4–67× the 2024 ETS price) is the routing-network analogue of that firm-level finding; the novelty is not the abate-versus-buy rule but its derivation from intermodal modal topology and its embedding in a multi-regime classification.

*(Reference numbering note: this inserts Rekker as **[51]**. If you prefer Rekker to sit numerically with the other second-pass additions, renumber so that Noguchi/Zakeri/Chen/Heinold/Rekker occupy [47]–[51] in citation order; see the consolidated reference block below, which lists them in the order they are first cited.)*

---

## EDIT 4 — §2.2, §2.5: add Lagouvardou as the network-reconfiguration break-even precedent

**Rationale:** Lagouvardou et al. compute a per-network carbon-price turning point for a routing reconfiguration — the closest "break-even carbon price for a network decision" in the literature — and is uncited. Best placed in the §2.2 break-even paragraph (line 111), alongside Flodén [43] and Boehm [44].

**FIND (within line 111, the sentence on Flodén):**

> Flodén et al. [43] analyze EU ETS shipping inclusion and find that modal shift away from RoRo shipping emerges only at allowance prices above 90–150 €/t, illustrating that the break-even carbon price is transport-mode and corridor specific.

**REPLACE WITH:**

> Flodén et al. [43] analyze EU ETS shipping inclusion and find that modal shift away from RoRo shipping emerges only at allowance prices above 90–150 €/t, illustrating that the break-even carbon price is transport-mode and corridor specific. Lagouvardou et al. [52] take this furthest toward the present approach: through a cost–benefit comparison of allowance cost against a network-reconfiguration scenario, they identify the EU carbon-price turning point above which a container operator's transshipment-hub switch becomes cost-effective — a per-network break-even price derived for a specific routing decision. Their analysis is confined to a single binary reconfiguration (relocate the hub or not) in maritime liner service; it does not produce a continuous MAC curve across budget levels, nor a multi-regime classification, nor the co-benefit and infeasibility regimes that arise from discrete land-side modal substitution.

---

## EDIT 5 — §2.5, qualify the gap claim with the threshold lineage (line 125)

**Rationale:** §2.5 currently asserts the gap by listing what each adjacent literature does *not* do. After the second pass this reads as an unqualified gap a reviewer can puncture with Noguchi or Chen. Convert the assertion into a *bounded* claim that names the threshold lineage and states precisely what is left.

**FIND (end of line 125):**

> …What remains underdeveloped is the middle layer: deriving a network-specific MAC curve from an intermodal-routing MILP and using it to determine whether a logistics manager should shift modes, buy allowances, recognize co-benefit decarbonization, or redesign the network because the target is infeasible.

**REPLACE WITH:**

> …What remains underdeveloped is the middle layer: deriving a network-specific MAC curve from an intermodal-routing MILP and using it to determine whether a logistics manager should shift modes, buy allowances, recognize co-benefit decarbonization, or redesign the network because the target is infeasible. This gap is narrow and must be stated precisely, because the adjacent concept of carbon-price-induced regime thresholds is well established. Supply-chain-planning models have reported inflection points in the cost–emission response to carbon pricing since Zakeri et al. [49]; transport mode-selection models have derived policy-dependent mode-shifting thresholds since Chen et al. [50]; multimodal network-design MILPs show that below a threshold cap, carbon procurement becomes necessary [53]; and Noguchi [47] gives a formal existence proof of discontinuous modal-mix regimes on capacity-constrained multimodal networks. The present paper does not claim to discover regime thresholds. It claims the narrower and previously unfilled step of constructing the network-specific MAC curve that *locates* those thresholds for an intermodal-routing MILP, comparing it against observable carbon markets, and packaging the result as a five-regime taxonomy a practitioner can apply to classify a given network.

---

## EDIT 6 — §2.5, soften the "to the best of our knowledge" sentence (line 127)

**Rationale:** Standing alone after the new lineage paragraph, line 127 is now redundant and slightly overreaching. Tighten so it is consistent with Edit 5 and cannot be read as denying the threshold precedents.

**FIND (line 127):**

> To the best of our knowledge, prior intermodal-routing studies have not derived network-specific MAC curves from parametric MILP and converted them into an operational carbon-compliance regime taxonomy covering mode shift, allowance purchase, co-benefit decarbonization, and infeasible targets.

**REPLACE WITH:**

> To the best of our knowledge, although regime-threshold behaviour under carbon pricing is established in adjacent literatures [47, 49, 50, 53], no prior intermodal-routing study has derived a network-specific MAC curve from parametric MILP and converted it into an operational carbon-compliance regime taxonomy spanning mode shift, allowance purchase, co-benefit decarbonization, and infeasible targets.

---

## EDIT 7 — Reference list: add five entries

**Rationale:** Add the second-pass citations. Numbering continues from the current last entry **[46]** (Glenk). They are listed below in order of first appearance in the text per the edits above.

**INSERT after [46]:**

> [47] T. Noguchi, Turnpike theorems and thresholds for carbon-priced modal split on capacity-constrained transport networks, Networks Spat. Econ. (2025). https://doi.org/[confirm DOI]
>
> [48] A. Heinold, F. Meisel, Emission rates of intermodal rail/road and road-only transportation in Europe: A comprehensive simulation study, Transp. Res. Part D Transp. Environ. 65 (2018) 421–437. https://doi.org/10.1016/j.trd.2018.09.003
>
> [49] A. Zakeri, F. Dehghanian, B. Fahimnia, J. Sarkis, Carbon pricing versus emissions trading: A supply chain planning perspective, Int. J. Prod. Econ. 164 (2015) 197–205. https://doi.org/10.1016/j.ijpe.2014.11.012
>
> [50] X. Chen, G. Hao, Effects of carbon emission reduction policies on transportation mode selections with stochastic demand, Transp. Res. Part E Logist. Transp. Rev. 90 (2016) 196–205. https://doi.org/10.1016/j.tre.2015.11.008
>
> [51] L. Rekker, M. Mulder, et al., Carbon abatement in the European chemical industry: assessing the feasibility of abatement technologies by estimating firm-level marginal abatement costs, Energy Econ. 126 (2023) 106943. https://doi.org/10.1016/j.eneco.2023.106943
>
> [52] S. Lagouvardou, H.N. Psaraftis, Implications of the EU Emissions Trading System (ETS) on European container routes: A carbon leakage case study, Marit. Transp. Res. 3 (2022) 100059. https://doi.org/10.1016/j.martra.2022.100059
>
> [53] A. Majumdar, et al., Network design for a decarbonised supply chain considering cap-and-trade policy of carbon emissions, Ann. Oper. Res. (2023). https://doi.org/[confirm DOI]

---

## Application checklist

- **Reference numbering.** This redline assigns Noguchi **[47]**, Heinold & Meisel **[48]**, Zakeri **[49]**, Chen **[50]**, Rekker **[51]**, Lagouvardou **[52]**, Majumdar **[53]**, continuing from the existing Glenk **[46]**. The in-text tags in Edits 1–6 use these numbers. If your build renumbers references automatically, verify the seven new tags resolve correctly after insertion.
- **DOIs to confirm before submission.** Noguchi [47] (in-press; confirm volume/DOI), Glenk [46] (already flagged), Majumdar [53] (Ann. Oper. Res. online-first; confirm). Do not submit with placeholder DOIs.
- **Verify [35] is the correct Misconel paper** — the *J. Clean. Prod.* 2022 step-wise MACC paper, not the *Energy Strategy Reviews* 2024 item.
- **Edits are independent and non-overlapping** except that Edit 2 and Edit 5 both cite Noguchi [47]; that is intentional cross-reinforcement (intro positioning + related-work gap), not duplication.
- **Net effect on framing.** After these edits: the *decision rule* is claimed as a new routing-network instantiation of an established rule (walled vs. Rekker, Lagouvardou); the *taxonomy* is claimed as a new operational five-regime scheme over an acknowledged conceptual base (walled vs. Noguchi, Zakeri, Chen); the *managerial implication* is foregrounded but no longer called "validated" (bounded vs. Heinold & Meisel); and the synthesis is presented as operationalization, not discovery. That is the defensible position the four claims can hold under a hard review.
