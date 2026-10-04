# H63 × G42: goal period #42 (non-holdout days)

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** 5 non-holdout days · 16 calling agents · 34 projects touched · work signals: 46 state changes (S), 10 births, 1477 routine commits.

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
| herding bursts (≥ 3 agents) · matched 1–2-agent clusters | 0 · 61 |
| bursts / controls with a state change (S) in the 60 min before the follower onset | 0/0 · 7/61 |
| OR_S [95%] (Haldane) · z vs S time-shift | n/a [n/a, n/a] · n/a |
| bursts / controls with an agent chat link in the 60 min before | 0/0 · 7/61 (OR_L n/a) |
| OR routine commit · OR birth | n/a · n/a |
| bursts with both S and a link · S first | 0 · 0 |
| hazard h_S − h_S′ [95%] (arrivals in risk set) | 0.86 [-0.03, 3.09] (64.00) |
| hazard κ − κ′ [95%] · untrimmed κ − κ′ | 1.32 [-0.17, 3.03] · 1.04 |
| hazard h_S − h_R [95%] | 1.28 [-0.00, 3.35] |

**Verdict: descriptive.** Fewer than 3 herding bursts or 5 S signals: descriptive by the rule.
Data: `data/processed/H63-bursts-start-with-work/results/periods.parquet`, `clusters_G42.parquet`.

