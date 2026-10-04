# H35 × G37: Pick your own goal (2026-03-30 → 2026-04-01)

**Verdict:** descriptive
**Role:** replication (exploratory) (round 1, non-holdout); exploratory (descriptive)
**Verdict (1b):** descriptive (< 6 strictly isolated first nudges; 2026-10-04)
**Period:** regime III · mode F · 13 agents · nudges 17. Data: `data/processed/H35-nudger-maxwell-demon/G37/`.

## Why this period
first regime-III goal.

## Prediction
*Written 2026-10-03, before running on this period.*
- **P1:** the nudger's state information I(M; D, G, K) is above the circular-shift null p95 (scored only with ≥ 15 nudges in the grid).
- **P2 (descriptive here):** first-nudge ATT on A30 reported with its day-bootstrap CI.
- **Verdict:** descriptive (too few nudges for the gate model and policy values; numbers reported, not scored beyond P1).

## Result
Descriptive. P1 (≥ 15 nudges): information above the permutation null (b = 2.20). Gate-level numbers rest on 8–10 nudged gates and are not interpreted; long-pause regime (nudged gates escape at high rates).

| Quantity | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| information used, b = I(M;D,G,K)/r | 2.20 bits per nudge of 11.1 bits decision entropy; within-day part 1.68 | permutation null p95 | above |
| decomposition (bits per nudge) | I(M;K) 1.02, I(M;G\|D) 0.30, I(M;K\|D,G) 0.28, I(M;D) 0.85; agent \| X 0.09; controller memory \| X 0.14 | within-stratum permutation |  |
| first-nudge ATT, A30 (strict isolation) | 2.76 [-8.00, 8.90], n = 5 | 0 |  |
| first-nudge ATT, A30 (H04 isolation set) | 0.30 [-2.39, 6.26], n = 12; placebo 0.39 [-1.34, 7.87] | 0 |  |
| gate escape by trap age (un-nudged / nudged) | k 1: 0.55 (n 111); k 1: 1.00 (n 3) nudged; k 2–3: 0.34 (n 80); k 2–3: 1.00 (n 3) nudged; k 4–9: 0.28 (n 54); k 4–9: 1.00 (n 2) nudged; k ≥10: 1.00 (n 1) nudged |  |  |
| gate model (card), nudge × ln k | 0.34 ± 318.05 | 0 |  |
| value per nudge (escapes): random-gate / logged / once at k=1 / k=2 | 0.560 / 0.614 / 0.468 / 0.556 (ratios to logged 0.76, 0.91) |  |  |

Data: `data/processed/H35-nudger-maxwell-demon/G37/results.json` (built 2026-10-03).

## Scorecard (period-specific axes)
C 0 · D 0 · E 0 · G 0 (descriptive period; too few nudges to score).

## Notes
- 2026-10-03: folder created with the prediction, before the run.
- 2026-10-03: results filled from the round-1 run (after the prediction above).
