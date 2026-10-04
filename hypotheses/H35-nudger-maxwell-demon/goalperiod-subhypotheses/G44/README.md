# H35 × G44: Finetune your leader (2026-05-26 → 2026-05-29)

**Verdict:** descriptive
**Role:** exploratory (round 1, non-holdout); exploratory (descriptive)
**Verdict (1b):** descriptive (< 6 strictly isolated first nudges; 2026-10-04)
**Period:** regime III · mode C · 16 agents · nudges 27. Data: `data/processed/H35-nudger-maxwell-demon/G44/`.

## Why this period
regime III.

## Prediction
*Written 2026-10-03, before running on this period.*
- **P1:** the nudger's state information I(M; D, G, K) is above the circular-shift null p95 (scored only with ≥ 15 nudges in the grid).
- **P2 (descriptive here):** first-nudge ATT on A30 reported with its day-bootstrap CI.
- **Verdict:** descriptive (too few nudges for the gate model and policy values; numbers reported, not scored beyond P1).

## Result
Descriptive. P1 (≥ 15 nudges): information above the permutation null (b = 1.19). Gate-level numbers rest on 8–10 nudged gates and are not interpreted; long-pause regime (nudged gates escape at high rates).

| Quantity | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| information used, b = I(M;D,G,K)/r | 1.19 bits per nudge of 10.8 bits decision entropy; within-day part 0.66 | permutation null p95 | above |
| decomposition (bits per nudge) | I(M;K) 1.05, I(M;G\|D) 0.35, I(M;K\|D,G) 0.03, I(M;D) 0.18; agent \| X 0.63; controller memory \| X 0.35 | within-stratum permutation |  |
| first-nudge ATT, A30 (strict isolation) | 0.29 [-0.23, 1.85], n = 5 | 0 |  |
| first-nudge ATT, A30 (H04 isolation set) | 1.54 [-0.37, 2.86], n = 11; placebo -0.32 [-1.46, 1.57] | 0 |  |
| gate escape by trap age (un-nudged / nudged) | k 1: 0.51 (n 175); k 2–3: 0.38 (n 120); k 2–3: 1.00 (n 6) nudged; k 4–9: 0.28 (n 85); k 4–9: 1.00 (n 1) nudged; k ≥10: 0.24 (n 17); k ≥10: 0.00 (n 1) nudged |  |  |
| gate model (card), nudge × ln k | -18.08 ± 223.24 | 0 |  |
| value per nudge (escapes): random-gate / logged / once at k=1 / k=2 | 0.557 / 0.533 / 0.543 / 0.605 (ratios to logged 1.02, 1.14) |  |  |

Data: `data/processed/H35-nudger-maxwell-demon/G44/results.json` (built 2026-10-03).

## Scorecard (period-specific axes)
C 0 · D 0 · E 0 · G 0 (descriptive period; too few nudges to score).

## Notes
- 2026-10-03: folder created with the prediction, before the run.
- 2026-10-03: results filled from the round-1 run (after the prediction above).
