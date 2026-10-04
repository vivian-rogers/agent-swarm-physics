# H36 × G17: Each agent: build your own personal website (2025-10-13 → 2025-10-20)

**Verdict:** failed
**Verdict (1b):** failed (unchanged)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode I (each agent its own objective) · N = 7 at start · 5 non-holdout active days

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2025-10-13): alarm did not fire on days −1..+1; R1 did not fire.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | 0.21 | 0.77 | -0.66 | 0.21 |
| Z_I | 0.55 | 0.09 | -0.24 | 1.71 |
| Z_χ | 0.04 | 1.25 | -0.71 | -0.26 |
| Z_C | 0.03 | 0.96 | -1.02 | -0.83 |
| Z_act | 1.02 | -0.46 | -0.54 | 0.72 |
| Z_cont | -0.77 | 2.18 | -0.68 | 0.03 |
| R1 centroid shift | 1.03 | 0.89 | -0.69 | -0.28 |

**Placebo days in this period:** 0; alarms 0.
Non-holdout days scored: 5 of 5; mean Z_phys 0.67.

Data: `data/processed/H36-reorganization-alarm/G17/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Re-run on the fixed activity table and outage mask (DQ8), restatements removed, both embedding models (card: Round 1b). Same verdict rule as round 1.

| Score (day −1 / 0 / +1) | round 1 | 1b bge | 1b gte |
| --- | --- | --- | --- |
| Z_phys (alarm) | 0.21 / 0.77 / -0.66 | -0.19 / -0.33 / -0.41 | -0.15 / -0.51 / -0.29 |
| Z_act | 1.02 / -0.46 / -0.54 | 0.43 / -1.65 / 0.05 | 0.43 / -1.65 / 0.05 |
| Z_cont | -0.77 / 2.18 / -0.68 | -0.92 / 1.52 / -0.85 | -0.86 / 1.16 / -0.61 |
| R1 | 1.03 / 0.89 / -0.69 | 0.67 / 1.14 / -1.02 | 0.86 / 1.62 / -0.88 |

Placebo days: 0 (alarms 0 bge, 0 gte). Data: `data/processed/H36-reorganization-alarm/r1b/fixed_bge_restate/` and `.../fixed_gte_restate/`.
<!-- /R1B -->
