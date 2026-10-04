# H36 × G06: Create your own merch store. Whichever agent's store makes the most profit wins! (2025-06-26 → 2025-07-16)

**Verdict:** failed
**Verdict (1b):** failed (unchanged)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime I · mode K (competition) · N = 4 at start · 15 non-holdout active days · events inside: NE02

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2025-06-26): alarm did not fire on days −1..+1; R1 fired.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | 0.96 | 0.28 | -0.96 | 1.32 |
| Z_I | 0.74 | -0.47 | -1.55 | 2.32 |
| Z_χ | 0.40 | -0.02 | -0.98 | 1.65 |
| Z_C | 1.76 | 1.32 | -0.34 | -0.01 |
| Z_act | 0.86 | 0.27 | -0.82 | 2.05 |
| Z_cont | 1.03 | 0.04 | -1.33 | 0.68 |
| R1 centroid shift | -0.10 | 2.84 | -1.00 | 0.82 |

**Placebo days in this period:** 5; alarms 0 (rate 0.00).
Non-holdout days scored: 13 of 13; mean Z_phys -0.18.

Data: `data/processed/H36-reorganization-alarm/G06/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Re-run on the fixed activity table and outage mask (DQ8), restatements removed, both embedding models (card: Round 1b). Same verdict rule as round 1.

| Score (day −1 / 0 / +1) | round 1 | 1b bge | 1b gte |
| --- | --- | --- | --- |
| Z_phys (alarm) | 0.96 / 0.28 / -0.96 | 0.64 / 0.67 / -0.96 | 0.54 / 0.56 / -0.87 |
| Z_act | 0.86 / 0.27 / -0.82 | -0.01 / 0.85 / -0.81 | -0.01 / 0.85 / -0.81 |
| Z_cont | 1.03 / 0.04 / -1.33 | 1.16 / 0.26 / -1.29 | 1.06 / 0.09 / -1.01 |
| R1 | -0.10 / 2.84 / -1.00 | -0.12 / 2.71 / -0.92 | -0.26 / 4.26 / -1.33 |

Placebo days: 4 (alarms 0 bge, 0 gte). Data: `data/processed/H36-reorganization-alarm/r1b/fixed_bge_restate/` and `.../fixed_gte_restate/`.
<!-- /R1B -->
