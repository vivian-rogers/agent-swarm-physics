# H63 × G36: goal period #36 (non-holdout days)

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** 5 non-holdout days · 12 calling agents · 400 projects touched · work signals: 48 state changes (S), 20 births, 484 routine commits.

## Why this period
Eligible for the replication layer: goal ≥ 30 (dense git, DQ4) and ≥ 30 agent work commits.

## Prediction
*Written 2026-10-04 20:40 UTC, before running on this period; templated from the card.*
- **Supported** if OR_S > 1 with p < 0.05 (bursts vs matched non-burst clusters) **and** h_S − h_S' > 0 (state changes lead arrivals).
- **Failed** if OR_S ≤ 1 and h_S − h_S' ≤ 0. **Mixed** otherwise. **Descriptive** if < 3 herding bursts or < 5 S signals.
- Links are expected to replicate H28 (κ − κ' ≤ 0).

## Result
*Run 2026-10-04 ~20:45 UTC (trimmed window: all-present, ≥ 30 min after each agent's first call).*

| Statistic | Value |
| --- | --- |
| herding bursts (≥ 3 agents) · matched 1–2-agent clusters | 28 · 482 |
| bursts / controls with a state change (S) in the 60 min before the follower onset | 0/28 · 3/482 |
| OR_S [95%] (Haldane) · z vs S time-shift | 2.40 [0.12, 47.66] · 2.20 |
| bursts / controls with an agent chat link in the 60 min before | 9/28 · 18/482 (OR_L 12.21) |
| OR routine commit · OR birth | 3.01 · 91.04 |
| bursts with both S and a link · S first | 0 · 0 |
| hazard h_S − h_S′ [95%] (arrivals in risk set) | 0.06 [-1.70, 0.70] (349.00) |
| hazard κ − κ′ [95%] · untrimmed κ − κ′ | 0.29 [-0.77, 1.11] · 0.32 |
| hazard h_S − h_R [95%] | 0.33 [-0.97, 0.93] |

**Verdict: failed.** State changes precede few bursts; links precede most.
Data: `data/processed/H63-bursts-start-with-work/results/periods.parquet`, `clusters_G36.parquet`.

