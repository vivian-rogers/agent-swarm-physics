# H35 × G35: Test your game (2026-03-16 → 2026-03-20)

**Verdict:** descriptive
**Role:** exploratory (round 1, non-holdout); exploratory (descriptive)
**Period:** regime II · mode C · 13 agents · nudges 17. Data: `data/processed/H35-nudger-maxwell-demon/G35/`.

## Why this period
regime II.

## Prediction
*Written 2026-10-03, before running on this period.*
- No pause gates in regime I/II: X = (D, K = current run of consecutive WAITs).
- **P1:** the nudger's state information I(M; D, G, K) is above the circular-shift null p95 (scored only with ≥ 15 nudges in the grid).
- **P2 (descriptive here):** first-nudge ATT on A30 reported with its day-bootstrap CI.
- **Verdict:** descriptive (P1 scored only with ≥ 15 nudges).

## Result
Descriptive; fewer than 15 nudges in the grid, so P1 is not scored. Numbers below are for completeness only.

| Quantity | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| information used, b = I(M;D,G,K)/r | 1.93 bits per nudge of 12.4 bits decision entropy; within-day part 1.86 | permutation null p95 | above |
| decomposition (bits per nudge) | I(M;K) 1.39, I(M;G\|D) 0.00, I(M;K\|D,G) 1.29, I(M;D) 0.63; agent \| X 1.52; controller memory \| X 1.63 | within-stratum permutation |  |
| first-nudge ATT, A30 (strict isolation) | -10.38 (no CI), n = 1 | 0 |  |
| first-nudge ATT, A30 (H04 isolation set) | -3.80 [-13.94, 1.68], n = 4; placebo -0.57 [-3.81, 0.54] | 0 |  |

Data: `data/processed/H35-nudger-maxwell-demon/G35/results.json` (built 2026-10-03).

## Scorecard (period-specific axes)
C 0 · D 0 · E 0 · G 0 (descriptive period; too few nudges to score).

## Notes
- 2026-10-03: folder created with the prediction, before the run.
- 2026-10-03: results filled from the round-1 run (after the prediction above).
