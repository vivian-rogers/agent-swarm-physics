# H36 × G24: Do random acts of kindness! (2025-12-22 → 2025-12-29)

**Verdict:** failed
**Verdict (1b):** failed (unchanged)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime I · mode C (shared objective) · N = 10 at start · 5 non-holdout active days · events inside: NE09

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2025-12-22; same day as NE09,#24): alarm did not fire on days −1..+1; R1 fired.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | -0.73 | 0.04 | -0.41 | -0.29 |
| Z_I | -0.80 | -0.40 | -0.56 | -0.28 |
| Z_χ | -0.97 | 0.01 | -0.65 | -0.20 |
| Z_C | -0.42 | 0.50 | -0.03 | -0.37 |
| Z_act | -0.78 | -0.48 | -0.37 | -0.05 |
| Z_cont | -0.69 | 0.58 | -0.52 | -0.60 |
| R1 centroid shift | -0.84 | 2.25 | -0.39 | -0.01 |

**Placebo days in this period:** 0; alarms 0.
Non-holdout days scored: 5 of 5; mean Z_phys 0.02.

Data: `data/processed/H36-reorganization-alarm/G24/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Re-run on the fixed activity table and outage mask (DQ8), restatements removed, both embedding models (card: Round 1b). Same verdict rule as round 1.

| Score (day −1 / 0 / +1) | round 1 | 1b bge | 1b gte |
| --- | --- | --- | --- |
| Z_phys (alarm) | -0.73 / 0.04 / -0.41 | -0.73 / -0.09 / -0.29 | -0.87 / -0.02 / -0.29 |
| Z_act | -0.78 / -0.48 / -0.37 | -0.63 / -0.56 / -0.15 | -0.63 / -0.56 / -0.15 |
| Z_cont | -0.69 / 0.58 / -0.52 | -0.81 / 0.44 / -0.54 | -1.13 / 0.54 / -0.55 |
| R1 | -0.84 / 2.25 / -0.39 | -0.81 / 2.38 / -0.36 | -0.94 / 2.47 / -0.35 |

Placebo days: 0 (alarms 0 bge, 0 gte). Data: `data/processed/H36-reorganization-alarm/r1b/fixed_bge_restate/` and `.../fixed_gte_restate/`.
<!-- /R1B -->

## Round 2 (2026-10-05)
<!-- R2 -->
Round-2 readouts at this period's kickoff (card: Round 2; predictions P2.1–P2.3, RB1, P3.2). Role: replication (exploratory).

| Readout | bge | gte |
| --- | --- | --- |
| intraday topic-shift z, windows 0 / 1 / 2 of day 0 | 29.89 / 18.37 / 1.62 | 43.80 / 27.63 / 1.85 |
| first intraday alarm window (z ≥ 3) | 0 | 0 |
| frozen C3 score, max over days −1..+1 (alarm ≥ 2) | 1.38 | 1.47 |
| Z_act_inv (sampling-invariant activity), days −1 / 0 / +1 | -0.48 / 0.12 / 0.29 | (same) |

Data: `data/processed/H36-reorganization-alarm/r2/` (intraday_<model>.json, rob_<model>_restate/, activity_inv.parquet).
<!-- /R2 -->
