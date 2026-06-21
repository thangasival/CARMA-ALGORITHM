# Peer Review — CARMA v3

**Manuscript:** *Marginal Abatement Cost as a Carbon Decision Signal in Intermodal Supply Chain Routing: A Parametric MILP Framework for Mode Shift, Allowance Purchase, and Departure Timing*
**Target journal:** Supply Chain Analytics (Elsevier), ISSN 2949-8635
**Article type:** Research Article
**Manuscript version reviewed:** v3 (2026-06-14)
**Review date:** 2026-06-21
**Severity register:** Harsh ("Reviewer 2" mode), as requested
**Reviewer note:** This is a *simulated* pre-submission peer review, generated to mirror what an SCA reviewer would likely return. It is not an official editorial decision. No Supplementary Information file was provided or referenced.

---

## 2. Summary of the manuscript

The paper develops a parametric MILP framework that estimates finite-difference marginal abatement cost (MAC) curves for intermodal freight routing by solving the carbon-budgeted assignment problem at successive reduction targets and differencing adjacent integer solutions, deliberately bypassing LP-relaxation duals (reported as zero in all 33 solves). The resulting network-specific MAC is compared against an observable carbon price to classify each (network, budget) point into one of five carbon-compliance regimes: mode-shift preferred, parity, allowance-purchase preferred, co-benefit decarbonization, or infeasible. Across three hand-constructed network archetypes (Salamanca domestic truck-rail, Iberian maritime, Frankfurt hub) plus 150 stochastically generated variants, the central finding is that domestic truck-rail mode shift carries MAC of 245–4,366 €/t — 4–67× the EU ETS 2024 price of 65 €/t — placing it permanently in the allowance-preferred regime, while maritime networks decarbonize as a co-benefit of cost minimization and hub networks hit a hard feasibility ceiling near 25%. The framework is explicitly positioned as a supply-chain decision-analytics contribution rather than a new optimization method.

---

## 3. Overall assessment

**Strengths.** The decision-analytics framing is genuine and well-suited to SCA's prescriptive-analytics mandate: the paper does not merely optimize a route plan, it converts optimization output into a named instrument choice (shift / buy / do-nothing / redesign). The honesty about scope is unusually mature for a v3 — the contribution-hierarchy discussion (§1.4), the "procedure vs. numerical values" generalizability boundary (§3.4), and the Table 8 claim-strength ledger are exactly the kind of self-discipline reviewers reward, and they pre-empt several objections. The step-function MAC argument is correct and the LP-dual-failure motivation is technically sound. The literature positioning against Noguchi [47], Misconel [35], Glenk [46], Rekker [51], and Lagouvardou [52] is careful and, where I could check it, accurate.

**High-level concerns.** Three things stand between this manuscript and a defensible submission, and the first is serious:

1. The headline empirical claim is **internally contradicted by the paper's own robustness table.** The abstract, the §6 preamble, and Propositions 1 say domestic rail-limited networks are uniformly allowance-preferred with "0% shift-preferred." But Table 9 reports that 54% of the 50 generated rail-limited networks are *non-binding / co-benefit* at 20% budget. "Not shift-preferred" and "allowance-preferred" are being silently conflated, and the conflation props up the central thesis. This must be fixed before submission — a reviewer who notices it (and SCA uses ≥2 expert reviewers) will lose trust in every other number.

2. **Evidentiary base is entirely synthetic.** Three archetypes you designed to land in their predicted regimes, plus generated networks sampled from the *same* structural constraints. The paper is candid that this demonstrates internal consistency, not real-world frequency — but for a prescriptive-analytics journal, a framework whose entire validation is "the model behaves as I constructed it to behave" is thin. At least one real corridor is needed.

3. **Numerical inconsistencies** between the abstract, the §6 preamble, Table 9, and §6.6 prose. Several reported statistics do not match across locations (detailed in Major 3).

This is not a reject-grade idea — the framing is publishable. But in its current state it is **Major revision needed**, bordering on Substantial rework because of Major 1.

---

## 4. Major comments

