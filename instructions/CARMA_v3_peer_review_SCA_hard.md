# Pre-Submission Peer Review — CARMA v3

**Manuscript:** *Marginal Abatement Cost as a Carbon Decision Signal in Intermodal Supply Chain Routing: A Parametric MILP Framework for Mode Shift, Allowance Purchase, and Departure Timing*
**Target journal:** Supply Chain Analytics (Elsevier, ISSN 2949-8635)
**Article type (intended):** Original research / analytical
**Severity register:** Harsh ("Reviewer 2")
**Literature audit anchored to:** 21 June 2026
**Review date:** 21 June 2026
**Supporting material on file:** Appendix A + GitHub repository only (no SI)

> *Reviewer note.* This is a simulated peer review intended to mirror what two Supply Chain Analytics reviewers and a handling editor would likely return. It is deliberately harsh per your instruction. It is not an editorial decision, and a real referee may weight these points differently. Every external claim is grounded in sources retrieved this session; Consensus links are live.

---

## 1. Summary of the manuscript

The paper develops a parametric mixed-integer linear programming (MILP) framework that estimates finite-difference marginal abatement cost (MAC) curves for carbon-constrained intermodal routing by solving the cost-minimizing MILP at a sequence of tightening carbon budgets and differencing adjacent solutions, rather than reading shadow prices from LP-relaxation duals (which the authors report as zero in all 33 base solves). The resulting MAC curve is compared against an observable carbon price to classify each (network, budget) point into one of five carbon-compliance regimes: mode-shift preferred, parity, allowance-purchase preferred, co-benefit decarbonization, or infeasible. The framework is exercised on three network archetypes (rail-limited domestic, maritime-accessible long-haul, hub-limited redundancy), with a 150-network / 1,650-solve robustness study testing whether each archetype stays in its predicted regime under parameter sampling. The headline empirical finding is that domestic truck-rail mode shift is uneconomic at realistic carbon prices (MAC 245–4,366 €/t, 4–67× the 2024 EU ETS price), placing it firmly in the allowance-preferred regime, while maritime-accessible networks decarbonize as a cost-minimization by-product and hub networks hit a hard feasibility ceiling.

---

## 2. Overall assessment

**Strengths.** The framing is genuinely useful: the question "should this network shift modes or buy allowances at this carbon price?" is a real decision-analytics gap, and the five-regime taxonomy is a clean, communicable packaging of it. The manuscript is unusually honest about its own boundaries — the contribution hierarchy in §1.4, the "procedure versus numerical values" separation in §3.4, and the strength-of-claims Table 8 are exactly the kind of self-discipline that survives review. The finite-difference-over-binding-steps argument for absolute-MAC validity (§3.2) is well reasoned. Statistical/internal-consistency checks (below) pass: the MAC arithmetic reconciles with the cost/emission tables at every spot-checked step.

**High-level concerns.** Four issues materially affect publishability, in descending order:

1. **The methodological-novelty claim collides with prior art the paper does not cite.** The "parametric MILP adaptation for finite-difference MAC" (Contribution 2) is, as a *method*, Jenkins (1982, *Management Science*) — RHS-parametric MILP solved at point values and joined, with a heuristic exploiting flat regions where the integer solution is unchanged. That is the manuscript's sweep-and-difference procedure and its step-function structure. The paper currently positions this contribution as "the only auditable, transparent, solver-independent way" without engaging the canonical reference for the exact technique. (Major 1.)

2. **The empirical base is three hand-built archetypes plus same-distribution resampling, and the paper repeatedly tells the reader so — which invites the question of what is actually being validated.** The 150-network study is explicitly *internal* consistency, not real-world frequency (§6.6). Stripped of external grounding, the empirical contribution reduces to "a framework we designed to produce regime X on archetype Y does produce regime X on archetype Y, and on networks sampled to resemble Y." This is not fatal, but at harsh severity it is the difference between "demonstration" and "validation," and the abstract/highlights still read as validation. (Major 2.)

3. **A large machinery — NSGA-III Pareto search, departure-time scheduling, the six-factor physics-informed emission model — is invoked in scope, conclusion, and data-availability but never reported in Results.** The conclusion claims "8.9% fleet emission reduction" from departure timing and "improves trade-off coverage" from Pareto search; neither number nor figure appears in §6. Either report these or cut them. As written they read as residue from a larger manuscript and will draw a "where are these results?" from any careful referee. (Major 3.)

