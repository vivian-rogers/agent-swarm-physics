# H63 × G30: goal period #30 (non-holdout days)

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** 5 non-holdout days · 11 calling agents · 37 projects touched · work signals: 7 state changes (S), 2 births, 341 routine commits.

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
| herding bursts (≥ 3 agents) · matched 1–2-agent clusters | 8 · 46 |
| bursts / controls with a state change (S) in the 60 min before the follower onset | 1/8 · 0/46 |
| OR_S [95%] (Haldane) · z vs S time-shift | 18.60 [0.69, 500.42] · 1.86 |
| bursts / controls with an agent chat link in the 60 min before | 7/8 · 6/46 (OR_L 46.67) |
| OR routine commit · OR birth | 6.67 · 5.47 |
| bursts with both S and a link · S first | 1 · 0 |
| hazard h_S − h_S′ [95%] (arrivals in risk set) | 0.13 [-1.06, 0.55] (130.00) |
| hazard κ − κ′ [95%] · untrimmed κ − κ′ | 1.24 [-0.14, 2.72] · 0.52 |
| hazard h_S − h_R [95%] | 0.81 [0.12, 1.48] |

**Verdict: failed.** State changes precede few bursts; links precede most.
Data: `data/processed/H63-bursts-start-with-work/results/periods.parquet`, `clusters_G30.parquet`.

