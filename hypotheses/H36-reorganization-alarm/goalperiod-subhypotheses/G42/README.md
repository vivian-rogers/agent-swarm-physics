# H36 × G42: Run your own Youtube channel! (2026-05-18 → 2026-05-25)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode I (each agent its own objective) · N = 15 at start · 5 non-holdout active days

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2026-05-18): alarm did not fire on days −1..+1; R1 fired.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | -0.48 | 0.46 | -1.30 | -0.21 |
| Z_I | -0.19 | 0.79 | 0.30 | -0.28 |
| Z_χ | -1.03 | -0.09 | -1.88 | -0.97 |
| Z_C | -0.21 | 0.67 | -2.32 | 0.61 |
| Z_act | -0.45 | 1.16 | -1.54 | -0.14 |
| Z_cont | -0.41 | -0.36 | -0.44 | -0.33 |
| R1 centroid shift | 0.23 | 6.69 | 0.04 | -0.27 |

**Placebo days in this period:** 0; alarms 0.
Non-holdout days scored: 5 of 5; mean Z_phys -0.35.

Data: `data/processed/H36-reorganization-alarm/G42/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->
