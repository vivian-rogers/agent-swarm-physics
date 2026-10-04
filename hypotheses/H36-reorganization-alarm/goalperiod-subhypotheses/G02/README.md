# H36 × G02: Unsupervised agents look back on their previous goal and forward to their next (2025-05-10 → 2025-05-12)

**Verdict:** n/a
**Verdict (1b):** n/a (unchanged)
**Role:** replication (exploratory) (round 1, non-holdout)
**Period:** regime I · mode F (free / none) · N = 4 at start · 2 non-holdout active days

## Why this period
Every non-holdout goal period contributes its kickoff (a T-goal transition, day 0 = its first active day) and its within-period placebo days (≥ 3 active days from any catalogued event) to H36's alarm evaluation. Transitions are the object (exception c); this folder reports the period's share of the evidence.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* The card's predictions as they apply here (card: `../README.md`, incl. Amendments 0–1).

- **Kickoff:** not scored (day 0 held out, or fewer than 5 baseline days).
- **Placebo days (P7):** per-day alarm rate ≤ 0.10 [0.7].

**Period verdict rule:** supported if the kickoff window alarms and the placebo-day alarm rate is ≤ 0.10 (or there are no placebo days); mixed if the kickoff alarms but placebo FAR > 0.10; failed if the kickoff window (≥ 1 scored day) does not alarm; n/a if the kickoff is not scored.

## Result
<!-- RESULT -->
**Kickoff:** not scored (day 0 held out, or fewer than 5 baseline days).

**Placebo days in this period:** 0; alarms 0.
Non-holdout days scored: 0 of 2; mean Z_phys –.

Data: `data/processed/H36-reorganization-alarm/G02/day_stats.parquet`, `scores.parquet`.
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Re-run on the fixed activity table and outage mask (DQ8), restatements removed, both embedding models (card: Round 1b). Same verdict rule as round 1.

| Score (day −1 / 0 / +1) | round 1 | 1b bge | 1b gte |
| --- | --- | --- | --- |
| Z_phys (alarm) | – / – / – | – / – / – | – / – / – |
| Z_act | – / – / – | – / – / – | – / – / – |
| Z_cont | – / – / – | – / – / – | – / – / – |
| R1 | – / – / – | – / – / – | – / – / – |

Placebo days: 0 (alarms 0 bge, 0 gte). Data: `data/processed/H36-reorganization-alarm/r1b/fixed_bge_restate/` and `.../fixed_gte_restate/`.
<!-- /R1B -->
