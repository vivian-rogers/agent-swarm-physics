# H63 × G41: goal period #41 (non-holdout days)

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** 5 non-holdout days · 15 calling agents · 67 projects touched · work signals: 65 state changes (S), 17 births, 1768 routine commits.

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
| herding bursts (≥ 3 agents) · matched 1–2-agent clusters | 9 · 97 |
| bursts / controls with a state change (S) in the 60 min before the follower onset | 3/9 · 6/97 |
| OR_S [95%] (Haldane) · z vs S time-shift | 7.58 [1.51, 38.07] · 2.46 |
| bursts / controls with an agent chat link in the 60 min before | 4/9 · 18/97 (OR_L 3.51) |
| OR routine commit · OR birth | 0.48 · 9.20 |
| bursts with both S and a link · S first | 3 · 1 |
| hazard h_S − h_S′ [95%] (arrivals in risk set) | -0.20 [-1.64, 0.35] (146.00) |
| hazard κ − κ′ [95%] · untrimmed κ − κ′ | -0.06 [-0.31, 0.17] · -0.30 |
| hazard h_S − h_R [95%] | 0.17 [-0.28, 0.69] |

**Verdict: mixed.** State changes precede few bursts; links precede most.
Data: `data/processed/H63-bursts-start-with-work/results/periods.parquet`, `clusters_G41.parquet`.

