# CARMA Manuscript Figures — Mermaid Source

All figures for `paper/CARMA_manuscript_v2.md`.
Render with any Mermaid-compatible viewer (GitHub, Obsidian, mermaid.live).

**Inline figures (appear in manuscript body):**
- Fig. 1 → Figure 1 (six-phase pipeline) — after §5.1
- Fig. 2 → Figure 2 (DCCT dual-channel mechanism) — after §3.2
- Fig. 3 → Figure 5 (IGD ablation xychart) — after §6.6 Table 7
- Fig. 4 → Figure 7 (HOS scheduling gantt) — after §6.9 HOS table

**Supplementary figures (referenced in text, not inline):**
- Fig. S1 → Figure 3 (PIEM six-factor chain)
- Fig. S2 → Figure 6 (budget tightness sweep xychart)
- Fig. S3 → Figure 9 (contribution mindmap)

**Removed from submission (lower priority):**
- Figure 4 (Certificate-Anchored Pareto Front schematic) — conceptual diagram, content covered by Tables 4-5
- Figure 8 (quadrantChart λ* vs ETS) — covered by Table 8 and §7.0 text

---

## Figure 1 — CARMA Six-Phase Pipeline Overview

```mermaid
flowchart LR
    subgraph INPUT["INPUT"]
        R["Routes R\n(distance, weight,\ncommodity, context)"]
        B["Carbon budget B\n(kg CO₂e)"]
        CI["Grid CI profiles\n(8 EU/US regions)"]
    end

    subgraph P1["Phase 1 · PIEM"]
        PIEM["6-factor emission formula\nGrubb · COPERT · HBEFA\nEN16258 · Slope · Weather\n→ 15 ML features per route"]
    end

    subgraph P2["Phase 2 · ML Ensemble"]
        MOE["Segmented MoE\nRF + XGBoost per segment\nMAPE 1.88% overall"]
    end

    subgraph P3["Phase 3 · MILP"]
        MILP["Carbon-budget MILP\nPuLP / CBC solver\n53–91 ms"]
        OUT3["X*_MILP  certified mode assignment\nλ*  shadow price €/kg CO₂e"]
    end

    subgraph P4["Phase 4 · DCCT-NSGA-III ◀ PRIMARY"]
        CAPS["Channel 1 · CAPS\nSeed ⌊N/4⌋ individuals\nfrom X*_MILP"]
        SPRD["Channel 2 · SPRD\nAugment reference dirs\nusing λ* signal"]
        NSGA["NSGA-III evolution\nM=4 obj  N=84  G=80 gen\n4-objective Pareto search"]
        PF["PF* — 84 Pareto solutions\nCertificate-Anchored"]
    end

    subgraph P5["Phase 5 · CI Schedule"]
        CI_OPT["Departure-time optimisation\nt* = argmin E_elec(r,h)\nEU HOS filter applied"]
    end

    subgraph P6["Phase 6 · Synthesis"]
        TCH["Tchebycheff scalarisation\nw_cost=0.40  w_em=0.40\nw_time=0.10  w_rel=0.10"]
        XPREF["x*_pref — preferred solution"]
    end

    subgraph OUTPUT["OUTPUT"]
        O1["X*_MILP · λ* · PF*\nx*_pref · T* · ΔE_fleet"]
    end

    R --> P1
    P1 --> P2
    R --> P3
    P2 --> P3
    P3 --> OUT3
    OUT3 --> CAPS
    OUT3 --> SPRD
    CAPS --> NSGA
    SPRD --> NSGA
    NSGA --> PF
    CI --> CI_OPT
    PF --> CI_OPT
    PF --> TCH
    CI_OPT --> TCH
    TCH --> XPREF
    XPREF --> OUTPUT
    PF --> OUTPUT
    OUT3 --> OUTPUT

    style P4 fill:#fff3cd,stroke:#f0ad4e,stroke-width:2px
    style CAPS fill:#d4edda,stroke:#28a745
    style SPRD fill:#d4edda,stroke:#28a745
    style OUT3 fill:#cce5ff,stroke:#004085
```

---

## Figure 2 — DCCT Dual-Channel Mechanism

