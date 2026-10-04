# H63 × G51: goal period #51 (non-holdout days)

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** 45 non-holdout days · 32 calling agents · 1379 projects touched · work signals: 596 state changes (S), 151 births, 45838 routine commits.

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
| herding bursts (≥ 3 agents) · matched 1–2-agent clusters | 218 · 4193 |
| bursts / controls with a state change (S) in the 60 min before the follower onset | 3/218 · 87/4193 |
| OR_S [95%] (Haldane) · z vs S time-shift | 0.66 [0.21, 2.10] · -1.96 |
| bursts / controls with an agent chat link in the 60 min before | 144/218 · 584/4193 (OR_L 12.03) |
| OR routine commit · OR birth | 2.13 · 14.55 |
| bursts with both S and a link · S first | 4 · 2 |
| hazard h_S − h_S′ [95%] (arrivals in risk set) | 0.17 [-0.11, 0.43] (3901.00) |
| hazard κ − κ′ [95%] · untrimmed κ − κ′ | 0.39 [0.29, 0.57] · 0.25 |
| hazard h_S − h_R [95%] | 0.29 [0.12, 0.41] |

**Verdict: failed.** State changes precede few bursts; links precede most.
Data: `data/processed/H63-bursts-start-with-work/results/periods.parquet`, `clusters_G51.parquet`.