**Major 1 — The central "0% shift-preferred = allowance-preferred" claim contradicts Table 9.**
*Location: Abstract (lines 31, 17), §6 preamble (line 344), §6.6 Table 9 (line 480), Proposition 1 (lines 532, 490).*
The abstract states "0% shift-preferred in rail-limited networks" and frames the domestic class as sitting "in a permanent allowance-preferred regime." Proposition 1 reports "0% shift-preferred outcomes across 50 generated rail-limited domestic networks at 65 €/t, with median MAC of 1,398 €/t." But Table 9 reports the rail-limited domestic family as **54.0% non-binding/co-benefit and only 46.0% allowance-preferred** at 20% budget. A network in the co-benefit regime is one where the cost optimum *already* meets the budget — which is the *opposite* of "physical mode shift is uneconomic so you must buy allowances." More than half your generated domestic networks therefore do not support the headline narrative; they support a *different* (and arguably more interesting) story: that even rail-limited domestic networks frequently decarbonize for free at modest targets. As written, the paper buries this by reporting only the "0% shift-preferred" slice and computing median MAC over "binding cases" only. **Action:** Reconcile this directly. Either (a) restrict the headline claim to *binding* domestic networks and state up front that ~54% are non-binding at 20%, or (b) re-run at a tighter budget where more networks bind and report that. Do not let "not shift-preferred" stand in for "allowance-preferred" anywhere in the abstract, propositions, or highlights.

**Major 2 — No field or real-corridor validation; the entire evidence base is self-constructed.**
*Location: §5.1 (line 324), §6.6 (lines 470–484), §7.4 (lines 563–565).*
The three archetypes are explicitly designed so that "the experiment tests whether each structural class lands in its predicted regime" — i.e., you built networks to confirm predictions, then confirmed them. The 150 generated networks are sampled within the same family-defining constraints, so they test stability, not external validity, as you concede. For a journal whose scope is *prescriptive* analytics that "suggest[s] alternative courses of action to supply chain managers," a framework validated only against its own construction is a weak managerial artifact. The Heinold & Meisel [48] ±2.5× "calibration anchor" (line 484) is a plausibility argument, not a validation. **Action:** Add at least one real corridor with published or obtainable cost/emission data (even a single lane) and show the framework recovers a sensible regime classification. If genuinely impossible before submission, reframe the contribution explicitly as a *methodological / conceptual* framework with illustrative synthetic experiments, soften the abstract's empirical-sounding "Applied to three intermodal network structural classes," and move field validation from "future work" to "required next step" in the framing.

**Major 3 — Cross-location numerical inconsistencies erode confidence in the results.**
*Location: Abstract (line 31), §6 preamble (line 344), Table 9 (line 480), §6.6 prose (line 484).*
Several numbers do not agree across the manuscript:
- §6 preamble (line 344) says hub-limited median maximum feasible abatement is **15%**, and rail-limited median MAC **1,398 €/t**; Table 9 (line 480) lists rail-limited *median max feasible* as **50%** and hub as **15%** with hub median MAC **920 €/t** — but the §6 preamble (line 344) gives hub "52% infeasible" while also describing rail-limited as "0% shift-preferred." These are individually findable but collectively confusing because the same families are described with different summary statistics in three places.
- The abstract (line 31) reports rail-limited median MAC "1,398 €/t (21× ETS)" but §6.6 (line 484) gives the generated-family range as "142 to 9,093 €/t" while the base-case Salamanca table (line 363) tops out at 4,366 €/t and the §6.6 Heinold-adjusted range is "130–11,000 €/t." A reader cannot reconstruct which range is authoritative.
**Action:** Build one master results table (family × statistic) and make every in-text number, the abstract, and the highlights cite *from it.* Verify each figure. Reviewers read the abstract and Table 9 side by side; discrepancies here read as carelessness at best.

**Major 4 — Salamanca dataset overlap with Sánchez-Pravos et al. [5] needs sharper handling, including self-overlap risk.**
*Location: §1.5 (line 85), §2.1 (line 99), §5.1 (line 326).*
You share the Salamanca network with [5], a 2026 SCA paper (confirmed: Sánchez-Pravos et al., *Supply Chain Analytics* 13 (2026) 100182). The methodological distinction you draw — they optimize assignments with ML-predicted emission factors, you derive the MAC of those assignments — is legitimate and clearly argued. Two residual risks: (i) an SCA reviewer may be an author or close reader of [5] and will scrutinize whether your Salamanca cost/emission inputs are *identical* to theirs or re-derived; state this explicitly. (ii) The paper reuses emission-model machinery (the six-factor physics-informed formula, §4.2 line 316) that appears to originate in your own related work — if so, this risks text/result recycling and should be cited to its origin and described as adopted, not introduced here. **Action:** Add one sentence in §5.1 stating exactly which inputs are taken from [5] vs. recomputed, and cite the origin of the six-factor emission formula if it is prior work of your own.

