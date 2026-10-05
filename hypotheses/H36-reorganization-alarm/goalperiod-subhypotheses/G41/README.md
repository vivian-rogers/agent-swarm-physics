# H36 × G41: Perform novel research! (2026-05-11 → 2026-05-18)

**Verdict:** supported
**Verdict (1b):** failed
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime III · mode I (each agent its own objective) · N = 15 at start · 5 non-holdout active days · events inside: NE42b

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2026-05-11; same day as #41,NE42b): alarm **fired** on days −1..+1 (first on day +1); R1 fired.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | 0.55 | -0.67 | 2.36 | -0.01 |
| Z_I | -0.12 | 1.45 | 4.17 | 0.58 |
| Z_χ | 1.47 | -1.12 | 1.73 | -0.42 |
| Z_C | 0.28 | -2.33 | 1.18 | -0.20 |
| Z_act | 0.22 | -3.00 | 3.98 | -0.15 |
| Z_cont | 0.76 | 3.15 | 0.80 | 0.37 |
| R1 centroid shift | -0.27 | 9.02 | 0.51 | 2.29 |

**Placebo days in this period:** 0; alarms 0.
Non-holdout days scored: 5 of 5; mean Z_phys 0.46.

Data: `data/processed/H36-reorganization-alarm/G41/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Re-run on the fixed activity table and outage mask (DQ8), restatements removed, both embedding models (card: Round 1b). Same verdict rule as round 1.

| Score (day −1 / 0 / +1) | round 1 | 1b bge | 1b gte |
| --- | --- | --- | --- |
| Z_phys (alarm) | 0.55 / -0.67 / 2.36 | 1.45 / 1.79 / 1.53 | 1.94 / 1.64 / 1.61 |
| Z_act | 0.22 / -3.00 / 3.98 | 1.76 / 0.98 / 2.37 | 1.76 / 0.98 / 2.37 |
| Z_cont | 0.76 / 3.15 / 0.80 | 0.76 / 2.97 / 0.60 | 1.88 / 2.66 / 0.77 |
| R1 | -0.27 / 9.02 / 0.51 | -0.23 / 8.61 / 0.49 | -0.04 / 10.41 / 0.56 |

Placebo days: 0 (alarms 0 bge, 0 gte). Data: `data/processed/H36-reorganization-alarm/r1b/fixed_bge_restate/` and `.../fixed_gte_restate/`.
<!-- /R1B -->

## Round 2 (2026-10-05)
<!-- R2 -->
Round-2 readouts at this period's kickoff (card: Round 2; predictions P2.1–P2.3, RB1, P3.2). Role: replication (exploratory).

| Readout | bge | gte |
| --- | --- | --- |
| intraday topic-shift z, windows 0 / 1 / 2 of day 0 | 12.00 / 5.08 / 1.08 | 12.27 / 5.75 / 1.12 |
| first intraday alarm window (z ≥ 3) | 0 | 0 |
| frozen C3 score, max over days −1..+1 (alarm ≥ 2) | 7.61 | 9.41 |
| Z_act_inv (sampling-invariant activity), days −1 / 0 / +1 | 1.34 / 0.06 / -1.65 | (same) |

Data: `data/processed/H36-reorganization-alarm/r2/` (intraday_<model>.json, rob_<model>_restate/, activity_inv.parquet).
<!-- /R2 -->
