# H36 × G25: Create a digital museum of 2025 (2025-12-29 → 2026-01-05)

**Verdict:** failed
**Verdict (1b):** failed (unchanged)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime I · mode C (shared objective) · N = 10 at start · 5 non-holdout active days

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2025-12-29): alarm did not fire on days −1..+1; R1 fired.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | 1.00 | 0.58 | 1.17 | 0.56 |
| Z_I | 1.47 | 1.06 | 1.49 | 0.14 |
| Z_χ | 1.75 | 0.81 | 1.47 | 1.22 |
| Z_C | -0.21 | -0.12 | 0.53 | 0.31 |
| Z_act | 0.12 | -0.36 | 0.99 | 0.80 |
| Z_cont | 2.34 | 2.00 | 1.51 | 0.09 |
| R1 centroid shift | 3.48 | 3.16 | 0.24 | 0.55 |

**Placebo days in this period:** 0; alarms 0.
Non-holdout days scored: 5 of 5; mean Z_phys 0.61.

Data: `data/processed/H36-reorganization-alarm/G25/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Re-run on the fixed activity table and outage mask (DQ8), restatements removed, both embedding models (card: Round 1b). Same verdict rule as round 1.

| Score (day −1 / 0 / +1) | round 1 | 1b bge | 1b gte |
| --- | --- | --- | --- |
| Z_phys (alarm) | 1.00 / 0.58 / 1.17 | 1.01 / 1.04 / 1.86 | 1.07 / 0.74 / 1.99 |
| Z_act | 0.12 / -0.36 / 0.99 | 0.08 / 0.21 / 2.23 | 0.08 / 0.21 / 2.23 |
| Z_cont | 2.34 / 2.00 / 1.51 | 2.37 / 2.30 / 1.44 | 2.43 / 1.61 / 1.78 |
| R1 | 3.48 / 3.16 / 0.24 | 4.12 / 3.20 / 0.23 | 4.14 / 2.89 / 0.27 |

Placebo days: 0 (alarms 0 bge, 0 gte). Data: `data/processed/H36-reorganization-alarm/r1b/fixed_bge_restate/` and `.../fixed_gte_restate/`.
<!-- /R1B -->

## Round 2 (2026-10-05)
<!-- R2 -->
Round-2 readouts at this period's kickoff (card: Round 2; predictions P2.1–P2.3, RB1, P3.2). Role: replication (exploratory).

| Readout | bge | gte |
| --- | --- | --- |
| intraday topic-shift z, windows 0 / 1 / 2 of day 0 | 3.90 / 2.39 / 0.41 | 3.67 / 2.32 / 0.05 |
| first intraday alarm window (z ≥ 3) | 0 | 0 |
| frozen C3 score, max over days −1..+1 (alarm ≥ 2) | 3.12 | 3.14 |
| Z_act_inv (sampling-invariant activity), days −1 / 0 / +1 | -0.37 / -0.73 / 3.03 | (same) |

Data: `data/processed/H36-reorganization-alarm/r2/` (intraday_<model>.json, rob_<model>_restate/, activity_inv.parquet).
<!-- /R2 -->
