# H36 × G30: Adopt a park and get it cleaned! (2026-02-09 → 2026-02-16)

**Verdict:** supported
**Verdict (1b):** supported (unchanged)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime I · mode C (shared objective) · N = 12 at start · 5 non-holdout active days · events inside: NE10

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2026-02-09): alarm **fired** on days −1..+1 (first on day +0); R1 did not fire.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | – | 2.86 | -0.40 | 0.79 |
| Z_I | – | 0.74 | -0.62 | 1.72 |
| Z_χ | – | 1.49 | 0.21 | 0.70 |
| Z_C | – | 6.36 | -0.80 | -0.04 |
| Z_act | – | 0.40 | -3.10 | 1.25 |
| Z_cont | – | 5.44 | 3.12 | 0.49 |
| R1 centroid shift | – | – | 1.35 | 1.93 |

**Placebo days in this period:** 0; alarms 0.
Non-holdout days scored: 5 of 5; mean Z_phys 0.89.

Data: `data/processed/H36-reorganization-alarm/G30/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Re-run on the fixed activity table and outage mask (DQ8), restatements removed, both embedding models (card: Round 1b). Same verdict rule as round 1.

| Score (day −1 / 0 / +1) | round 1 | 1b bge | 1b gte |
| --- | --- | --- | --- |
| Z_phys (alarm) | – / 2.86 / -0.40 | – / 3.79 / 2.58 | – / 3.02 / 2.82 |
| Z_act | – / 0.40 / -3.10 | – / 0.42 / 2.00 | – / 0.42 / 2.00 |
| Z_cont | – / 5.44 / 3.12 | – / 7.29 / 3.45 | – / 5.94 / 3.96 |
| R1 | – / – / 1.35 | – / – / 1.51 | – / – / 1.13 |

Placebo days: 0 (alarms 0 bge, 0 gte). Data: `data/processed/H36-reorganization-alarm/r1b/fixed_bge_restate/` and `.../fixed_gte_restate/`.
<!-- /R1B -->
