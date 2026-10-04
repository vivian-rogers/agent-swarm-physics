# H63 × G35: goal period #35 (non-holdout days)

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** 5 non-holdout days · 12 calling agents · 10 projects touched · work signals: 1 state changes (S), 3 births, 421 routine commits.

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
| herding bursts (≥ 3 agents) · matched 1–2-agent clusters | 1 · 17 |
| bursts / controls with a state change (S) in the 60 min before the follower onset | 0/1 · 0/17 |
| OR_S [95%] (Haldane) · z vs S time-shift | 11.67 [0.16, 826.06] · 0.72 |
| bursts / controls with an agent chat link in the 60 min before | 0/1 · 6/17 (OR_L 0.59) |
| OR routine commit · OR birth | 4.20 · 11.67 |
| bursts with both S and a link · S first | 0 · 0 |
| hazard h_S − h_S′ [95%] (arrivals in risk set) | -22.68 [0.00, 0.00] (30.00) |
| hazard κ − κ′ [95%] · untrimmed κ − κ′ | -1.40 [-7.29, 1.92] · -2.20 |
| hazard h_S − h_R [95%] | -22.65 [-1.55, -0.10] |

**Verdict: descriptive.** Fewer than 3 herding bursts or 5 S signals: descriptive by the rule.
Data: `data/processed/H63-bursts-start-with-work/results/periods.parquet`, `clusters_G35.parquet`.

