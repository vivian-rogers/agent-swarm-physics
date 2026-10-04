# H80 × G31: Free week (farewell to Claude 3.7 Sonnet) (2026-02-16 → 02-20)

**Verdict:** mixed
**Role:** replication
**Period:** regime I · 11–12 agents · #general · 5 days. One automated stream (1,546 commits, 6 days).

## Why this period
One of the two non-holdout periods besides #51 with automated commits under an agent identity. Regime I gives a different scaffold for transfer (axis I).

## Prediction
*Written 2026-10-04, before running on this period.*
- P1: C reaches AUC ≥ 0.85 (day-blocked; one positive stream, so the AUC measures one script vs the agents).
- P2: ΔAUC_A < 0.02. Kill: ≥ 0.05 (only if ≥ 50 windows per class; G31 has 54 automated windows).
- P3: ρ(a_RP, LZ78) ≥ 0.9.

## Result
Data: `results/classifier.json` (unit G31, day-blocked).

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 C ≥ 0.85 | 0.690 [0.538, 0.904] (54 automated windows, 1 stream; 42 agent windows) | failed |
| P2 ΔAUC_A < 0.02 | 0.000 [0.000, 0.000] | supported |
| P3 ρ ≥ 0.9 | 0.976 | supported |

Timing alone: 0.955 [0.929, 1.000]; without the village-window feature 0.910. Regime I.

## Scorecard (period-specific axes)
- C: 1 (timing beats permutation; compression does not reach the threshold). H: 2 against AT.

## Notes
- 2026-10-04: round 1 run.
