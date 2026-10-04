# H36 × G04: Write a story and celebrate it with 100 people in person (2025-05-15 → 2025-06-19)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode C (shared objective) · N = 4 at start · 25 non-holdout active days

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2025-05-15): alarm did not fire on days −1..+1; R1 did not fire.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | – | -1.83 | 1.63 | 0.18 |
| Z_I | – | -1.19 | 1.25 | -0.00 |
| Z_χ | – | -3.33 | -1.07 | 0.22 |
| Z_C | – | -0.98 | 4.71 | 0.32 |
| Z_act | – | -0.95 | 2.03 | 0.62 |
| Z_cont | – | -2.80 | 0.98 | -0.47 |
| R1 centroid shift | – | – | -0.31 | -0.44 |

**Placebo days in this period:** 14; alarms 1 (rate 0.07).
Non-holdout days scored: 25 of 25; mean Z_phys 0.21.

Data: `data/processed/H36-reorganization-alarm/G04/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->
