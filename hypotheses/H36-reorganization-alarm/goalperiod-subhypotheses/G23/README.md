# H36 × G23: Compete against each other in an online chess tournament (2025-12-15 → 2025-12-22)

**Verdict:** failed
**Verdict (1b):** failed (unchanged)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode K (competition) · N = 10 at start · 5 non-holdout active days

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2025-12-15): alarm did not fire on days −1..+1; R1 did not fire.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | – | -0.17 | -0.74 | -1.45 |
| Z_I | – | -0.66 | -0.57 | -1.64 |
| Z_χ | – | -0.25 | -1.66 | -1.72 |
| Z_C | – | 0.39 | 0.01 | -1.01 |
| Z_act | – | -0.39 | 0.65 | -1.14 |
| Z_cont | – | -0.04 | -2.54 | -1.93 |
| R1 centroid shift | – | – | -1.00 | -1.26 |

**Placebo days in this period:** 0; alarms 0.
Non-holdout days scored: 5 of 5; mean Z_phys -0.79.

Data: `data/processed/H36-reorganization-alarm/G23/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Re-run on the fixed activity table and outage mask (DQ8), restatements removed, both embedding models (card: Round 1b). Same verdict rule as round 1.

| Score (day −1 / 0 / +1) | round 1 | 1b bge | 1b gte |
| --- | --- | --- | --- |
| Z_phys (alarm) | – / -0.17 / -0.74 | – / -0.40 / -0.66 | – / -0.19 / -0.57 |
| Z_act | – / -0.39 / 0.65 | – / -0.91 / 0.82 | – / -0.91 / 0.82 |
| Z_cont | – / -0.04 / -2.54 | – / 0.16 / -2.48 | – / 0.67 / -2.37 |
| R1 | – / – / -1.00 | – / – / -0.86 | – / – / -0.88 |

Placebo days: 0 (alarms 0 bge, 0 gte). Data: `data/processed/H36-reorganization-alarm/r1b/fixed_bge_restate/` and `.../fixed_gte_restate/`.
<!-- /R1B -->
