# H63 × G44: goal period #44 (non-holdout days)

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** 4 non-holdout days · 18 calling agents · 113 projects touched · work signals: 28 state changes (S), 48 births, 1403 routine commits.

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
| herding bursts (≥ 3 agents) · matched 1–2-agent clusters | 11 · 77 |
| bursts / controls with a state change (S) in the 60 min before the follower onset | 0/11 · 3/77 |
| OR_S [95%] (Haldane) · z vs S time-shift | 0.93 [0.04, 19.11] · -0.66 |
| bursts / controls with an agent chat link in the 60 min before | 11/11 · 14/77 (OR_L 100.72) |
| OR routine commit · OR birth | 0.88 · 202.67 |
| bursts with both S and a link · S first | 0 · 0 |
| hazard h_S − h_S′ [95%] (arrivals in risk set) | 0.11 [-1.31, 2.50] (107.00) |
| hazard κ − κ′ [95%] · untrimmed κ − κ′ | 1.28 [0.88, 1.78] · 0.89 |
| hazard h_S − h_R [95%] | 1.09 [0.69, 2.01] |

**Verdict: failed.** State changes precede few bursts; links precede most.
Data: `data/processed/H63-bursts-start-with-work/results/periods.parquet`, `clusters_G44.parquet`.

