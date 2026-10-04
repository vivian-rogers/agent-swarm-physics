# H36 × G36: Interact with other AI agents outside the Village! (2026-03-23 → 2026-03-30)

**Verdict:** failed
**Verdict (1b):** failed (unchanged)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime II · mode C (shared objective) · N = 13 at start · 5 non-holdout active days · events inside: NE14b, NE16

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2026-03-23): alarm did not fire on days −1..+1; R1 fired.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | 0.23 | 0.31 | -0.78 | -0.76 |
| Z_I | -0.27 | -0.09 | -1.56 | -0.55 |
| Z_χ | 0.64 | 0.49 | -1.43 | -0.94 |
| Z_C | 0.32 | 0.52 | 0.64 | -0.78 |
| Z_act | 0.62 | -0.11 | -0.36 | 0.14 |
| Z_cont | -0.45 | 0.73 | -1.60 | -1.89 |
| R1 centroid shift | -1.03 | 5.79 | 0.39 | -0.17 |

**Placebo days in this period:** 0; alarms 0.
Non-holdout days scored: 5 of 5; mean Z_phys -0.59.

Data: `data/processed/H36-reorganization-alarm/G36/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Re-run on the fixed activity table and outage mask (DQ8), restatements removed, both embedding models (card: Round 1b). Same verdict rule as round 1.

| Score (day −1 / 0 / +1) | round 1 | 1b bge | 1b gte |
| --- | --- | --- | --- |
| Z_phys (alarm) | 0.23 / 0.31 / -0.78 | 0.14 / 0.19 / -0.96 | 0.19 / 0.07 / -1.02 |
| Z_act | 0.62 / -0.11 / -0.36 | 0.50 / -0.29 / -0.68 | 0.50 / -0.29 / -0.68 |
| Z_cont | -0.45 / 0.73 / -1.60 | -0.45 / 0.73 / -1.45 | -0.33 / 0.49 / -1.61 |
| R1 | -1.03 / 5.79 / 0.39 | -1.05 / 5.72 / 0.39 | -0.88 / 7.65 / 0.48 |

Placebo days: 0 (alarms 0 bge, 0 gte). Data: `data/processed/H36-reorganization-alarm/r1b/fixed_bge_restate/` and `.../fixed_gte_restate/`.
<!-- /R1B -->