**Major 5 — The novelty that survives is narrow; make sure the paper claims only that, consistently.**
*Location: §1.4 (lines 65–77), §2.3 (lines 117–123), Table 1 (line 142).*
The literature audit (below) confirms that the abate-vs-buy conclusion, carbon-price regime thresholds, step-function MAC, and MAC-vs-ETS firm-level comparisons are all prior art — which you commendably concede. What is left as novel is the *operationalization*: a finite-difference MAC estimator for routing + five named regimes + topology-driven a-priori indicators + endogenous network break-even price. That is a real but modest contribution. The risk is that Table 1 (line 142) overstates it: the "This paper" row claims "Dynamic CI" and "Pareto front (4-obj)" as differentiators, but the dynamic carbon-intensity timing (RQ4) and the Pareto search (RQ3) are explicitly demoted to "supporting" analyses elsewhere and are barely evidenced in Results (I found no Pareto-quality table and only a single 8.9% departure-timing number at line 599). **Action:** Either give RQ3/RQ4 real results sections or cut them from the contribution table and abstract. A reviewer will check that every column you claim is backed by a result. Right now two are not.

**Major 6 — RQ3 (Pareto) and RQ4 (departure timing) are advertised but not delivered.**
*Location: RQs (lines 57, 59), Highlights (line 18), Conclusion (line 599), Data Availability (line 613).*
RQ3 asks whether exact-model information improves Pareto trade-off discovery; RQ4 asks about departure-timing savings. Neither has a dedicated, evidenced results subsection in §6 (which runs §6.1–§6.6 on MAC/regimes only). The conclusion asserts "8.9% fleet emission reduction" for departure timing (line 599) with no supporting table, design, or analysis anywhere in §5–§6. The scripts are listed in Data Availability but the paper must stand on its own. **Action:** Add §6.x subsections with the actual RQ3/RQ4 results and methods, or remove these RQs, the corresponding highlight, the Table 1 columns, and the conclusion sentence. Half-present research questions invite a "what happened to RQ3/4?" reviewer comment that reads as incompleteness.

**Major 7 — Unverifiable / forthcoming references in load-bearing positions.**
*Location: References [46], [47], [53] (lines 721, 723, 735); used at §2.2 (line 105, 109), §1.4 (line 75), §2.3 (line 117).*
[46] Glenk et al. is "forthcoming" with a DOI placeholder and an *internal editorial note* still embedded in the reference ("DOI must be confirmed before submission — if still unpublished, replace comparison in §2.2 with Rekker et al. [51]"). [47] Noguchi and [53] Majumdar also carry "DOI must be confirmed" placeholders. Noguchi [47] is doing real positioning work — it is your closest theoretical prior art (§1.4 line 75, §2.3 line 117). Citing an unconfirmed/forthcoming paper as the thing your contribution is carved against is fragile: if a reviewer cannot find it, your novelty boundary collapses. **Action:** (1) Remove the embedded editorial note from [46] immediately — it must not appear in a submitted manuscript. (2) Confirm DOIs/venues for [47] and [53] or downgrade them to "working paper"/preprint with a stable URL. (3) If Noguchi [47] is not yet publicly retrievable, lean the theoretical-prior-art argument on the published Zakeri [49] / Chen [50] instead so the novelty boundary does not depend on an unverifiable source.

---

## 5. Minor comments

