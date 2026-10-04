# H80 × G41: Novel research (NE42 split back) (2026-05-11 → 05-15)

**Verdict:** supported
**Role:** replication
**Period:** regime III · 15 agents · #best / #rest · 5 days. One automated stream (858 commits on one day).

## Why this period
One of the two non-holdout periods besides #51 with automated commits under an agent identity. Regime III, same scaffold as #51, different goal.

## Prediction
*Written 2026-10-04, before running on this period.*
- P1: C reaches AUC ≥ 0.85 (day-blocked; one positive stream, so the AUC measures one script vs the agents).
- P2: ΔAUC_A < 0.02. Kill: ≥ 0.05 (only if ≥ 50 windows per class; G41 has 20 automated windows, so the kill cannot fire here).
- P3: ρ(a_RP, LZ78) ≥ 0.9.

## Result
Data: `results/classifier.json` (unit G41, window-level folds: the one automated stream committed on one day, so day-blocked folds are undefined).

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 C ≥ 0.85 | 0.958 [0.916, 0.991] (20 automated windows, 1 stream) | supported (one stream) |
| P2 ΔAUC_A < 0.02 | −0.001 [−0.005, 0.000]; kill cannot fire (< 50 automated windows) | supported |
| P3 ρ ≥ 0.9 | 0.945 | supported |

Timing alone 0.948. Window-level folds put windows of the same stream in train and test, so 0.958 measures "this script vs these agents".

## Scorecard (period-specific axes)
- C: 1. H: 2 against AT (one stream, low power).

## Notes
- 2026-10-04: round 1 run.
