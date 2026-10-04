# H36 × G21: Forecast the abilities and effects of AI (2025-12-01 → 2025-12-08)

**Verdict:** supported
**Verdict (1b):** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode I (each agent its own objective) · N = 8 at start · 5 non-holdout active days · events inside: NE28, NE07

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2025-12-01; same day as #21,NE28): alarm **fired** on days −1..+1 (first on day -1); R1 did not fire.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | 2.29 | 0.62 | 1.16 | 0.73 |
| Z_I | 2.62 | -0.00 | 1.72 | 1.61 |
| Z_χ | 1.49 | 0.13 | 1.71 | 0.51 |
| Z_C | 2.77 | 1.72 | 0.04 | 0.09 |
| Z_act | 3.85 | -0.47 | 2.24 | 0.78 |
| Z_cont | 0.33 | 1.86 | -0.09 | 0.97 |
| R1 centroid shift | 1.97 | 1.49 | -0.17 | 0.77 |

**Placebo days in this period:** 0; alarms 0.
Non-holdout days scored: 5 of 5; mean Z_phys 1.05.

Data: `data/processed/H36-reorganization-alarm/G21/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Re-run on the fixed activity table and outage mask (DQ8), restatements removed, both embedding models (card: Round 1b). Same verdict rule as round 1.

| Score (day −1 / 0 / +1) | round 1 | 1b bge | 1b gte |
| --- | --- | --- | --- |
| Z_phys (alarm) | 2.29 / 0.62 / 1.16 | 1.60 / 0.77 / 0.65 | 1.06 / 1.01 / 1.10 |
| Z_act | 3.85 / -0.47 / 2.24 | 2.31 / 0.02 / 1.42 | 2.31 / 0.02 / 1.42 |
| Z_cont | 0.33 / 1.86 / -0.09 | 0.85 / 1.58 / 0.05 | -0.26 / 2.07 / 1.02 |
| R1 | 1.97 / 1.49 / -0.17 | 2.17 / 1.46 / -0.07 | 2.35 / 1.82 / -0.06 |

Placebo days: 0 (alarms 0 bge, 0 gte). Data: `data/processed/H36-reorganization-alarm/r1b/fixed_bge_restate/` and `.../fixed_gte_restate/`.
<!-- /R1B -->
