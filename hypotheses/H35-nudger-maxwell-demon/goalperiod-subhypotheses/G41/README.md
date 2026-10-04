# H35 × G41: Perform novel research (2026-05-11 → 2026-05-15)

**Verdict:** mixed
**Role:** replication (exploratory) (round 1, non-holdout); secondary
**Verdict (1b):** mixed (round-1 statistics unchanged; no strictly isolated first nudges; 2026-10-04)
**Period:** regime III · mode I · 15 agents · nudges 59. Data: `data/processed/H35-nudger-maxwell-demon/G41/`.

## Why this period
regime III, third-largest nudge count.

## Prediction
*Written 2026-10-03, before running on this period.*
- **P1:** information above the circular-shift null p95.
- **P2:** first-nudge ATT point estimate > 0.
- **P3:** shared gate-model kick × ln k slope < 0 (sign).
- **P5:** gate-once (k* = 1 or 2) value per nudge ≥ the logged nudger's (point ratio ≥ 1).
- **Verdict rule:** supported if all four hold; failed if none; otherwise mixed. Low power (59 nudges, 5 days).

## Result
**Outcome vs prediction.** P1 supported but weak (b = 0.44, above null; agent identity and controller memory carry more than the state, 1.16 and 1.20 bits). P2 untestable under strict isolation (no first nudge without another direct kick in 30 min); with H04's isolation set the ATT is 3.25 [2.52, 4.91] (placebo 0.63 [−0.02, 2.17]). **P3 failed as worded:** the shared-model slope is +0.36 ± 0.40 (the card model gives −0.24 ± 0.90; both uninformative). P5 supported on the point (×1.01 / ×1.11). Long-pause regime as in G38 (nudged gates escape 0.33–1.0).

| Quantity | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| information used, b = I(M;D,G,K)/r | 0.44 bits per nudge of 9.7 bits decision entropy; within-day part 0.38 | permutation null p95 | above |
| decomposition (bits per nudge) | I(M;K) 0.23, I(M;G\|D) 0.23, I(M;K\|D,G) -0.01, I(M;D) -0.02; agent \| X 1.16; controller memory \| X 1.20 | within-stratum permutation |  |
| first-nudge ATT, A30 (strict isolation) | –, n = 0 | 0 |  |
| first-nudge ATT, A30 (H04 isolation set) | 3.25 [2.52, 4.91], n = 20; placebo 0.63 [-0.02, 2.17] | 0 |  |
| gate escape by trap age (un-nudged / nudged) | k 1: 0.52 (n 115); k 1: 1.00 (n 8) nudged; k 2–3: 0.24 (n 83); k 2–3: 0.80 (n 5) nudged; k 4–9: 0.22 (n 85); k 4–9: 0.33 (n 3) nudged; k ≥10: 0.31 (n 16); k ≥10: 1.00 (n 1) nudged |  |  |
| gate model (card), nudge × ln k | -0.24 ± 0.90 | 0 |  |
| value per nudge (escapes): random-gate / logged / once at k=1 / k=2 | 0.402 / 0.393 / 0.395 / 0.436 (ratios to logged 1.01, 1.11) |  |  |

Data: `data/processed/H35-nudger-maxwell-demon/G41/results.json` (built 2026-10-03).

## Scorecard (period-specific axes)
C 1 (information above null) · D 0 · E 0 · G 0.

## Notes
- 2026-10-03: folder created with the prediction, before the run.
- 2026-10-03: results filled from the round-1 run (after the prediction above).
