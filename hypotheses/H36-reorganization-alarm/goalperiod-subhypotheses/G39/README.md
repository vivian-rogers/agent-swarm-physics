# H36 × G39: Build your own interactive world! (2026-04-27 → 2026-05-04)

**Verdict:** supported
**Verdict (1b):** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode I (each agent its own objective) · N = 15 at start · 5 non-holdout active days

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2026-04-27): alarm **fired** on days −1..+1 (first on day -1); R1 fired.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | 2.46 | 3.51 | 0.64 | -1.00 |
| Z_I | 2.46 | 8.26 | -0.98 | -2.13 |
| Z_χ | 3.86 | 1.55 | 0.94 | -0.65 |
| Z_C | 1.07 | 0.74 | 1.96 | -0.23 |
| Z_act | 1.80 | 6.51 | -0.63 | -0.84 |
| Z_cont | 3.36 | 1.10 | 1.79 | -1.59 |
| R1 centroid shift | -0.36 | 28.82 | -0.43 | -0.87 |

**Placebo days in this period:** 0; alarms 0.
Non-holdout days scored: 5 of 5; mean Z_phys 0.47.

Data: `data/processed/H36-reorganization-alarm/G39/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Re-run on the fixed activity table and outage mask (DQ8), restatements removed, both embedding models (card: Round 1b). Same verdict rule as round 1.

| Score (day −1 / 0 / +1) | round 1 | 1b bge | 1b gte |
| --- | --- | --- | --- |
| Z_phys (alarm) | 2.46 / 3.51 / 0.64 | 1.53 / 1.88 / 0.73 | 1.16 / 1.31 / 0.30 |
| Z_act | 1.80 / 6.51 / -0.63 | 1.71 / 3.47 / -0.41 | 1.71 / 3.47 / -0.41 |
| Z_cont | 3.36 / 1.10 / 1.79 | 1.30 / 0.73 / 1.86 | 0.49 / -0.54 / 0.98 |
| R1 | -0.36 / 28.82 / -0.43 | -0.24 / 27.79 / -0.65 | 1.58 / 35.02 / -2.42 |

Placebo days: 0 (alarms 0 bge, 0 gte). Data: `data/processed/H36-reorganization-alarm/r1b/fixed_bge_restate/` and `.../fixed_gte_restate/`.
<!-- /R1B -->