```mermaid
flowchart TB
    MILP["Carbon-Budget MILP\nmin Σ(c_rm + λ_ETS · e_rm)·x_rm\ns.t. Σ e_rm·x_rm ≤ B"]

    MILP -->|"Primal output\nX*_MILP = certified\nmode assignment"| CH1
    MILP -->|"Dual output\nλ* = shadow price on\ncarbon constraint C2"| CH2

    subgraph CH1["Channel 1 · CAPS"]
        direction TB
        C1A["Seed 1 individual: X*_MILP\n(certified extremal anchor)"]
        C1B["Seed ⌊N/4⌋−1 individuals:\nflip_one_gene(X*_MILP)\n(MILP neighbourhood)"]
        C1C["Seed N−⌊N/4⌋ individuals:\nrandom feasible\n(diversity)"]
        C1A --> POP["Initial population P₀\nN=84 individuals"]
        C1B --> POP
        C1C --> POP
    end

    subgraph CH2["Channel 2 · SPRD"]
        direction TB
        S1["α = min(1, λ* × 10)\n(dual-signal sensitivity)"]
        S2["p_j = (1 + α·e₂_j) / Z\n(bias toward emission-axis dirs)"]
        S3["Ref^ = Ref ∪ sample ⌈α·|Ref|⌉\n(augmented direction set)"]
        S1 --> S2 --> S3
    end

    POP --> NSGA3["NSGA-III Evolution\nG_max generations\nM=4 objectives"]
    S3 --> NSGA3

    NSGA3 --> PF["PF* — Certificate-Anchored Pareto Front\n• X*_MILP anchored at emission-minimal extreme (Theorem 1)\n• λ*-sensitive region has denser coverage (Theorem 3)\n• Best IGD across ablation variants (empirical)"]

    subgraph EC1["Economic Role of λ*"]
        E1["λ* = 0.052 €/kg (Iberian)\nλ* = 0.047 €/kg (Salamanca)\nλ* = 0.065 €/kg (Rotterdam)"]
        E2["EU ETS avg = 0.065 €/kg\n→ λ* ≤ ETS at 20% budget\n→ mode shifts self-justifying"]
        E1 --> E2
    end

    CH2 -.->|"Same λ* value\nused in both roles"| EC1

    style CH1 fill:#d4edda,stroke:#28a745,stroke-width:2px
    style CH2 fill:#cce5ff,stroke:#004085,stroke-width:2px
    style EC1 fill:#fff3cd,stroke:#f0ad4e,stroke-width:2px
    style PF fill:#f8d7da,stroke:#721c24,stroke-width:2px
```

---

## Figure 3 — PIEM Six-Factor Emission Formula

```mermaid
flowchart LR
    BASE["Base emission\nd · w · EF_m(WTW)\nkg CO₂e/tonne-km\n× distance × weight"]

    F1["F1 · Grubb Payload\n1 / (α_m + (1−α_m)·η)\nHalf-load truck: +31%"]
    F2["F2 · COPERT Speed\nFC(v_actual) / FC(v*)\nV-shape min at 80 km/h"]
    F3["F3 · Temperature\n1 + c₁·ΔT + c₂·ΔT²\n−10°C: +11.3%"]
    F4["F4 · HBEFA Congestion\n1 + A·(cong−1)^γ\ncong=2.0: non-linear penalty"]
    F5["F5 · Terrain\n1 ± k·slope\nUphill 8°: +28%\nRail downhill regen: −18.8%"]
    F6["F6 · Weather–Congestion\n1 + (f_wx−1)/√cong\nSnow @ low cong: +24.4%\nAttenuated at high cong"]

    BASE --> F1 --> F2 --> F3 --> F4 --> F5 --> F6 --> OUT["E(r,m)\nTotal emission kg CO₂e\n15 ML-ready features"]

    subgraph SOURCES["Standard sources"]
        S1["Grubb 1988"]
        S2["COPERT 5 · EEA 2019"]
        S3["EN 16258:2012"]
        S4["HBEFA 4.2 · 2022"]
        S5["HBEFA grade correction"]
        S6["HBEFA weather"]
    end

    F1 -.-> S1
    F2 -.-> S2
    F3 -.-> S3
    F4 -.-> S4
    F5 -.-> S5
    F6 -.-> S6

    style OUT fill:#d4edda,stroke:#28a745,stroke-width:2px
```

---

## Figure 4 — Certificate-Anchored Pareto Front Structure

```mermaid
flowchart TB
    subgraph PF_SPACE["4-Objective Pareto Space (schematic)"]
        direction LR
        ANCHOR["X*_MILP\nEmission-minimal anchor\n(Theorem 1: always in PF*)\nλ* = 0.052 €/kg"]

        subgraph SPRD_REGION["λ*-sensitive region\n(SPRD-dense coverage)"]
            P1_["Cost-emission\nbalanced solutions"]
            P2_["Cost-time\ntrade-offs"]
        end

        TIME_EXT["Time-minimal extreme\n(all truck/air)\nHigh cost, high emission"]
        COST_EXT["Cost-emission minimal\n(all rail/ship)\nLow cost, low emission"]

        ANCHOR --- SPRD_REGION
        SPRD_REGION --- TIME_EXT
        SPRD_REGION --- COST_EXT
    end

    subgraph IBERIAN["Iberian Network (n=12)"]
        EM_RANGE["Emission: 14,251–19,558 kg CO₂e\n−27.1% at certified extreme"]
        COST_RANGE["Cost: €100,875–139,875\n−27.9% at certified extreme"]
        TIME_RANGE["Time: 68–84 hours\nCRI: 0.12–0.28"]
    end

    subgraph ROTTERDAM["Rotterdam Hub (n=14)"]
        R_EM["Emission: 9,644–68,767 kg CO₂e\n7.1× spread"]
        R_COST["Cost: €8,545–91,258\n10.7× spread"]
        R_TIME["Time: 70.8–222.5 hours\n3.1× spread"]
    end

    PF_SPACE --> IBERIAN
    PF_SPACE --> ROTTERDAM

    style ANCHOR fill:#f8d7da,stroke:#721c24,stroke-width:2px
    style SPRD_REGION fill:#cce5ff,stroke:#004085,stroke-width:2px
```

