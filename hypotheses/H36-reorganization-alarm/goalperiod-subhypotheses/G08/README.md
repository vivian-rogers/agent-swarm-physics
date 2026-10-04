# H36 × G08: Design the AI Village benchmark for open-ended goal pursuit – and test yourselves on it! (2025-07-18 → 2025-08-13)

**Verdict:** supported
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode C (shared objective) · N = 4 at start · 18 non-holdout active days

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2025-07-18): alarm **fired** on days −1..+1 (first on day +0); R1 fired.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | 1.18 | 6.54 | 0.08 | 0.34 |
| Z_I | 0.83 | 13.25 | 0.13 | 0.79 |
| Z_χ | 0.84 | 7.17 | 0.42 | 0.47 |
| Z_C | 1.87 | -0.80 | -0.31 | -0.25 |
| Z_act | -0.01 | 11.22 | -0.13 | 0.33 |
| Z_cont | 2.65 | 2.54 | 0.38 | 0.50 |
| R1 centroid shift | -1.01 | 5.50 | 0.80 | -0.43 |

**Placebo days in this period:** 13; alarms 1 (rate 0.08).
Non-holdout days scored: 18 of 18; mean Z_phys 0.57.

Data: `data/processed/H36-reorganization-alarm/G08/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->
