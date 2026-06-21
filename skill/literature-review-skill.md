---
name: literature-review
description: >
  Conduct a rigorous, structured academic literature review on any topic using the Consensus search tool.
  Use this skill whenever a user asks to "do a literature review", "survey the research on", "find key papers about",
  "what does the research say about", "summarize the academic literature on", or similar — even if phrased casually
  like "what do researchers know about X" or "help me understand the science of Y". Also trigger when a user is
  writing a thesis, grant proposal, systematic review, or research paper and needs to map the evidence landscape.
  Requires the Consensus MCP tool to be connected.
compatibility: "Requires Consensus MCP tool (mcp.consensus.app)"
---

# Literature Review Skill

Conduct a structured, multi-phase academic literature review using the Consensus search tool. Follow the four phases below in order.

---

## Phase 1: RECON

Run **one broad search** on the topic to orient yourself:
- Learn the dominant terminology and sub-fields
- Note any high-citation papers in the results
- Identify methodological distinctions (e.g., RCTs vs. observational, qualitative vs. quantitative)

Do not synthesize yet. Use this to inform Phase 2.

---

## Phase 2: PLAN

Choose the right framework based on the topic type:

| Framework | When to use |
|-----------|-------------|
| **PICO** (Population · Intervention · Comparison · Outcome) | Health, behavioral, educational, social science questions with a clear intervention |
| **SPIDER** (Sample · Phenomenon · Design · Evaluation · Research type) | Qualitative or lived-experience questions, no clear intervention |
| **Decomposition** (Mechanism · Applications · Limitations · Comparisons · History) | Technology, tools, or systems topics |

Break the topic into **4–5 sub-areas** using the chosen framework.

Present to the user:
- The framework chosen and why
- The 4–5 sub-areas
- A one-line rationale for each

Then ask: **"Quick scan (5 searches) or standard (10)?"** Wait for their answer before proceeding.

---

## Phase 3: SEARCH

Run searches **sequentially** — Consensus has a ~1 query/second rate limit.

**Budget allocation:**

*Quick (5 searches):* One search per sub-area.

*Standard (10 searches):*
- 5 sub-area searches (one per sub-area)
- 2 systematic review/meta-analysis searches: `"systematic review [sub-area]"` on the two most important sub-areas
- 2 era-gated searches on the most important sub-area:
  - One with `year_max: 2015` (foundational)
  - One with `year_min: 2021` (recent frontier)
- 1 follow-up on the highest-cited paper found so far

**Use filters strategically:**
- `year_min` / `year_max` for era-gating
- `human: true` for clinical/behavioral topics
- `sample_size_min` for underpowered study concerns
- `sjr_max: 1` to restrict to top-tier journals

**Track across all searches:**
- 🔁 **Repeat-hit papers** — appearing in 3+ sub-area searches → likely foundational; flag these
- 👤 **Recurring authors** — dominant research groups
- 📈 **Citations per year since publication** — identifies seminal work

---

## Phase 4: SYNTHESIZE

Output the full review in chat with these sections:

---

### Topic Overview
One tight paragraph: what the topic is, which framework was used, and the shape of the evidence landscape (where it's robust, where it's sparse).

---

### Start Here — Priority Reading Order
5–7 papers ordered for a newcomer:
1. Best recent review or meta-analysis (broadest orientation)
2. Foundational/seminal paper(s)
3. 2–3 papers at the current frontier
4. One paper highlighting a key gap or controversy

For each paper include:
- Title linked to its Consensus URL
- Authors + year
- One sentence: what it contributes
- One sentence: what to pay attention to while reading

---

### How the Field Got Here
Short narrative paragraph + a timeline table:

| Year | Milestone | Significance |
|------|-----------|--------------|

5–8 rows. Note any terminology shifts (e.g., "gut flora" → "gut microbiome") so older literature isn't missed.

---

### Sub-area Guides
One section per sub-area. Each contains:
- **What the research shows** — 2–3 sentences with inline citations
- **Key papers** — 3–5 papers (linked, with citation count + year + one sentence on why it matters); flag any 🔁 repeat-hit papers
- **Search terms** — 6–10 terms including synonyms, MeSH terms, and historical terms
- **Boolean search strings** — 2–3 ready-to-paste strings

---

### Key Research Groups
Top 3–5 recurring authors. For each:
- Affiliation
- Sub-areas they cover
- One representative paper (linked)

---

### Open Questions & Gaps
Three categories, each with a "why it matters" note:

1. **Methodological gaps** — weak designs, underpowered samples, inconsistent measures
2. **Population/context gaps** — who or what hasn't been studied
3. **Conceptual/theoretical gaps** — unreconciled contradictions, untested mechanisms, un-integrated adjacent fields

---

### Bibliography
Every cited paper, alphabetical by first author, each with a clickable Consensus URL.

---

## Rules

- **Only cite papers Consensus actually returned in this session.** If drawing on outside knowledge, label it `[not from Consensus]` and don't include it in the bibliography.
- **If a search returns very few results, say so explicitly** — don't silently fill the gap with inferences.
- **Use full Consensus URLs** — never truncated.
- **Flag repeat-hit papers** with 🔁 wherever they appear — they're likely must-reads.
- **Do not start Phase 3 until the user confirms** the scan size (quick or standard).
