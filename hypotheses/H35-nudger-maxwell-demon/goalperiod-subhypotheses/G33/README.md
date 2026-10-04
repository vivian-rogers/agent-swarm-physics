# H35 × G33: Discuss the Pentagon-AI news (2026-03-02 → 2026-03-04)

**Verdict:** descriptive
**Role:** exploratory (round 1, non-holdout); exploratory (descriptive)
**Verdict (1b):** descriptive (< 6 strictly isolated first nudges; 2026-10-04)
**Period:** regime II · mode C · 12 agents · nudges 22. Data: `data/processed/H35-nudger-maxwell-demon/G33/`.

## Why this period
regime II.

## Prediction
*Written 2026-10-03, before running on this period.*
- No pause gates in regime I/II: X = (D, K = current run of consecutive WAITs).
- **P1:** the nudger's state information I(M; D, G, K) is above the circular-shift null p95 (scored only with ≥ 15 nudges in the grid).
- **P2 (descriptive here):** first-nudge ATT on A30 reported with its day-bootstrap CI.
- **Verdict:** descriptive (P1 scored only with ≥ 15 nudges).

## Result
Descriptive. P1 scored (15 nudges in the grid): **not above** the permutation null (b ≈ 0). Regime II: X = (idle duration, WAIT run); strict isolation leaves no first nudge.

| Quantity | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| information used, b = I(M;D,G,K)/r | -0.00 bits per nudge of 10.2 bits decision entropy; within-day part -0.01 | permutation null p95 | not above |
| decomposition (bits per nudge) | I(M;K) -0.01, I(M;G\|D) 0.00, I(M;K\|D,G) -0.02, I(M;D) 0.01; agent \| X 0.57; controller memory \| X 0.74 | within-stratum permutation |  |
| first-nudge ATT, A30 (strict isolation) | –, n = 0 | 0 |  |
| first-nudge ATT, A30 (H04 isolation set) | 1.76 [1.02, 3.52], n = 13; placebo 0.39 [-1.77, 1.36] | 0 |  |

Data: `data/processed/H35-nudger-maxwell-demon/G33/results.json` (built 2026-10-03).

## Scorecard (period-specific axes)
C 0 · D 0 · E 0 · G 0 (descriptive period; too few nudges to score).

## Notes
- 2026-10-03: folder created with the prediction, before the run.
- 2026-10-03: results filled from the round-1 run (after the prediction above).
