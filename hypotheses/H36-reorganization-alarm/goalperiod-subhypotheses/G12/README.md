# H36 × G12: Form two teams and debate each other, while one agent judges. Choose your teammates wisely! (2025-09-01 → 2025-09-08)

**Verdict:** supported
**Verdict (1b):** supported (unchanged)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime I · mode M (mixed) · N = 7 at start · 5 non-holdout active days · events inside: NE04

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2025-09-01): alarm **fired** on days −1..+1 (first on day -1); R1 fired.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | 2.59 | 1.53 | 0.93 | 0.48 |
| Z_I | 1.65 | 1.34 | 0.92 | 0.30 |
| Z_χ | 2.61 | 1.69 | 1.13 | 0.55 |
| Z_C | 3.50 | 1.57 | 0.76 | 0.60 |
| Z_act | -0.19 | 0.16 | 0.33 | -0.11 |
| Z_cont | 5.98 | 3.30 | 1.73 | 1.21 |
| R1 centroid shift | 1.62 | 3.58 | -0.03 | -0.13 |

**Placebo days in this period:** 0; alarms 0.
Non-holdout days scored: 5 of 5; mean Z_phys 0.48.

Data: `data/processed/H36-reorganization-alarm/G12/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Re-run on the fixed activity table and outage mask (DQ8), restatements removed, both embedding models (card: Round 1b). Same verdict rule as round 1.

| Score (day −1 / 0 / +1) | round 1 | 1b bge | 1b gte |
| --- | --- | --- | --- |
| Z_phys (alarm) | 2.59 / 1.53 / 0.93 | 2.70 / 1.59 / 0.86 | 3.75 / 1.31 / 0.76 |
| Z_act | -0.19 / 0.16 / 0.33 | -0.10 / 0.11 / 0.25 | -0.10 / 0.11 / 0.25 |
| Z_cont | 5.98 / 3.30 / 1.73 | 6.06 / 3.55 / 1.65 | 8.14 / 2.97 / 1.42 |
| R1 | 1.62 / 3.58 / -0.03 | 1.38 / 4.08 / -0.00 | 1.53 / 3.87 / -0.09 |

Placebo days: 0 (alarms 0 bge, 0 gte). Data: `data/processed/H36-reorganization-alarm/r1b/fixed_bge_restate/` and `.../fixed_gte_restate/`.
<!-- /R1B -->
