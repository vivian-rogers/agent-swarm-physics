# H63 × G33: goal period #33 (non-holdout days)

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** 3 non-holdout days · 11 calling agents · 18 projects touched · work signals: 4 state changes (S), 7 births, 620 routine commits.

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
| herding bursts (≥ 3 agents) · matched 1–2-agent clusters | 2 · 20 |
| bursts / controls with a state change (S) in the 60 min before the follower onset | 1/2 · 0/20 |
| OR_S [95%] (Haldane) · z vs S time-shift | 41.00 [1.12, 1507.36] · 0.98 |
| bursts / controls with an agent chat link in the 60 min before | 1/2 · 3/20 (OR_L 5.67) |
| OR routine commit · OR birth | 3.00 · 19.00 |
| bursts with both S and a link · S first | 1 · 0 |
| hazard h_S − h_S′ [95%] (arrivals in risk set) | 2.00 [0.00, 2.47] (29.00) |
| hazard κ − κ′ [95%] · untrimmed κ − κ′ | 0.45 [0.11, 17.13] · -0.28 |
| hazard h_S − h_R [95%] | 2.28 [-0.00, 2.70] |

**Verdict: descriptive.** Fewer than 3 herding bursts or 5 S signals: descriptive by the rule.
Data: `data/processed/H63-bursts-start-with-work/results/periods.parquet`, `clusters_G33.parquet`.

