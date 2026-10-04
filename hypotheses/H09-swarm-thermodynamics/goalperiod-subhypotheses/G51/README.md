# H09 × G51: memory set point across #51's roster sweep (N 25 → 32), and the homeostat

**Verdict:** n/a
**Verdict (1b):** mixed (V ignores read inflow but rises with N; the homeostat overshoots)
**Role:** native
**Period:** #51, non-holdout weeks (the tail from 09-07 is held out), regime III.

## Why this period
N grows at a fixed goal, so ledger inflow per call grows with it (elasticity 1.9 on N). That separates "memory tracks what you read" from "memory is an agent set point".

## Prediction
Written 2026-10-04 08:40 UTC (card, N2):
- within-agent elasticity of weekly median memory size on reads per call |b| < 0.1;
- on N, |b| < 0.2.

## Result (`analysis/r1b_memory.py`)
- On reads per call: 0.019 [−0.02, 0.06] (246 agent-weeks, 32 agents). **Pass.**
- On N: 0.33 [0.03, 0.64]. **Fail**, but N rises with calendar time in #51, so this is confounded with tenure.
- Homeostat (card N3, all regime-III periods; #51 dominates with 44k of 60k snapshots): median AR(1) φ −0.10. After forced resets φ is −0.22 [−0.23, −0.20], an overshoot.
