# H36 × G13: Design, run and write up a human subjects experiment (2025-09-08 → 2025-09-22)

**Verdict:** failed
**Verdict (1b):** failed (unchanged)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime I · mode C (shared objective) · N = 6 at start · 10 non-holdout active days

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2025-09-08): alarm did not fire on days −1..+1; R1 fired.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | -0.25 | -0.26 | -1.00 | -1.42 |
| Z_I | -0.44 | 0.12 | -0.82 | -1.57 |
| Z_χ | -0.11 | -0.68 | -1.12 | -1.42 |
| Z_C | -0.19 | -0.21 | -1.06 | -1.26 |
| Z_act | -0.18 | -0.42 | -0.93 | -1.52 |
| Z_cont | -0.40 | 0.09 | -1.03 | -1.33 |
| R1 centroid shift | 3.76 | 1.04 | -0.34 | -0.51 |

**Placebo days in this period:** 5; alarms 0 (rate 0.00).
Non-holdout days scored: 10 of 10; mean Z_phys -0.39.

Data: `data/processed/H36-reorganization-alarm/G13/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Re-run on the fixed activity table and outage mask (DQ8), restatements removed, both embedding models (card: Round 1b). Same verdict rule as round 1.

| Score (day −1 / 0 / +1) | round 1 | 1b bge | 1b gte |
| --- | --- | --- | --- |
| Z_phys (alarm) | -0.25 / -0.26 / -1.00 | -0.82 / -0.13 / -0.74 | -0.78 / -0.39 / -0.75 |
| Z_act | -0.18 / -0.42 / -0.93 | -0.99 / -0.51 / -0.49 | -0.99 / -0.51 / -0.49 |
| Z_cont | -0.40 / 0.09 / -1.03 | -0.54 / 0.26 / -1.01 | -0.46 / -0.29 / -1.02 |
| R1 | 3.76 / 1.04 / -0.34 | 4.74 / 1.01 / -0.36 | 3.78 / 1.33 / -0.24 |

Placebo days: 5 (alarms 0 bge, 0 gte). Data: `data/processed/H36-reorganization-alarm/r1b/fixed_bge_restate/` and `.../fixed_gte_restate/`.
<!-- /R1B -->

## Round 2 (2026-10-05)
<!-- R2 -->
Round-2 readouts at this period's kickoff (card: Round 2; predictions P2.1–P2.3, RB1, P3.2). Role: replication (exploratory).

| Readout | bge | gte |
| --- | --- | --- |
| intraday topic-shift z, windows 0 / 1 / 2 of day 0 | 2.01 / 0.94 / -0.39 | 2.42 / 1.73 / -0.06 |
| first intraday alarm window (z ≥ 3) | none | none |
| frozen C3 score, max over days −1..+1 (alarm ≥ 2) | 3.74 | 2.78 |
| Z_act_inv (sampling-invariant activity), days −1 / 0 / +1 | -0.67 / -0.71 / – | (same) |

Data: `data/processed/H36-reorganization-alarm/r2/` (intraday_<model>.json, rob_<model>_restate/, activity_inv.parquet).
<!-- /R2 -->
