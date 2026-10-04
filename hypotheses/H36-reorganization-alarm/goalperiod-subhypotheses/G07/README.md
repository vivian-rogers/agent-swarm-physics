# H36 × G07: Holiday: do whatever you prefer! Next goal will begin soon (2025-07-16 → 2025-07-18)

**Verdict:** failed
**Verdict (1b):** supported (bge) / failed (gte)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime I · mode F (free / none) · N = 4 at start · 2 non-holdout active days

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2025-07-16): alarm did not fire on days −1..+1; R1 fired.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | – | 1.86 | 1.18 | 6.54 |
| Z_I | – | 1.86 | 0.83 | 13.25 |
| Z_χ | – | 3.52 | 0.84 | 7.17 |
| Z_C | – | 0.20 | 1.87 | -0.80 |
| Z_act | – | 0.14 | -0.01 | 11.22 |
| Z_cont | – | 4.16 | 2.65 | 2.54 |
| R1 centroid shift | – | 2.65 | -1.01 | 5.50 |

**Placebo days in this period:** 0; alarms 0.
Non-holdout days scored: 2 of 2; mean Z_phys 1.52.

Data: `data/processed/H36-reorganization-alarm/G07/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Re-run on the fixed activity table and outage mask (DQ8), restatements removed, both embedding models (card: Round 1b). Same verdict rule as round 1.

| Score (day −1 / 0 / +1) | round 1 | 1b bge | 1b gte |
| --- | --- | --- | --- |
| Z_phys (alarm) | – / 1.86 / 1.18 | -0.02 / 1.58 / 2.00 | 0.02 / 1.17 / 1.17 |
| Z_act | – / 0.14 / -0.01 | 0.23 / -0.09 / 0.06 | 0.23 / -0.09 / 0.06 |
| Z_cont | – / 4.16 / 2.65 | -0.50 / 3.80 / 4.31 | -0.38 / 3.00 / 2.48 |
| R1 | – / 2.65 / -1.01 | -0.53 / 3.27 / -0.19 | -0.60 / 3.53 / -1.00 |

Placebo days: 0 (alarms 0 bge, 0 gte). Data: `data/processed/H36-reorganization-alarm/r1b/fixed_bge_restate/` and `.../fixed_gte_restate/`.
<!-- /R1B -->
