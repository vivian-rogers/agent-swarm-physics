# H35 × G42: Run your own YouTube channel (2026-05-18 → 2026-05-22)

**Verdict:** descriptive
**Role:** replication (exploratory) (round 1, non-holdout); exploratory (descriptive)
**Verdict (1b):** descriptive (< 6 strictly isolated first nudges; 2026-10-04)
**Period:** regime III · mode I · 15 agents · nudges 25. Data: `data/processed/H35-nudger-maxwell-demon/G42/`.

## Why this period
regime III.

## Prediction
*Written 2026-10-03, before running on this period.*
- **P1:** the nudger's state information I(M; D, G, K) is above the circular-shift null p95 (scored only with ≥ 15 nudges in the grid).
- **P2 (descriptive here):** first-nudge ATT on A30 reported with its day-bootstrap CI.
- **Verdict:** descriptive (too few nudges for the gate model and policy values; numbers reported, not scored beyond P1).

## Result
Descriptive. P1 (≥ 15 nudges): information above the permutation null (b = 1.37). Gate-level numbers rest on 8–10 nudged gates and are not interpreted; long-pause regime (nudged gates escape at high rates).

| Quantity | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| information used, b = I(M;D,G,K)/r | 1.37 bits per nudge of 11.3 bits decision entropy; within-day part 0.94 | permutation null p95 | above |
| decomposition (bits per nudge) | I(M;K) 0.60, I(M;G\|D) 0.52, I(M;K\|D,G) 0.40, I(M;D) 0.24; agent \| X 0.71; controller memory \| X 0.79 | within-stratum permutation |  |
| first-nudge ATT, A30 (strict isolation) | 0.81 [-4.10, 8.54], n = 3 | 0 |  |
| first-nudge ATT, A30 (H04 isolation set) | -0.81 [-5.56, 1.65], n = 12; placebo 0.31 [-1.07, 1.10] | 0 |  |
| gate escape by trap age (un-nudged / nudged) | k 1: 0.76 (n 63); k 1: 1.00 (n 5) nudged; k 2–3: 0.37 (n 19); k 2–3: 1.00 (n 1) nudged; k 4–9: 0.62 (n 8) |  |  |
| gate model (card), nudge × ln k | -5.54 ± 1055.78 | 0 |  |
| value per nudge (escapes): random-gate / logged / once at k=1 / k=2 | 0.334 / 0.226 / 0.361 / 0.247 (ratios to logged 1.59, 1.09) |  |  |

Data: `data/processed/H35-nudger-maxwell-demon/G42/results.json` (built 2026-10-03).

## Scorecard (period-specific axes)
C 0 · D 0 · E 0 · G 0 (descriptive period; too few nudges to score).

## Notes
- 2026-10-03: folder created with the prediction, before the run.
- 2026-10-03: results filled from the round-1 run (after the prediction above).
