# H36 × G20: Start a Substack and join the blogosphere (2025-11-17 → 2025-12-01)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode I (each agent its own objective) · N = 8 at start · 10 non-holdout active days · events inside: NE06

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2025-11-17): alarm did not fire on days −1..+1; R1 fired.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | 0.51 | 0.10 | -0.13 | -0.63 |
| Z_I | -0.50 | 0.10 | -0.36 | -0.80 |
| Z_χ | 0.75 | -0.06 | -0.00 | -1.03 |
| Z_C | 1.27 | 0.27 | -0.04 | -0.07 |
| Z_act | 0.45 | 0.57 | -0.46 | -0.35 |
| Z_cont | 0.25 | -0.52 | 0.22 | -1.07 |
| R1 centroid shift | 1.48 | 5.24 | 1.86 | -0.62 |

**Placebo days in this period:** 0; alarms 0.
Non-holdout days scored: 10 of 10; mean Z_phys 0.26.

Data: `data/processed/H36-reorganization-alarm/G20/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->
