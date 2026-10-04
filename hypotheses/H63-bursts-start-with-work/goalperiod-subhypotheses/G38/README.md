# H63 × G38: goal period #38 (non-holdout days)

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** 17 non-holdout days · 14 calling agents · 241 projects touched · work signals: 32 state changes (S), 32 births, 958 routine commits.

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
| herding bursts (≥ 3 agents) · matched 1–2-agent clusters | 10 · 354 |
| bursts / controls with a state change (S) in the 60 min before the follower onset | 0/10 · 0/354 |
| OR_S [95%] (Haldane) · z vs S time-shift | 33.76 [0.64, 1784.85] · 4.12 |
| bursts / controls with an agent chat link in the 60 min before | 7/10 · 24/354 (OR_L 32.08) |
| OR routine commit · OR birth | 0.43 · 87.00 |
| bursts with both S and a link · S first | 0 · 0 |
| hazard h_S − h_S′ [95%] (arrivals in risk set) | 0.38 [-1.19, 1.16] (269.00) |
| hazard κ − κ′ [95%] · untrimmed κ − κ′ | 0.29 [-0.59, 1.64] · -1.58 |
| hazard h_S − h_R [95%] | 0.33 [-0.76, 1.39] |

**Verdict: failed.** State changes precede few bursts; links precede most.
Data: `data/processed/H63-bursts-start-with-work/results/periods.parquet`, `clusters_G38.parquet`.