4. **Scope fit with Supply Chain Analytics is plausible but not airtight.** SCA's stated remit is *prescriptive* analytics that "suggest alternative courses of action to supply chain managers" using optimization/ML/simulation. The regime taxonomy fits that framing well. But the paper's own §1.5 concedes the directly comparable prior work (Sánchez-Pravos et al. [5]) is *in this journal* and shares the Salamanca dataset — so the novelty bar is set by a paper the editor can see at a glance. The delta must be unmistakable in the abstract, not argued over three paragraphs in §1.4. (Major 4.)

**Headline recommendation:** **Major revision needed.** The core idea is publishable in SCA and the honesty is a real asset, but the methodological-novelty framing must be corrected against Jenkins (1982) and the Chen et al. (2024) threshold result, the unreported machinery must be reported or removed, and the empirical claims must be brought into line with what three archetypes can actually support.

---

## 3. Major comments

**Major 1 — The parametric-MILP method you claim to adapt is Jenkins (1982), which you do not cite; correct the novelty framing.**
*Location: §1.4 Contribution 2; §2.2 ("No prior intermodal routing paper… constructs a parametric MAC curve from sequential MILP solves"); §3.2 final paragraph; §2.3.*
Contribution 2 claims finite-difference MAC from sequential MILP solves is "the only auditable, transparent, and solver-independent way to recover a managerial carbon-compliance signal in discrete routing models." But [Jenkins, *Parametric Mixed Integer Programming: An Application to Solid Waste Management*, Management Science 1982](https://consensus.app/papers/details/5a7bbfc644095e16b293d3b4841604ad/) established exactly this procedure: solve the MILP at point values of a right-hand-side parameter and join the results, with a heuristic rule that the same integer solution remains optimal across intermediate RHS values (your "flat regions"). Your method *is* RHS-parametric MILP applied to the carbon-budget constraint. This does not sink the paper — your transposition to carbon compliance and the regime taxonomy are still defensible — but the current wording is overclaiming and an OR-literate referee will catch it immediately. **Action:** cite Jenkins (1982) explicitly; restate Contribution 2 as "we apply RHS-parametric MILP (Jenkins 1982) to the carbon-budget constraint and reinterpret the resulting step-function value differences as a managerial MAC signal." The novelty then rests cleanly on the *decision-analytics interpretation*, where it is genuinely defensible, not on the *computational technique*, where it is not.

**Major 2 — Distinguish "internal consistency" from "robustness" honestly in the abstract and highlights, not only in §6.6.**
*Location: Abstract; Highlights; §6 preamble; §6.6.*
§6.6 is admirably candid: the generated networks are sampled within the same structural-class constraints as the base cases, so they "demonstrate internal consistency, not real-world regime frequencies." But the abstract presents the 150-network / 1,650-solve numbers (54%/46%, 100%, 52%) as if they were robustness *evidence*, and Highlight 1–3 read as empirical findings about the world. A harsh referee will call this a presentation that oversells the design. The 1,650 solves do not test whether the taxonomy is *correct about real networks*; they test whether it is *self-consistent under parameter perturbation within a class you defined*. That is a legitimate and worthwhile check — but it must be labelled as such everywhere, including the abstract. **Action:** add one clause to the abstract ("a within-class consistency study, not a population sample") and reword Highlights 1–3 to foreground mechanism over frequency.

**Major 3 — Report the NSGA-III Pareto search, departure-time scheduling, and emission-model results, or remove them from scope/conclusion/data-availability.**
*Location: §1.5; §4.4 (emission model); §7.1 Rule 4; Conclusion para 3 ("8.9% fleet emission reduction"); Data Availability (`demo_carma.py`, `scalability_benchmark.py`).*
The conclusion asserts two quantitative results that appear in no results section: an 8.9% departure-timing emission reduction and that "exact-model-informed multi-objective Pareto search improves trade-off coverage." The MILP/MAC core of the paper does not use NSGA-III at all (it is single-objective, §4.2). Either (a) add a results subsection with the Pareto-coverage metric and the 8.9% derivation, or (b) cut these claims and the corresponding scope/limitations/repo references. Leaving them in without results is the single most likely trigger for a "the manuscript is internally incomplete" desk-stage flag. If the Pareto/scheduling material belongs to a different paper, remove it here. **Action:** decide whether this is one paper or two, and make §6 match §1.5 and §8 exactly.

**Major 4 — Sharpen the delta against Sánchez-Pravos et al. [5] in the abstract, since it is in-journal and shares your dataset.**
*Location: Abstract; §1.5; §2.1.*
You concede [5] is "directly comparable prior art, sharing the Salamanca network dataset" and published in SCA. The handling editor will see this instantly. Your distinction — they optimize assignments, you derive the MAC of those assignments and classify the compliance response — is correct and sufficient, but it is currently buried. The abstract never names [5] or states the delta. **Action:** add one sentence to the abstract making the contribution-over-[5] explicit ("Unlike prior carbon-aware routing on this network, which minimizes cost and emissions, we derive the network's endogenous break-even carbon price and classify the rational compliance instrument"). Reusing their dataset is fine and even helpful for comparability — but say why the reuse is purposive up front.

**Major 5 — Engage Chen et al. (2024) and the recent threshold/switching-band literature you currently omit; the "regime threshold" concept is more crowded than §2.3 admits.**
*Location: §2.2; §2.3; §1.4 (Noguchi positioning).*
You position the regime-threshold concept against Zakeri [49], Chen & Hao [50], Noguchi [47], Majumdar [53]. But [Chen et al., *Low-Carbon Route Optimization Model for Multimodal Freight Transport*, Socio-Economic Planning Sciences 2024](https://consensus.app/papers/details/046d1d74bfcd5cbb8066d992b6e1501a/) already shows *discontinuous* mode transitions at specific carbon-tax thresholds (road→rail at +60%, rail→waterway at +140%) — a direct empirical analogue of your "the same price implies different decisions" claim. [Yin et al., *Transition of multimodal transport network under different carbon price scenarios*, Transport Policy 2025](https://consensus.app/papers/details/084e0c5d9eb35f2bafb1ec58e17ee8ed/) and the very recent [Mu et al., 2026, *Sustainable Futures*](https://consensus.app/papers/details/ae8501df94a5504ca80b07a968f9d828/) (explicit "switching bands," "boundary solutions," "threshold-staged" carbon under binding capacity) sit even closer to your framing. None of these defeats your contribution — none derives a *network-specific MAC curve* and converts it to a five-regime *operational* taxonomy with co-benefit and infeasibility regimes — but their absence makes §2.3's "this gap is narrow and must be stated precisely" look less precise than claimed. **Action:** cite Chen et al. (2024) and Yin et al. (2025) (and ideally Mu et al. 2026) in §2.2; restate the gap as "no prior work converts the network-specific MAC curve into a five-regime operational compliance taxonomy," which survives all of them.

**Major 6 — The co-benefit and infeasibility "regimes" are definitional, not findings; calibrate the claim strength accordingly.**
*Location: §3.3 (Regimes 4–5); Findings 2, 5, 6; Propositions 2–3.*
Regime 4 (co-benefit) is *defined* as the constraint being non-binding, and Regime 5 (infeasible) is *defined* as no feasible MILP. So "the Iberian network exhibits co-benefit" and "Frankfurt becomes infeasible above 25%" are not discoveries about MAC — they are restatements of the cost-optimal solution already satisfying / not being able to satisfy the budget, which any carbon-budget MILP returns directly (you say as much in Table 2's "solver status only" row). The genuine contribution is naming these as managerial regimes and embedding them in one taxonomy with the binding cases — which is fine — but Findings 5–6 and Propositions 2–3 are phrased as empirical results when they are largely tautological given the definitions. At harsh severity this reads as inflating three archetype observations into "propositions." **Action:** reframe Regimes 4–5 results as "the taxonomy correctly absorbs the two boundary cases that conventional solvers report only as status codes," and downgrade Propositions 2–3 from "empirically grounded structural rules" to "definitional boundary behaviors confirmed to occur in the sampled families."

**Major 7 — The "endogenous break-even carbon price B*(r)" is presented as the central novel object but is numerically identical to λ̂(r); clarify what work the renaming does.**
*Location: §3.1 (B*(r) = λ̂(r) × 1000); §1.4; Conclusion.*
B*(r) is defined as λ̂(r) × 1000 — i.e., the finite-difference MAC expressed in €/t instead of €/kg. The paper repeatedly elevates "the endogenous network break-even carbon price" to headline-contribution status, but it is a unit conversion of the MAC, not a distinct construct. The economic *interpretation* (compare to π) is the contribution; the renaming risks a referee concluding the paper has one idea wearing two names to look like two. **Action:** state plainly that B*(r) is the MAC re-expressed as a price for direct comparison to π, and let the contribution rest on the comparison rule + taxonomy rather than on B* as a separate object.

---

## 4. Minor comments

1. **Reference [46] (Glenk et al.) and [47], [53] carry "DOI must be confirmed before submission" / "forthcoming" placeholders.** SCA requires resolvable references; "in press" entries must be updated or the claims they support softened. [46] is load-bearing for your closest-comparator argument in §2.2 — verify it is published, or hedge the comparison. (§References [46], [47], [53].)
2. **Two tables are both numbered "Table 2"** (the "Decision outputs" table at line ~109 and the "Parametric budget sweep" table at line ~324). Renumber throughout; Table 1 also appears *after* Table 2 in §2. (§2, §6.1.)
3. **The 16% transport-emissions figure [1]** is attributed to "supply chain transportation" but the IEA source is transport-sector CO₂ generally. Tighten the attribution. (§1.1.)
4. **HBEFA reference [17] is dated 2026** with a bare `hbefa.net` URL; confirm the version (the text cites HBEFA 4.2) and give a stable citation. (§References [17]; §4.4.)
5. **"33 solves" vs "33 base-archetype solves (3 networks × 11 budgets)"** — 3 × 11 = 33 ✓, but the abstract says "all 33 solves" while §6.6 reports 1,650; a reader briefly conflates them. Add "base-archetype" at first mention in the abstract. (Abstract; §6.1.)
6. **Frankfurt rail emission factor is given as 0.057 in §5.1 but 0.040–0.075 (Uniform) in Appendix A**; reconcile the base-case value against the generated range and state which grid assumption (German vs EU-27) governs the base case. (§5.1; Appendix A.)
7. **Algorithm 1 step 3 multiplies by 1000** to get €/t, but the §3.2 formula for λ̂ returns €/kg; make the unit handling consistent between the formula box and the algorithm. (§3.2; §3.5.)
8. **"45%" budget row in Table 2 (Salamanca) reports 5 shifts then 50% reports 6**, but the MAC at 45% (2,193) uses the 40→45 step while 40% is non-binding — verify the difference base is the last *binding* solve, not the adjacent grid point, and state the convention. (§6.1.)
9. **Regime 2 (parity) never occurs in any result** across 33 base solves, 240 sensitivity cells, or 150 generated networks. Note this explicitly — an empty regime is itself a finding (the step-function rarely lands within ±10% of π) and pre-empts a "why include it?" question. (§3.3; §6.)
10. **Departure-time adjustment / EU HOS regulatory constraint** (Conclusion) is asserted with no model or citation. Either support or remove (ties to Major 3). (§8.)
11. **"co-benefit decarbonization" is used both as a regime label and as a general phenomenon** (citing Liu et al. [40]); disambiguate the defined term from the descriptive use on first occurrence. (§1; §3.3.)
12. **Table 8 lists "240 sensitivity cells"** but §6.5 says 240 cells "across Salamanca and Frankfurt" while Table 7 shows ~13 parameter rows × 6 prices × 2 networks ≈ 156; reconcile the cell count. (§6.5; Table 8.)
13. **The single-anonymized review model at SCA** means author identity is visible to reviewers; the GitHub URL `github.com/sthangavel/...` and the sole-author CRediT de-anonymize the work. That is acceptable under single-anonymized review, but confirm you are not intending double-anonymized submission. (Data Availability; CRediT.)
14. **"4–67×" vs "3.8–67×"** — the abstract says 4–67× while Finding 4 and the Conclusion say 3.8–67×. The 245 €/t / 65 = 3.77×, so 3.8× is correct; fix the abstract. (Abstract vs §6.2, §8.)
15. **NSGA-III, DEAP, scikit-learn, XGBoost** are thanked in Acknowledgements and listed in the repo but unused in the reported method; trim to what the paper actually uses (ties to Major 3). (Acknowledgements; Data Availability.)
16. **Maps/territorial note** is not relevant (no maps), but if you add a network schematic with city locations, SCA's map-boundary disclaimer policy applies. (General.)

---

## 5. Reporting-standard compliance

No EQUATOR reporting standard applies: this is an optimization/decision-analytics methods paper with synthetic and resampled instances, not a clinical, observational, or systematic-review study. The relevant community norm is computational reproducibility. General-rigor assessment:

| Dimension | Status | Note |
|---|---|---|
| Problem/model fully specified | **Pass** | MILP, objectives, constraints (C1–C4), budget map all stated (§4). |
| Method reproducible | **Pass (with caveat)** | Public repo + Appendix A parameter ranges + fixed seeds (0–49). Caveat: reported results (NSGA-III, 8.9%) not all traceable to a results section — see Major 3. |
| Baselines / comparators fair | **Partial** | Comparison tables (Tables 1, 2) are qualitative yes/no matrices, not quantitative benchmarks against a competing method on shared instances. |
| Sensitivity / ablation | **Pass** | Step-size robustness (§6.4), parameter sweep (§6.5), generated-network study (§6.6). |
| Uncertainty handling | **Partial** | No confidence intervals or seed-variance reporting on the 150-network statistics (medians given, dispersion only as range). |
| External validity stated | **Pass** | Unusually explicit (§3.4, §7.4, Table 8). |
| Code/data availability | **Pass** | MIT-licensed repo with named scripts. |

**Action:** report dispersion (IQR or seed variance) alongside the median MAC and infeasibility rates in Table 9, and add at least one quantitative head-to-head (e.g., MAC-regime recommendation vs a naïve "shift to lowest-emission mode" policy) so the comparison tables are not purely declarative.

---

## 6. Literature audit

**Field context.** MAC curves are well established in climate/energy economics and increasingly in transport policy, but their application to *network-specific freight routing* is genuinely thin — confirmed by [Ricci et al. 2025, *Future Transportation*](https://consensus.app/papers/details/759679a203cb52aaa2c1a2350721f59b/) ("a significant research gap in the freight sector, largely overlooked compared to passenger transport"), which the manuscript already cites as [36]. The step-wise/bottom-up MAC structure the paper relies on is supported by the energy-system literature ([Misconel et al., cited [35]; Tomaschek 2015](https://consensus.app/papers/details/ae2e3607687f526dbe989f65c15b9d84/); [Du et al. 2021](https://consensus.app/papers/details/c4701847f7005352b640fca35abbcfe3/)). So the *high-level* gap claim survives.

**Novelty assessment per claim.**

| Claim | Verdict | Evidence |
|---|---|---|
| Finite-difference MAC from sequential MILP solves is a novel method | **Does not survive** | [Jenkins 1982, Management Science](https://consensus.app/papers/details/5a7bbfc644095e16b293d3b4841604ad/) is RHS-parametric MILP solved at point values with a flat-region heuristic — the same technique. → Major 1. Reframe as application, not method. |
| Network-specific MAC curve → operational compliance regime taxonomy for intermodal routing | **Survives (narrowly)** | No retrieved paper produces a five-regime operational taxonomy spanning shift/parity/buy/co-benefit/infeasible from a network MAC curve. This is the defensible core. |
| Carbon price partitions a network into discontinuous decision regimes | **Not novel (paper concedes this)** | [Chen et al. 2024](https://consensus.app/papers/details/046d1d74bfcd5cbb8066d992b6e1501a/), [Yin et al. 2025](https://consensus.app/papers/details/084e0c5d9eb35f2bafb1ec58e17ee8ed/), [Noguchi 2025](https://consensus.app/papers/details/866fc0c908a459d8b58963623c5ef300/), [Mu et al. 2026](https://consensus.app/papers/details/ae8501df94a5504ca80b07a968f9d828/). Cite Chen/Yin → Major 5. |
| Domestic truck-rail MAC ≫ ETS price (allowance preferred) | **Survives as corroboration, not discovery** | Paper correctly attributes prior art ([Rekker 51], [Boehm 44], [Zakeri 49]). Honest. |

**Citation spot-checks.**
- **Noguchi [47]** — verified real and accurately characterized. [Networks and Spatial Economics 2025](https://consensus.app/papers/details/866fc0c908a459d8b58963623c5ef300/): turnpike theorems, finite threshold set where steady modal mix changes discontinuously, envelope identity (derivative of steady value w.r.t. carbon weight = steady emissions), purely theoretical with a small synthetic network, "transparent diagnostics… regime-aware planning" wording. Your §1.4 / §2.2 boundary statement is faithful. Good.
- **Ricci et al. [36]** — verified; the "freight sector largely overlooked" quote is accurate. Good.
- **Lagouvardou [52]** (single-reconfiguration maritime hub turning-point) — the manuscript's characterization is consistent with this author group's MAC/MBM work ([Lagouvardou et al. 2023, Nature Energy](https://consensus.app/papers/details/a89669132fe9503fbe23fe9e8caa62f6/)); confirm the specific [52] (Maritime Transport Research 2022) abstract matches the "transshipment-hub switch turning point" description before submission.

**New since claimed revision (consider for this version, not flagged as a miss):** [Staden et al. 2024, *IMA J. Management Mathematics*](https://consensus.app/papers/details/f6353f98264858c790fe5d92a042b339/) (intermodal cost-emissions trade-off transparency) and [Mu et al. 2026](https://consensus.app/papers/details/ae8501df94a5504ca80b07a968f9d828/) are recent enough that omission is forgivable, but both strengthen your related-work framing if added.

---

## 7. Journal-specific assessment (Supply Chain Analytics)

**7.1 Scope fit.** SCA's remit is prescriptive analytics that "compare scenarios, provide insight, and suggest alternative courses of action to supply chain managers" via optimization/ML/simulation ([Guide for Authors](https://www.sciencedirect.com/journal/supply-chain-analytics/publish/guide-for-authors)). The regime-classification decision rule is a clean fit for "prescriptive… suggest alternative courses of action." **Verdict: in scope.**

**7.2 Novelty calibration.** Named comparators: Sánchez-Pravos et al. [5] (in-journal, same dataset — your novelty floor), Mencaroni et al. [28] (parametric emission-cost, single-facility), and the broader carbon-aware routing set ([6], [7], [8], [41]). Against [5] specifically, your delta (compliance-decision layer vs assignment optimization) is real but under-stated in the abstract → Major 4. **Verdict: novelty bar met, conditional on sharpening the delta and correcting the method claim (Major 1).** This is an incremental-but-useful contribution, appropriate for SCA's tier; it is not a paradigm-level result and should not be pitched as one.

**7.3 Style match.** SCA papers are applied, managerially framed, and figure-driven. The manuscript matches in tone but is **long and argument-dense** in §1–§2 (the contribution is litigated across §1.4, §2.2, §2.3, §3.1, and §7.4 — substantial repetition of the "we don't claim a new method" disclaimer). Tighten: the same hedge appears ~6 times. SCA reviewers will prefer one crisp positioning statement.

**7.4 Required-but-missing items.**

| Item | Required by SCA / Elsevier | Present? | Action |
|---|---|---|---|
| Editable source file (.docx/.tex; PDF not accepted) | Yes | Working in .md | Convert to .docx or .tex for submission |
| Declaration of Generative AI in writing | Yes (Elsevier policy) | Not present | Add an AI-use statement; note GenAI **not** permitted for figure creation |
| Highlights (3–5, ≤85 chars) | Yes | Present (5) | Check character limits; Highlight 2 is long |
| Abstract within limit | Yes | ~330 words | Verify against SCA limit; likely needs trimming |
| CRediT statement | Yes | Present | OK |
| Declaration of Competing Interest | Yes | Present | OK |
| Data availability statement | Yes | Present (repo) | OK |
| Graphical abstract | Optional | Absent | Optional; if added, must not be AI-generated |
| Figures referenced (Fig. 2, Fig. 3) | — | Referenced, not embedded | Ensure figures are included and legible at submission |

**7.5 Alternative venues** (if Major 1/3 cannot be resolved): *Cleaner Logistics and Supply Chain* (Elsevier), *Transportation Research Part D*, or *Transportation Research Part E* — all carry network-level carbon-routing work and would accept the decision-analytics framing. SCA remains the best primary target given [5]'s presence there establishes topical fit.

---

## 8. Recommendation

**Major revision needed.**

The paper has a real, communicable contribution — a network-specific MAC curve converted into an operational five-regime carbon-compliance taxonomy — and it is written with more honesty about its own limits than most submissions. That honesty is its strongest asset and should be preserved, not sanded off. But at harsh severity, three things will draw fire from competent referees and must be fixed before submission. First, the methodological-novelty claim (Contribution 2) overreaches: RHS-parametric MILP is Jenkins (1982), and the sentence "the only auditable, transparent, solver-independent way" is not survivable as written — reframe the novelty onto the decision-analytics interpretation, where it holds (Major 1). Second, the manuscript advertises machinery (NSGA-III Pareto search, departure-time scheduling with a specific 8.9% number, the six-factor emission model) that never appears in Results; this makes the paper read as internally incomplete and is the most likely desk-stage problem — report it or cut it (Major 3). Third, the empirical claims must be matched to what three archetypes and same-distribution resampling can support: the 1,650-solve study is an internal-consistency check, and the abstract/highlights should say so (Major 2).

None of these is fatal. The design can answer the research questions it poses; the data are appropriate for a demonstration-and-mechanism contribution; there are no integrity concerns. With Major 1 reframed, Major 3 resolved one way or the other, and the related-work gap restated to survive Chen et al. (2024) and Noguchi (2025) (Major 5), this is a credible SCA paper. The delta against the in-journal Sánchez-Pravos et al. [5] needs to be unmistakable in the abstract (Major 4), because the editor will be looking for exactly that. Expect a real reviewer to converge on the same short list: fix the novelty framing, report-or-remove the orphaned results, and stop calling a within-class consistency study a robustness validation.

---

## 9. Audit log

**Manuscript:** CARMA_manuscript_v3.md, 735 lines, ~13,000 words main text, 53 references, 3 archetype networks + 150 generated, Appendix A present, no SI.
**Manuscript type:** Original research — optimization / decision-analytics methods paper (non-EQUATOR). Reviewed via general-rigor + statistical-sanity + journal-fit path.
**Severity dial:** Harsh ("Reviewer 2"), per request.
**Literature anchor:** 21 June 2026; no missing-citation flags raised for papers post-dating that date (Mu et al. 2026 and Staden et al. 2024 offered as optional additions, not deficiencies).

**Journal sources fetched.**
- SCA Guide for Authors — https://www.sciencedirect.com/journal/supply-chain-analytics/publish/guide-for-authors (scope, single-anonymized review, editable source files required, GenAI-in-figures prohibited)
- SCA scope (Elsevier Shop) — https://shop.elsevier.com/journals/supply-chain-analytics/2949-8635
- DOAJ SCA profile — https://doaj.org/toc/2949-8635

**Consensus searches (3 + journal profiling).**

| # | Query | Purpose | Key hits |
|---|---|---|---|
| 1 | marginal abatement cost curve intermodal freight routing carbon price mode shift | Field context + novelty floor | Ricci 2025 [36]; Chen 2024 (new); Du 2021; Longva 2024; Lagouvardou 2023 |
| 2 | turnpike threshold carbon-priced modal split capacity-constrained transport network | Verify Noguchi [47]; threshold prior art | Noguchi 2025 [47] verified; Yin 2025 (new); Mu 2026 (new) |
| 3 | parametric MILP sequential solve finite difference shadow price MAC integer routing | Test methodological-novelty claim | **Jenkins 1982 (decisive)**; Mukherjee 2006 [42]; Crema 1995 [39]; Kuosmanen 2021 [32] |

**Statistical sanity checks performed:** MAC arithmetic reconciled against Salamanca/Iberian/Frankfurt tables at 5%, 20%, 45→50%, and Frankfurt 25% steps — all internally consistent. Percentage/Δ columns verified against baseline. Cross-document consistency flagged: "4–67×" (abstract) vs "3.8–67×" (body) — Minor 14; duplicate "Table 2" — Minor 2; sensitivity cell count (240 vs ~156) — Minor 12.

**Coverage notes / limitations of this review.** (1) The skill's reference rubric files were not available in this environment; the review follows the SKILL.md workflow and rubric structure directly. (2) Figures 2–3 were referenced but not embedded in the manuscript file, so figure legibility/visualization-fairness could not be assessed. (3) References [46], [47], [53] carry unconfirmed DOIs; verify before submission. (4) Glenk [46] and Lagouvardou [52] abstracts were characterized from the manuscript and adjacent verified work, not independently re-fetched per-reference — confirm before relying on the §2.2 comparison wording. (5) This is a simulated review; calibrate against your own judgment and any co-author input.
