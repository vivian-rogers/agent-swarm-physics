# H36 × G18: Reduce global poverty as much as you can (2025-10-20 → 2025-11-03)

**Verdict:** supported
**Verdict (1b):** supported (unchanged)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime I · mode C (shared objective) · N = 7 at start · 10 non-holdout active days

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2025-10-20): alarm **fired** on days −1..+1 (first on day +0); R1 fired.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | 0.84 | 2.80 | -0.01 | 0.13 |
| Z_I | 1.24 | 2.52 | 0.11 | 0.22 |
| Z_χ | 1.22 | 2.58 | 0.15 | 0.46 |
| Z_C | 0.05 | 3.29 | -0.28 | -0.29 |
| Z_act | 0.87 | 2.55 | -0.45 | -0.69 |
| Z_cont | 0.93 | 3.04 | 0.63 | 1.25 |
| R1 centroid shift | -0.11 | 2.26 | -0.54 | 0.21 |

**Placebo days in this period:** 0; alarms 0.
Non-holdout days scored: 10 of 10; mean Z_phys 0.55.

Data: `data/processed/H36-reorganization-alarm/G18/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Re-run on the fixed activity table and outage mask (DQ8), restatements removed, both embedding models (card: Round 1b). Same verdict rule as round 1.

| Score (day −1 / 0 / +1) | round 1 | 1b bge | 1b gte |
| --- | --- | --- | --- |
| Z_phys (alarm) | 0.84 / 2.80 / -0.01 | 0.82 / 3.10 / 0.30 | 0.61 / 2.83 / 0.05 |
| Z_act | 0.87 / 2.55 / -0.45 | 0.99 / 2.89 / 0.01 | 0.99 / 2.89 / 0.01 |
| Z_cont | 0.93 / 3.04 / 0.63 | 0.74 / 3.33 / 0.74 | 0.29 / 2.64 / 0.16 |
| R1 | -0.11 / 2.26 / -0.54 | -0.49 / 2.11 / -0.39 | -0.32 / 2.46 / -0.53 |

Placebo days: 0 (alarms 0 bge, 0 gte). Data: `data/processed/H36-reorganization-alarm/r1b/fixed_bge_restate/` and `.../fixed_gte_restate/`.
<!-- /R1B -->
