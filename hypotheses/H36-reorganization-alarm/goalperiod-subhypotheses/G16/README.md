# H36 × G16: Choose your own goal! (2025-10-06 → 2025-10-13)

**Verdict:** supported
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode F (free / none) · N = 7 at start · 5 non-holdout active days

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2025-10-06): alarm **fired** on days −1..+1 (first on day +0); R1 did not fire.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | – | 4.37 | -0.31 | 1.21 |
| Z_I | – | 5.21 | -0.47 | 0.85 |
| Z_χ | – | 4.63 | -0.63 | 0.26 |
| Z_C | – | 3.28 | 0.16 | 2.51 |
| Z_act | – | 7.63 | -0.02 | 0.85 |
| Z_cont | – | 0.32 | -0.75 | 1.57 |
| R1 centroid shift | – | – | 0.67 | 2.49 |

**Placebo days in this period:** 0; alarms 0.
Non-holdout days scored: 4 of 4; mean Z_phys 1.37.

Data: `data/processed/H36-reorganization-alarm/G16/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->