---

## Figure 5 — Ablation Benchmark: IGD by Variant and Instance Size

```mermaid
xychart-beta
    title "IGD (lower is better) — 5 Variants × 3 Instance Sizes"
    x-axis ["MOEA/D", "NSGA3-Random", "NSGA3-CAPS", "NSGA3-SPRD", "NSGA3-DCCT"]
    y-axis "IGD (normalized to shared reference front)" 0 --> 0.35
    line [0.268, 0.125, 0.136, 0.143, 0.109]
    line [0.220, 0.258, 0.195, 0.196, 0.140]
    line [0.324, 0.290, 0.104, 0.228, 0.142]
```

*Lines: n=12 (top), n=25 (middle), n=50 (bottom). Lower IGD = better Pareto front coverage.*

---

## Figure 6 — Budget Tightness Sweep: DCCT vs Random IGD at n=12

```mermaid
xychart-beta
    title "IGD vs Carbon Budget Tightness (n=12 routes)"
    x-axis ["10% reduction", "20% reduction", "30% reduction", "40% reduction"]
    y-axis "IGD (lower is better)" 0 --> 0.22
    line [0.074, 0.094, 0.077, 0.121]
    line [0.193, 0.147, 0.090, 0.081]
```

*Line 1: NSGA3-DCCT. Line 2: NSGA3-Random. DCCT wins at 10% and 30% tightness.*

---

## Figure 7 — Dynamic CI Scheduling with EU HOS Constraint (Iberian Network)

```mermaid
gantt
    title Dynamic CI Departure Scheduling — Spain Solar Profile (Iberian Network)
    dateFormat HH:mm
    axisFormat %H:%M

    section Grid Carbon Intensity
    High CI window (morning peak)      :crit, ci_high1, 06:00, 4h
    Low CI window (solar peak)         :active, ci_low, 10:00, 4h
    Medium CI transition               :ci_med, 14:00, 4h
    High CI window (evening peak)      :crit, ci_high2, 18:00, 4h

    section Unconstrained Optimal
    Optimal departure window t*        :done, opt, 10:00, 4h
    CI saving: 421 kg CO2e per run    :milestone, 12:00, 0m

    section HOS-Constrained (EU Reg 561/2006)
    Routes under 337 km (no HOS impact):active, short, 10:00, 4h
    Routes over 337 km (HOS filter)    :hos, 10:00, 2h
    HOS break required after 4.5h      :crit, break, 14:30, 45m

    section Result
    HOS-constrained saving             :done, result, 10:00, 2h
    Net saving: 390 kg CO2e (-7.4%)   :milestone, 12:00, 0m
```

---

## Figure 8 — EU ETS Shadow Price Calibration (Economic Role of λ*)

```mermaid
quadrantChart
    title Shadow Price λ* vs EU ETS Price — Network Comparison
    x-axis "Carbon Budget Tightness" --> "Tighter"
    y-axis "λ* (€/kg CO₂e)" --> "Higher"
    quadrant-1 "Voluntary over-constraint\n(ETS subsidises shifts)"
    quadrant-2 "Tight budget, still viable"
    quadrant-3 "Loose budget\n(shifts not material)"
    quadrant-4 "Mode shifts self-justifying\n(λ* < ETS)"
    EU ETS 2024 avg (0.065): [0.50, 0.50]
    Iberian -20% (λ*=0.052): [0.40, 0.40]
    Salamanca -20% (λ*=0.047): [0.38, 0.36]
    Rotterdam -20% (λ*=0.065): [0.50, 0.50]
    Iberian -40% (est. λ*=0.10): [0.80, 0.77]
```

---

## Figure 9 — CARMA Contribution Hierarchy

```mermaid
mindmap
  root((CARMA))
    PRIMARY["PRIMARY ADVANCE"]
      λ* dual-use via DCCT
        Economic signal
          Compare vs EU ETS
          Break-even carbon price
          Auditable output
        Optimization signal
          SPRD reference dirs
          Emission-region concentration
          Theorem 3 proof
    SUPPORTING["SUPPORTING"]
      PIEM
        6-factor emission formula
        15 ML features per route
        Grubb/COPERT/HBEFA/EN16258
      Ablation study
        5 variants benchmarked
        MOEA/D vs NSGA3 family
        n=12/25/50 instances
      Dynamic CI + HOS
        8 EU/US grid profiles
        EU Reg 561/2006 compliance
        7-12% HOS reduction only
    NOT_CLAIMED["NOT CLAIMED"]
      First carbon routing paper
      Universal MOEA/D dominance
      Real telematics validation
      Full Pareto front guarantees
```
