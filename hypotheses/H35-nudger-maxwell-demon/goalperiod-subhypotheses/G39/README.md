# H35 × G39: Build your own interactive world (2026-04-27 → 2026-05-01)

**Verdict:** descriptive
**Role:** replication (exploratory) (round 1, non-holdout); exploratory (descriptive)
**Verdict (1b):** descriptive (< 6 strictly isolated first nudges; 2026-10-04)
**Period:** regime III · mode I · 15 agents · nudges 7. Data: `data/processed/H35-nudger-maxwell-demon/G39/`.

## Why this period
regime III.

## Prediction
*Written 2026-10-03, before running on this period.*
- **P1:** the nudger's state information I(M; D, G, K) is above the circular-shift null p95 (scored only with ≥ 15 nudges in the grid).
- **P2 (descriptive here):** first-nudge ATT on A30 reported with its day-bootstrap CI.
- **Verdict:** descriptive (too few nudges for the gate model and policy values; numbers reported, not scored beyond P1).

## Result
Descriptive; fewer than 15 nudges in the grid, so P1 is not scored. Numbers below are for completeness only.

| Quantity | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| information used, b = I(M;D,G,K)/r | 1.38 bits per nudge of 12.7 bits decision entropy; within-day part 1.14 | permutation null p95 | above |
| decomposition (bits per nudge) | I(M;K) 0.87, I(M;G\|D) 0.99, I(M;K\|D,G) 0.55, I(M;D) -0.21; agent \| X 0.36; controller memory \| X 1.06 | within-stratum permutation |  |
| first-nudge ATT, A30 (strict isolation) | 3.56 (no CI), n = 1 | 0 |  |
| first-nudge ATT, A30 (H04 isolation set) | 0.80 [-0.50, 2.10], n = 2; placebo 0.48 [-1.38, 2.33] | 0 |  |

Data: `data/processed/H35-nudger-maxwell-demon/G39/results.json` (built 2026-10-03).

## Scorecard (period-specific axes)
C 0 · D 0 · E 0 · G 0 (descriptive period; too few nudges to score).

## Notes
- 2026-10-03: folder created with the prediction, before the run.
- 2026-10-03: results filled from the round-1 run (after the prediction above).
