# H36 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-20)

**Verdict:** failed
**Verdict (1b):** failed (unchanged)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime III · mode I/K (?) · N = 21 at start · 45 non-holdout active days · events inside: NE32, NE-side-room, NE38, NE-focus, NE33

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2026-07-06): alarm did not fire on days −1..+1; R1 did not fire.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | – | 1.95 | -0.24 | 0.32 |
| Z_I | – | 1.45 | -0.38 | -0.31 |
| Z_χ | – | 2.02 | -0.32 | 0.32 |
| Z_C | – | 2.36 | -0.02 | 0.96 |
| Z_act | – | 2.05 | -0.10 | 0.13 |
| Z_cont | – | 1.65 | -0.48 | 0.36 |
| R1 centroid shift | – | – | 0.21 | 0.09 |

**Placebo days in this period:** 12; alarms 0 (rate 0.00).
Non-holdout days scored: 45 of 45; mean Z_phys 0.19.

Data: `data/processed/H36-reorganization-alarm/G51/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Re-run on the fixed activity table and outage mask (DQ8), restatements removed, both embedding models (card: Round 1b). Same verdict rule as round 1.

| Score (day −1 / 0 / +1) | round 1 | 1b bge | 1b gte |
| --- | --- | --- | --- |
| Z_phys (alarm) | – / 1.95 / -0.24 | – / 1.43 / -0.01 | – / 1.18 / -0.00 |
| Z_act | – / 2.05 / -0.10 | – / 0.86 / 0.28 | – / 0.86 / 0.28 |
| Z_cont | – / 1.65 / -0.48 | – / 1.81 / -0.40 | – / 1.30 / -0.36 |
| R1 | – / – / 0.21 | – / – / 0.17 | – / – / -0.11 |

Placebo days: 7 (alarms 0 bge, 0 gte). Data: `data/processed/H36-reorganization-alarm/r1b/fixed_bge_restate/` and `.../fixed_gte_restate/`.
<!-- /R1B -->

## Round 2 (2026-10-05)
<!-- R2 -->
Round-2 readouts at this period's kickoff (card: Round 2; predictions P2.1–P2.3, RB1, P3.2). Role: replication (exploratory).

| Readout | bge | gte |
| --- | --- | --- |
| intraday topic-shift z, windows 0 / 1 / 2 of day 0 | 13.10 / 5.70 / 0.70 | 10.15 / 5.12 / 0.40 |
| first intraday alarm window (z ≥ 3) | 0 | 0 |
| frozen C3 score, max over days −1..+1 (alarm ≥ 2) | 1.82 | 1.36 |
| Z_act_inv (sampling-invariant activity), days −1 / 0 / +1 | – / -0.32 / – | (same) |

Data: `data/processed/H36-reorganization-alarm/r2/` (intraday_<model>.json, rob_<model>_restate/, activity_inv.parquet).
<!-- /R2 -->
