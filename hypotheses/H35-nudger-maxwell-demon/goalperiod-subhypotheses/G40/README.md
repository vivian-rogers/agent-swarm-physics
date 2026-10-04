# H35 × G40: Connect your worlds into a 3D universe (2026-05-04 → 2026-05-08)

**Verdict:** descriptive
**Role:** exploratory (round 1, non-holdout); exploratory (descriptive)
**Period:** regime III · mode C · 15 agents · nudges 11. Data: `data/processed/H35-nudger-maxwell-demon/G40/`.

## Why this period
regime III, merged rooms (NE42).

## Prediction
*Written 2026-10-03, before running on this period.*
- **P1:** the nudger's state information I(M; D, G, K) is above the circular-shift null p95 (scored only with ≥ 15 nudges in the grid).
- **P2 (descriptive here):** first-nudge ATT on A30 reported with its day-bootstrap CI.
- **Verdict:** descriptive (too few nudges for the gate model and policy values; numbers reported, not scored beyond P1).

## Result
Descriptive; fewer than 15 nudges in the grid, so P1 is not scored. Numbers below are for completeness only.

| Quantity | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| information used, b = I(M;D,G,K)/r | 2.13 bits per nudge of 12.1 bits decision entropy; within-day part 1.75 | permutation null p95 | above |
| decomposition (bits per nudge) | I(M;K) 1.14, I(M;G\|D) 1.12, I(M;K\|D,G) 0.74, I(M;D) 0.14; agent \| X 1.47; controller memory \| X 0.89 | within-stratum permutation |  |
| first-nudge ATT, A30 (strict isolation) | 9.52 (no CI), n = 2 | 0 |  |
| first-nudge ATT, A30 (H04 isolation set) | 0.40 [-5.76, 7.99], n = 6; placebo -1.91 [-4.35, 1.38] | 0 |  |

Data: `data/processed/H35-nudger-maxwell-demon/G40/results.json` (built 2026-10-03).

## Scorecard (period-specific axes)
C 0 · D 0 · E 0 · G 0 (descriptive period; too few nudges to score).

## Notes
- 2026-10-03: folder created with the prediction, before the run.
- 2026-10-03: results filled from the round-1 run (after the prediction above).