1. **Highlight overreach.** Highlight 3 (line 17) states the Iberian network "achieves 77% emission reduction at 56% cost saving" as if a finding; it is a single constructed archetype. Hedge to "in the maritime archetype."
2. **Abstract is one 380-word paragraph.** SCA abstracts are typically tighter and unstructured but shorter. Trim to ~250 words; the LP-dual mechanics can move to the body.
3. **"33 solves" vs "1,650 solves."** The abstract emphasizes "zero in all 33 solves" (base cases) but the robustness study is 1,650 solves. Clarify early that 33 refers to base archetypes only, to avoid the impression the LP-dual check covered all runs.
4. **Section numbering gap.** §3.4 is followed by §3.6 (Algorithm Summary) — there is no §3.5. Renumber.
5. **Regime 4 MAC sign.** §3.2 (line 196) says λ̂ "= 0 / undefined" for non-binding, but §3.3 (line 230) labels Regime 4 "λ̂ undefined" and the abstract (line 31) calls co-benefit "negative MAC." Pick one convention — undefined (constraint non-binding) and negative (co-benefit shift saves money) are different cases and are being merged.
6. **Table X / Table Y unlabeled.** The tables at lines 127 and 543 are "Table X" and "Table Y." Give them numbers.
7. **"16% of global CO₂" (line 39)** is cited to [1], an IEA chart on transport sub-sectors. Confirm the 16% is supply-chain *transport* specifically and that [1] states it; the figure is often quoted for transport overall.
8. **CRI / fourth objective (line 298)** introduces weather Φ(w), congestion, and a θ parameter with exponent 0.70 and no citation or calibration. Since f₄ feeds the (demoted) Pareto analysis, either justify these constants or note they are illustrative.
9. **Complexity claim (line 279)** "T_MILP = 50–200 ms for n = 12–50" — report the machine/solver version; CBC timings are hardware-specific.
10. **Solver determinism.** You report LP duals "0.0 in all 33 solves" as confirmation; note the CBC version, since dual reporting behavior is solver- and version-dependent (you partly address this at line 567).
11. **Algorithm 1 step 4** classifies Regime 4 via "E₀ ≤ B(r)" but step 2 already set Regime 4 inside the loop; the two are redundant and could disagree if E₀ is the unconstrained optimum vs. baseline. Tighten.
12. **"co-benefit (negative MAC)"** appears in the abstract but Table 2 Iberian (line 370) shows the co-benefit as a one-shot −55.7% cost / −77.1% emissions jump at the unconstrained optimum, not a swept negative MAC curve. The Iberian "curve" is a single point; say so.
13. **Departure-time pathway (Pathway 3, line 166)** is introduced as a core compliance pathway in §3.1 but never enters the five-regime taxonomy or the MAC math. Either integrate it or present it as an adjunct.
14. **Reference [17] HBEFA dated 2026** (line 663) but emission factors cited as "HBEFA 4.2" (line 314); confirm the version/year alignment.
15. **GitHub repo (line 613)** is cited as the data-availability source; ensure it is public and anonymized appropriately for single-anonymized review (the author name is already on the manuscript, so this is lower-risk here, but confirm the repo resolves).
16. **"45%" row MAC 2,193 then "50%" MAC 4,366 (Table 2, lines 362–363)** — an 18× headline increase is quoted (line 387) from 245→4,366; the intermediate jump from 2,193 to 4,366 is the largest single step and deserves a one-line mechanistic explanation (which route switches and why it is so costly).
17. **Maps/territorial note** — SCA (per Elsevier guide) requires a study-area-map disclaimer if maps are shown. You use city pairs, not maps, so likely N/A, but confirm no figure renders a national-boundary map.

---

## 6. Reporting-standard compliance

No EQUATOR reporting standard applies: this is an operations-research / decision-analytics methods-and-application paper, not a clinical, observational, or systematic-review study. The relevant rigor expectations are general OR/computational-experiment norms.

| Rigor dimension | Status | Note |
|---|---|---|
| Reproducibility (code/data) | Partial → Good | Public repo + scripts listed; verify it resolves and is runnable (Major 2/Minor 15). |
| Experimental design stated | Yes | §5 is clear; but design is confirmatory-by-construction (Major 2). |
| Random seeds / variants reported | Yes | Appendix A documents seeds 0–49 per family. |
| Baseline / comparator fairness | Partial | Table 1 comparators are characterized, not re-run; some claimed columns unevidenced (Major 5). |
| Sensitivity analysis | Yes (strong) | §6.4 step-size, §6.5 parameter sweep (240 cells) are genuine strengths. |
| Internal numerical consistency | **No** | Cross-location mismatches (Major 1, Major 3). |
| Statement of limitations | Yes (strong) | §7.4 is thorough and honest. |

