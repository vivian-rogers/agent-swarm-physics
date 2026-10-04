# H36 × G19: Create a popular daily puzzle game like Wordle (2025-11-03 → 2025-11-17)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
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
**Kickoff** (day 0 = 2025-11-03): alarm did not fire on days −1..+1; R1 did not fire.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | 0.17 | -0.10 | 0.68 | 0.54 |
| Z_I | 0.17 | 0.11 | 0.90 | 1.10 |
| Z_χ | 0.28 | -0.28 | 0.91 | -0.18 |
| Z_C | 0.07 | -0.13 | 0.22 | 0.70 |
| Z_act | 0.24 | -0.79 | 0.56 | 0.86 |
| Z_cont | 0.09 | 0.90 | 0.91 | 0.31 |
| R1 centroid shift | -0.33 | 0.56 | -0.08 | -1.42 |

**Placebo days in this period:** 4; alarms 0 (rate 0.00).
Non-holdout days scored: 10 of 10; mean Z_phys 0.06.

Data: `data/processed/H36-reorganization-alarm/G19/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->
