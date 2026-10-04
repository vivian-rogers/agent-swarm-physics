# H35 × G31: Pick your own goal (2026-02-16 → 2026-02-19 (02-20 = NE11 excluded))

**Verdict:** descriptive
**Role:** replication (exploratory) (round 1, non-holdout); exploratory (descriptive)
**Verdict (1b):** descriptive (< 6 strictly isolated first nudges; 2026-10-04)
**Period:** regime I · mode F · 12 agents · nudges 24. Data: `data/processed/H35-nudger-maxwell-demon/G31/`.

## Why this period
regime I, first nudger week.

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
| information used, b = I(M;D,G,K)/r | 0.20 bits per nudge of 11.1 bits decision entropy; within-day part 0.20 | permutation null p95 | not above |
| decomposition (bits per nudge) | I(M;K) -0.00, I(M;G\|D) 0.00, I(M;K\|D,G) -0.03, I(M;D) 0.21; agent \| X 0.64; controller memory \| X 0.34 | within-stratum permutation |  |
| first-nudge ATT, A30 (strict isolation) | 5.00 (no CI), n = 1 | 0 |  |
| first-nudge ATT, A30 (H04 isolation set) | -0.33 [-1.19, 0.84], n = 10; placebo 0.61 [-0.27, 1.38] | 0 |  |

Data: `data/processed/H35-nudger-maxwell-demon/G31/results.json` (built 2026-10-03).

## Scorecard (period-specific axes)
C 0 · D 0 · E 0 · G 0 (descriptive period; too few nudges to score).

## Notes
- 2026-10-03: folder created with the prediction, before the run.
- 2026-10-03: results filled from the round-1 run (after the prediction above).
