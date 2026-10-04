# H36 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-23)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode F (free / none) · N = 12 at start · 5 non-holdout active days · events inside: NE29, NE11

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2026-02-16): alarm did not fire on days −1..+1; R1 fired.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | 0.06 | 0.01 | -1.02 | 1.10 |
| Z_I | -0.31 | 1.09 | -0.11 | 1.11 |
| Z_χ | 0.10 | -0.73 | -1.12 | 1.17 |
| Z_C | 0.38 | -0.33 | -1.84 | 1.04 |
| Z_act | -0.46 | 0.31 | -2.03 | 2.24 |
| Z_cont | 0.62 | -0.02 | 0.63 | -0.40 |
| R1 centroid shift | 0.43 | 5.29 | 1.56 | 0.92 |

**Placebo days in this period:** 0; alarms 0.
Non-holdout days scored: 5 of 5; mean Z_phys -0.13.

Data: `data/processed/H36-reorganization-alarm/G31/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->
