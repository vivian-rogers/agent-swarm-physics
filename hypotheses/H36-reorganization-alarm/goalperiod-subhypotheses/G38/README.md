# H36 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-27)

**Verdict:** failed
**Verdict (1b):** failed (unchanged)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime III · mode C (shared objective) · N = 12 at start · 17 non-holdout active days · events inside: NE36, NE17, NE18

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2026-04-02): alarm did not fire on days −1..+1; R1 fired.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | 0.44 | -0.63 | -0.19 | -0.38 |
| Z_I | 0.57 | -0.45 | -0.45 | 0.96 |
| Z_χ | 0.38 | -0.51 | -0.07 | -0.22 |
| Z_C | 0.36 | -0.92 | -0.05 | -1.87 |
| Z_act | 0.92 | -1.28 | -0.17 | -0.58 |
| Z_cont | -0.16 | 0.30 | -0.30 | 0.34 |
| R1 centroid shift | -0.13 | 2.37 | 0.59 | 0.44 |

**Placebo days in this period:** 3; alarms 0 (rate 0.00).
Non-holdout days scored: 17 of 17; mean Z_phys -0.15.

Data: `data/processed/H36-reorganization-alarm/G38/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Re-run on the fixed activity table and outage mask (DQ8), restatements removed, both embedding models (card: Round 1b). Same verdict rule as round 1.

| Score (day −1 / 0 / +1) | round 1 | 1b bge | 1b gte |
| --- | --- | --- | --- |
| Z_phys (alarm) | 0.44 / -0.63 / -0.19 | 0.32 / -0.08 / -0.14 | 0.20 / 0.05 / -0.11 |
| Z_act | 0.92 / -1.28 / -0.17 | 0.60 / -0.36 / -0.01 | 0.60 / -0.36 / -0.01 |
| Z_cont | -0.16 / 0.30 / -0.30 | -0.18 / 0.29 / -0.31 | -0.41 / 0.57 / -0.24 |
| R1 | -0.13 / 2.37 / 0.59 | -0.13 / 2.36 / 0.58 | 0.29 / 1.75 / 0.67 |

Placebo days: 3 (alarms 0 bge, 0 gte). Data: `data/processed/H36-reorganization-alarm/r1b/fixed_bge_restate/` and `.../fixed_gte_restate/`.
<!-- /R1B -->

## Round 2 (2026-10-05)
<!-- R2 -->
Round-2 readouts at this period's kickoff (card: Round 2; predictions P2.1–P2.3, RB1, P3.2). Role: replication (exploratory).

| Readout | bge | gte |
| --- | --- | --- |
| intraday topic-shift z, windows 0 / 1 / 2 of day 0 | 6.20 / 1.09 / -0.86 | 5.22 / 0.92 / -0.35 |
| first intraday alarm window (z ≥ 3) | 0 | 0 |
| frozen C3 score, max over days −1..+1 (alarm ≥ 2) | 1.36 | 0.75 |
| Z_act_inv (sampling-invariant activity), days −1 / 0 / +1 | 1.20 / 0.25 / 0.81 | (same) |

Data: `data/processed/H36-reorganization-alarm/r2/` (intraday_<model>.json, rob_<model>_restate/, activity_inv.parquet).
<!-- /R2 -->
