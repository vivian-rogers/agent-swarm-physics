# H35 × G36: Interact with agents outside the Village (2026-03-23 → 2026-03-27)

**Verdict:** descriptive
**Role:** replication (exploratory) (round 1, non-holdout); exploratory (descriptive)
**Verdict (1b):** descriptive (< 6 strictly isolated first nudges; 2026-10-04)
**Period:** regime II · mode C · 13 agents · nudges 6. Data: `data/processed/H35-nudger-maxwell-demon/G36/`.

## Why this period
regime II/III boundary (03-24).

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
| information used, b = I(M;D,G,K)/r | 0.46 bits per nudge of 13.0 bits decision entropy; within-day part 0.35 | permutation null p95 | not above |
| decomposition (bits per nudge) | I(M;K) 0.00, I(M;G\|D) 0.00, I(M;K\|D,G) 0.00, I(M;D) 0.46; agent \| X 1.29; controller memory \| X 0.93 | within-stratum permutation |  |
| first-nudge ATT, A30 (strict isolation) | 2.63 (no CI), n = 1 | 0 |  |
| first-nudge ATT, A30 (H04 isolation set) | 2.24 [0.72, 5.15], n = 3; placebo 0.88 [-4.55, 3.61] | 0 |  |

Data: `data/processed/H35-nudger-maxwell-demon/G36/results.json` (built 2026-10-03).

## Scorecard (period-specific axes)
C 0 · D 0 · E 0 · G 0 (descriptive period; too few nudges to score).

## Notes
- 2026-10-03: folder created with the prediction, before the run.
- 2026-10-03: results filled from the round-1 run (after the prediction above).
