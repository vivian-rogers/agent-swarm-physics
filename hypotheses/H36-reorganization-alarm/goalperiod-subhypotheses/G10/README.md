# H36 × G10: Complete as many games as you can in a week! (2025-08-18 → 2025-08-25)

**Verdict:** supported
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode I (each agent its own objective) · N = 7 at start · 5 non-holdout active days · events inside: NE27, NE03

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2025-08-18; same day as #10,NE27): alarm **fired** on days −1..+1 (first on day +0); R1 did not fire.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | – | 8.79 | 2.87 | -0.41 |
| Z_I | – | 10.71 | 4.61 | -0.29 |
| Z_χ | – | 8.25 | 3.80 | -0.33 |
| Z_C | – | 7.42 | 0.21 | -0.61 |
| Z_act | – | 12.62 | 7.29 | 0.05 |
| Z_cont | – | 4.32 | -2.43 | -0.98 |
| R1 centroid shift | – | – | -2.08 | -2.34 |

**Placebo days in this period:** 0; alarms 0.
Non-holdout days scored: 5 of 5; mean Z_phys 2.23.

Data: `data/processed/H36-reorganization-alarm/G10/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->
