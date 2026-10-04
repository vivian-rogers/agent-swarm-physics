# H36 × G27: Hack the OWASP Juice Shop hacking playground. Compete to see which agent can complete the most challenges (2026-01-12 → 2026-01-26)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode K (competition) · N = 10 at start · 10 non-holdout active days

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2026-01-12): alarm did not fire on days −1..+1; R1 fired.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | 1.48 | 0.05 | -0.17 | 0.13 |
| Z_I | -0.22 | -0.43 | -0.45 | -0.45 |
| Z_χ | 0.10 | 0.14 | -0.09 | -0.08 |
| Z_C | 4.54 | 0.44 | 0.03 | 0.90 |
| Z_act | -0.97 | 0.03 | 0.12 | -0.29 |
| Z_cont | 4.16 | -0.08 | -0.65 | 0.49 |
| R1 centroid shift | 1.05 | 2.23 | -0.34 | -0.55 |

**Placebo days in this period:** 5; alarms 0 (rate 0.00).
Non-holdout days scored: 10 of 10; mean Z_phys 0.04.

Data: `data/processed/H36-reorganization-alarm/G27/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->
