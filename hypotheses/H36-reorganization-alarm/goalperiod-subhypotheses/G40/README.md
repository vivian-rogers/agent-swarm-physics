# H36 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 2026-05-11)

**Verdict:** failed
**Verdict (1b):** failed (unchanged)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime III · mode C (shared objective) · N = 15 at start · 5 non-holdout active days · events inside: NE42a

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2026-05-04; same day as #40,NE42a): alarm did not fire on days −1..+1; R1 fired.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | -0.07 | 0.84 | -0.20 | 0.42 |
| Z_I | -0.52 | 1.01 | 0.27 | -0.13 |
| Z_χ | 0.14 | 1.55 | 0.42 | 1.14 |
| Z_C | 0.17 | -0.05 | -1.28 | 0.26 |
| Z_act | 0.01 | -0.61 | -0.11 | 0.53 |
| Z_cont | -0.33 | 2.83 | -0.16 | 0.10 |
| R1 centroid shift | -0.88 | 5.17 | 0.02 | -0.50 |

**Placebo days in this period:** 0; alarms 0.
Non-holdout days scored: 5 of 5; mean Z_phys 0.40.

Data: `data/processed/H36-reorganization-alarm/G40/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Re-run on the fixed activity table and outage mask (DQ8), restatements removed, both embedding models (card: Round 1b). Same verdict rule as round 1.

| Score (day −1 / 0 / +1) | round 1 | 1b bge | 1b gte |
| --- | --- | --- | --- |
| Z_phys (alarm) | -0.07 / 0.84 / -0.20 | -0.62 / 1.55 / 0.14 | -0.87 / 1.33 / 0.14 |
| Z_act | 0.01 / -0.61 / -0.11 | -0.85 / 0.56 / 0.12 | -0.85 / 0.56 / 0.12 |
| Z_cont | -0.33 / 2.83 / -0.16 | -0.53 / 2.98 / 0.19 | -1.02 / 2.69 / 0.23 |
| R1 | -0.88 / 5.17 / 0.02 | -0.80 / 3.88 / -0.15 | -1.39 / 1.93 / -0.74 |

Placebo days: 0 (alarms 0 bge, 0 gte). Data: `data/processed/H36-reorganization-alarm/r1b/fixed_bge_restate/` and `.../fixed_gte_restate/`.
<!-- /R1B -->

## Round 2 (2026-10-05)
<!-- R2 -->
Round-2 readouts at this period's kickoff (card: Round 2; predictions P2.1–P2.3, RB1, P3.2). Role: replication (exploratory).

| Readout | bge | gte |
| --- | --- | --- |
| intraday topic-shift z, windows 0 / 1 / 2 of day 0 | 6.87 / 1.42 / 0.26 | 10.12 / 1.37 / 0.37 |
| first intraday alarm window (z ≥ 3) | 0 | 0 |
| frozen C3 score, max over days −1..+1 (alarm ≥ 2) | 2.88 | 2.77 |
| Z_act_inv (sampling-invariant activity), days −1 / 0 / +1 | 0.91 / 0.74 / 0.50 | (same) |

Data: `data/processed/H36-reorganization-alarm/r2/` (intraday_<model>.json, rob_<model>_restate/, activity_inv.parquet).
<!-- /R2 -->