---

## 7. Literature audit

**Field context.** A targeted Consensus audit confirms the manuscript sits in a crowded space and, to the author's credit, the paper already concedes most of it. Model-derived MAC for sector/energy decarbonization is mature ([Ricci et al. 2025](https://consensus.app/papers/details/759679a203cb52aaa2c1a2350721f59b/?utm_source=claude_desktop) — which the paper cites as [36] and which corroborates the "freight is under-studied" gap; [Du et al. 2021](https://consensus.app/papers/details/c4701847f7005352b640fca35abbcfe3/?utm_source=claude_desktop); [Longva et al. 2024](https://consensus.app/papers/details/53e708f0398d558aa72207d40b35d284/?utm_source=claude_desktop) for shipping MACCs at 50–300 USD/t). Carbon-price-driven modal-shift thresholds in multimodal MILP/optimization are well established ([Wu et al. 2024](https://consensus.app/papers/details/3fe685a1b4745af2b64f63104668d21e/?utm_source=claude_desktop), [Chen et al. 2024](https://consensus.app/papers/details/046d1d74bfcd5cbb8066d992b6e1501a/?utm_source=claude_desktop), [Yin et al. 2025](https://consensus.app/papers/details/084e0c5d9eb35f2bafb1ec58e17ee8ed/?utm_source=claude_desktop)).

