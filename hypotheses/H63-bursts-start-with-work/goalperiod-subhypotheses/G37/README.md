# H63 × G37: goal period #37 (non-holdout days)

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** 3 non-holdout days · 12 calling agents · 79 projects touched · work signals: 2 state changes (S), 3 births, 176 routine commits.

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
| herding bursts (≥ 3 agents) · matched 1–2-agent clusters | 3 · 90 |
| bursts / controls with a state change (S) in the 60 min before the follower onset | 0/3 · 0/90 |
| OR_S [95%] (Haldane) · z vs S time-shift | 25.86 [0.44, 1503.27] · 0.74 |
| bursts / controls with an agent chat link in the 60 min before | 2/3 · 5/90 (OR_L 34.00) |
| OR routine commit · OR birth | 3.25 · 8.52 |
| bursts with both S and a link · S first | 0 · 0 |
| hazard h_S − h_S′ [95%] (arrivals in risk set) | 0.82 [-19.50, 1.32] (85.00) |
| hazard κ − κ′ [95%] · untrimmed κ − κ′ | -0.22 [-1.03, 0.46] · -0.30 |
| hazard h_S − h_R [95%] | 1.29 [-19.23, 1.58] |

**Verdict: descriptive.** Fewer than 3 herding bursts or 5 S signals: descriptive by the rule.
Data: `data/processed/H63-bursts-start-with-work/results/periods.parquet`, `clusters_G37.parquet`.

