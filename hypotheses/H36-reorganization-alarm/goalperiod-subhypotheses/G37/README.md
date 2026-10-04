# H36 × G37: Pick your own goal! (2026-03-30 → 2026-04-02)

**Verdict:** failed
**Verdict (1b):** failed (unchanged)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime III · mode F (free / none) · N = 13 at start · 3 non-holdout active days

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff (P1):** no physics alarm (Z_phys < 2.0 on days −1, 0, +1) [0.65]; if one fires, on day 0 or +1, not day −1 (P8) [0.7]. R1 (content centroid shift) z ≥ 2 on day 0 or +1 [0.6].
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff** (day 0 = 2026-03-30): alarm did not fire on days −1..+1; R1 fired.

| Score | day −1 | day 0 | day +1 | day +2 |
| --- | --- | --- | --- | --- |
| Z_phys (alarm) | -1.29 | 0.06 | 0.33 | 0.44 |
| Z_I | 0.08 | -0.56 | 0.48 | 0.57 |
| Z_χ | -1.72 | -0.30 | 0.38 | 0.38 |
| Z_C | -2.24 | 1.04 | 0.12 | 0.36 |
| Z_act | -1.00 | -0.30 | 0.90 | 0.92 |
| Z_cont | -1.23 | 0.34 | -0.38 | -0.16 |
| R1 centroid shift | 0.48 | 2.56 | 1.33 | -0.13 |

**Placebo days in this period:** 0; alarms 0.
Non-holdout days scored: 3 of 3; mean Z_phys 0.28.

Data: `data/processed/H36-reorganization-alarm/G37/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Re-run on the fixed activity table and outage mask (DQ8), restatements removed, both embedding models (card: Round 1b). Same verdict rule as round 1.

| Score (day −1 / 0 / +1) | round 1 | 1b bge | 1b gte |
| --- | --- | --- | --- |
| Z_phys (alarm) | -1.29 / 0.06 / 0.33 | -0.85 / 0.10 / 0.14 | -0.79 / -0.20 / 0.04 |
| Z_act | -1.00 / -0.30 / 0.90 | -0.50 / -0.24 / 0.53 | -0.50 / -0.24 / 0.53 |
| Z_cont | -1.23 / 0.34 / -0.38 | -1.36 / 0.35 / -0.36 | -1.23 / -0.26 / -0.58 |
| R1 | 0.48 / 2.56 / 1.33 | 0.47 / 2.55 / 1.36 | 0.49 / 3.28 / 1.88 |

Placebo days: 0 (alarms 0 bge, 0 gte). Data: `data/processed/H36-reorganization-alarm/r1b/fixed_bge_restate/` and `.../fixed_gte_restate/`.
<!-- /R1B -->