**Novelty assessment per claim.**
- *Abate-vs-buy / allowance-preferred conclusion:* **Prior art**, correctly conceded (Rekker [51], Boehm [44], Zakeri [49]). [Wu et al. 2024](https://consensus.app/papers/details/3fe685a1b4745af2b64f63104668d21e/?utm_source=claude_desktop) independently report that for oversize/heavy cargo, transport+modification costs dwarf carbon costs so ETS price fluctuation barely moves the optimum — the same qualitative mechanism behind your allowance-preferred regime. Consider citing as further corroboration.
- *Carbon-price regime thresholds:* **Prior art** (Zakeri [49], Chen [50], Noguchi [47]). Conceded.
- *Step-function MAC for discrete assignment:* **Prior art** (Kiuila & Rutherford [31], Misconel [35]). Conceded.
- *Finite-difference MAC estimator + 5 named regimes + endogenous network break-even price + topology indicators, for intermodal routing:* **Defensibly novel as a synthesis/operationalization.** No retrieved paper packages exactly this. [Chen et al. 2024](https://consensus.app/papers/details/046d1d74bfcd5cbb8066d992b6e1501a/?utm_source=claude_desktop) derive *carbon-tax* mode-switch thresholds (60% → road-to-rail, 140% → rail-to-water) but do not frame them as a MAC-vs-market break-even or a regime taxonomy. The narrow novelty survives — but it is narrow (Major 5).

**Citation spot-checks.**
- [5] Sánchez-Pravos et al. — **verified** as a real 2026 *Supply Chain Analytics* paper (100182). Prior-art handling is fair (Major 4 flags the residual overlap risk).
- [36] Ricci et al. — **verified**; the "significant research gap in the freight sector" quote is faithful to the abstract.
- [47] Noguchi, [46] Glenk, [53] Majumdar — **could not verify** (forthcoming / placeholder DOIs). See Major 7.

**New since this revision:** none flagged as missing — the audit surfaced corroborating, not invalidating, work. [Wu et al. 2024] and [Chen et al. 2024] predate v3 and could strengthen §2.1.

---

## 8. Journal-specific assessment

**8.1 Scope fit.** SCA's stated scope is *prescriptive* analytics that "build on descriptive, predictive, and diagnostic analytics to compare scenarios, provide insight, and suggest alternative courses of action to supply chain managers," using optimization/ML/simulation. The paper fits well on the *prescriptive* axis — it explicitly produces a course of action (shift/buy/redesign). The weak point relative to scope is the *data* expectation: the journal notes prescriptive work "typically requires more data"; this paper has synthetic data only (Major 2).

**8.2 Novelty calibration.** Against SCA comparators, the bar is applied analytics with a clear managerial decision output, not algorithmic novelty — which suits this paper's framing. Named comparators: Sánchez-Pravos et al. [5] (same journal, same Salamanca network, ML+GA routing) sets a directly relevant precedent and bar; your decision-layer contribution is differentiable but must out-deliver [5] on either realism or decision usefulness. **Verdict: bar is meetable, but currently undersold by the synthetic-only evidence and the unfinished RQ3/RQ4.**

**8.3 Style match.** Length and structure are within range for SCA; the prose is dense and occasionally repetitive (the abate-vs-buy concession is restated ~5 times across §1.4, §2.2, §2.3, §6.2, §7.4). Tighten.

**8.4 Required-but-missing items.**

| Item | Status | Action |
|---|---|---|
| Embedded editorial note in reference [46] | **Present — must remove** | Delete before submission. |
| Structured/length-compliant abstract | Borderline | Trim to ~250 words. |
| Declaration of Competing Interest | Present | OK. |
| CRediT statement | Present | OK. |
| Data availability statement | Present | Verify repo resolves. |
| AI-use disclosure | Not seen | Add if any AI tools were used in writing/analysis (Elsevier policy). |
| Highlights ≤ 85 chars each | Verify | Several highlights look long; check the character limit. |
| Figures (Fig. 2, Fig. 3) | Referenced, not embedded | Ensure they are included and legible in submission. |

**8.5 Alternative venues** (only if Major 2 cannot be addressed): *Cleaner Logistics and Supply Chain* (Elsevier), *Transportation Research Part D*, or *Computers & Industrial Engineering* would accept a more methods-framed version with synthetic-only validation more readily than SCA's prescriptive-managerial bar.

---

## 9. Recommendation

**Major revision needed** — conditional, and close to "Substantial rework" because of Major 1.

The framework is a legitimate, scope-appropriate decision-analytics contribution and the self-aware scoping is a real asset. But the paper cannot go out while its headline claim is contradicted by its own Table 9 (Major 1), while two of four research questions are advertised but unevidenced (Major 6), and while a load-bearing reference still contains an internal editorial note (Major 7). None of these is fatal to the *idea* — they are fixable in one revision cycle — but together they would, in harsh review, likely draw a reject-and-resubmit rather than minor revision. Priorities, in order: (1) reconcile the 0%-shift / 54%-co-benefit contradiction and rebuild a single master results table; (2) add one real corridor or honestly re-frame as conceptual/methodological; (3) finish or cut RQ3/RQ4; (4) clean the references. Do those four and this is a credible SCA submission.

---

## 10. Audit log

**Manuscript:** CARMA v3, ~10,500 words, 759 source lines, 53 references, 3 base archetypes + 150 generated networks (1,650 MILP solves), 9 numbered tables + 2 unlabeled (Table X/Y) + 2 figures (referenced, not embedded). Manuscript type: methods-and-application (OR / decision analytics). No EQUATOR standard applicable. No SI provided.

**Journal sources fetched:**
- SCA Guide for Authors — https://www.sciencedirect.com/journal/supply-chain-analytics/publish/guide-for-authors (scope, single-anonymized review, ≥2 reviewers confirmed; full word/figure limits not fully extracted from the live page — author should confirm against the guide directly).

**Consensus searches run (3):**

| # | Query | Purpose | Key hits |
|---|---|---|---|
| 1 | marginal abatement cost curve intermodal freight transport mode shift carbon price | Field map + MAC-for-transport novelty | Ricci 2025, Du 2021, Longva 2024, Wu 2024, Chen 2024, Yin 2025 |
| 2 | break-even carbon price mode shift vs allowance purchase decision rule logistics network optimization | Direct novelty test of the regime/break-even claim | No exact-match taxonomy found; nearest are cap-and-trade network-design MILPs |
| 3 | machine learning evolutionary optimization carbon-aware supply chain routing Salamanca emission prediction | Verify Sánchez-Pravos [5] prior art | [5] verified as real 2026 SCA paper |

**Coverage notes / limitations of this review.** The SCA author-guide page did not fully render word/figure/abstract limits, so §8.4 items flagged "verify" should be checked against the live guide. References [46], [47], [53] could not be verified (forthcoming/placeholder DOIs) — see Major 7. Figures 2–3 were not provided, only referenced, so figure-fairness checks (rubric §6.5) could not be completed. Internal numerical consistency was checked across abstract, §6 preamble, Table 9, and §6.6 prose; the discrepancies in Major 1 and Major 3 are the material ones found.
