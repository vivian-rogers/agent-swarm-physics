# H36 × G44: Finetune your leader! (2026-05-26 → 2026-06-01)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode C (shared objective) · N = 16 at start · 4 non-holdout active days · events inside: NE31

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2026-05-26; same day as #44,NE31): alarm did not fire on days −1..+1; R1 did not fire.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | – | -0.06 | -0.96 | 1.41 |
| Z_I | – | 0.34 | -0.38 | 1.66 |
| Z_χ | – | 0.05 | -0.06 | 2.15 |
| Z_C | – | -0.56 | -2.46 | 0.43 |
| Z_act | – | 0.25 | -0.39 | 1.89 |
| Z_cont | – | -0.34 | -1.54 | 0.87 |
| R1 centroid shift | – | – | 0.06 | 1.00 |

**Placebo days in this period:** 0; alarms 0.
Non-holdout days scored: 4 of 4; mean Z_phys 0.90.

Data: `data/processed/H36-reorganization-alarm/G44/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->
