# H36 × G04: Write a story and celebrate it with 100 people in person (2025-05-15 → 2025-06-19)

**Verdict:** failed
**Verdict (1b):** failed (unchanged)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime I · mode C (shared objective) · N = 4 at start · 25 non-holdout active days

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2025-05-15): alarm did not fire on days −1..+1; R1 did not fire.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | – | -1.83 | 1.63 | 0.18 |
| Z_I | – | -1.19 | 1.25 | -0.00 |
| Z_χ | – | -3.33 | -1.07 | 0.22 |
| Z_C | – | -0.98 | 4.71 | 0.32 |
| Z_act | – | -0.95 | 2.03 | 0.62 |
| Z_cont | – | -2.80 | 0.98 | -0.47 |
| R1 centroid shift | – | – | -0.31 | -0.44 |

**Placebo days in this period:** 14; alarms 1 (rate 0.07).
Non-holdout days scored: 25 of 25; mean Z_phys 0.21.

Data: `data/processed/H36-reorganization-alarm/G04/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Re-run on the fixed activity table and outage mask (DQ8), restatements removed, both embedding models (card: Round 1b). Same verdict rule as round 1.

| Score (day −1 / 0 / +1) | round 1 | 1b bge | 1b gte |
| --- | --- | --- | --- |
| Z_phys (alarm) | – / -1.83 / 1.63 | – / -1.09 / 0.83 | – / -1.41 / 0.93 |
| Z_act | – / -0.95 / 2.03 | – / -1.23 / 0.93 | – / -1.23 / 0.93 |
| Z_cont | – / -2.80 / 0.98 | – / -0.89 / 0.42 | – / -1.53 / 0.59 |
| R1 | – / – / -0.31 | – / – / -0.53 | – / – / -0.59 |

Placebo days: 14 (alarms 1 bge, 1 gte). Data: `data/processed/H36-reorganization-alarm/r1b/fixed_bge_restate/` and `.../fixed_gte_restate/`.
<!-- /R1B -->

## Round 2 (2026-10-05)
<!-- R2 -->
Round-2 readouts at this period's kickoff (card: Round 2; predictions P2.1–P2.3, RB1, P3.2). Role: replication (exploratory).

| Readout | bge | gte |
| --- | --- | --- |
| intraday topic-shift z, windows 0 / 1 / 2 of day 0 | -0.91 / -0.60 / -0.55 | -0.77 / -0.63 / -0.48 |
| first intraday alarm window (z ≥ 3) | none | none |
| frozen C3 score, max over days −1..+1 (alarm ≥ 2) | -0.03 | 0.01 |
| Z_act_inv (sampling-invariant activity), days −1 / 0 / +1 | – / – / – | (same) |

Data: `data/processed/H36-reorganization-alarm/r2/` (intraday_<model>.json, rob_<model>_restate/, activity_inv.parquet).
<!-- /R2 -->
