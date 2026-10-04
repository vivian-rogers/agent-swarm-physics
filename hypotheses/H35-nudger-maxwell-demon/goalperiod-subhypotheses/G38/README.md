# H35 × G38: Choose a charity and raise money (2026-04-02 → 2026-04-24)

**Verdict:** mixed
**Role:** native (round 1b native test below) · round 1: exploratory (round 1, non-holdout); secondary
**Verdict (1b):** failed (native N1 as worded: sustained ATT 0.058 < G51's 0.094; 2026-10-04)
**Period:** regime III · mode C · 12 agents · nudges 108. Data: `data/processed/H35-nudger-maxwell-demon/G38/`.

## Why this period
17 days, second-largest nudge count.

## Prediction
*Written 2026-10-03, before running on this period.*
- **P1:** information above the circular-shift null p95.
- **P2:** first-nudge ATT point estimate > 0.
- **P3:** shared gate-model kick × ln k slope < 0 (sign).
- **P5:** gate-once (k* = 1 or 2) value per nudge ≥ the logged nudger's (point ratio ≥ 1).
- **Verdict rule:** supported if all four hold; failed if none; otherwise mixed. Lower power than G51 (108 nudges, 4-h days).

## Result
**Outcome vs prediction.** P1 supported (b = 1.25, above null). P2 supported on the point (ATT 1.27 [−0.32, 2.91], n 25). **P3 failed:** the shared-model slope is +0.59 ± 0.25 and the card model gives nudge × ln k = +1.18 ± 0.52 (the effect *rises* with trap age). P5 supported on the point for k* = 2 (×1.02), not for k* = 1 (×0.66).

**Mechanism differs from G51.** Before 06-11 the default pause was 12 h, so a nudge (an @-mention) wakes a pausing agent: escape at nudged gates is 0.86–1.0 at every trap age vs 0.20–0.51 un-nudged. Targeting then matters little (logged ≈ random among gates, ΔV = −0.04 escapes per nudge).

| Quantity | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| information used, b = I(M;D,G,K)/r | 1.25 bits per nudge of 10.6 bits decision entropy; within-day part 0.82 | permutation null p95 | above |
| decomposition (bits per nudge) | I(M;K) 0.97, I(M;G\|D) 0.66, I(M;K\|D,G) 0.24, I(M;D) 0.26; agent \| X 0.61; controller memory \| X 0.83 | within-stratum permutation |  |
| first-nudge ATT, A30 (strict isolation) | 1.27 [-0.32, 2.91], n = 25 | 0 |  |
| first-nudge ATT, A30 (H04 isolation set) | 0.82 [-0.22, 2.11], n = 46; placebo -0.09 [-0.91, 0.70] | 0 |  |
| gate escape by trap age (un-nudged / nudged) | k 1: 0.51 (n 537); k 1: 0.87 (n 23) nudged; k 2–3: 0.28 (n 437); k 2–3: 0.86 (n 7) nudged; k 4–9: 0.20 (n 467); k 4–9: 0.86 (n 14) nudged; k ≥10: 0.24 (n 100); k ≥10: 1.00 (n 6) nudged |  |  |
| gate model (card), nudge × ln k | 1.18 ± 0.52 | 0 |  |
| value per nudge (escapes): random-gate / logged / once at k=1 / k=2 | 0.494 / 0.455 / 0.299 / 0.463 (ratios to logged 0.66, 1.02) |  |  |

Data: `data/processed/H35-nudger-maxwell-demon/G38/results.json` (built 2026-10-03).

## Round 1b native test (NE44 contrast: long-pause regime)
*Role of this section: native (round 1b), in addition to round 1.*
*Prediction written 2026-10-04, before computing any round-1b outcome around a nudge.* G38 runs under the 12-h pause default (NE44 changed it to 5 min on 06-11, inside the holdout, so the step itself is untestable); a nudge here wakes an agent out of a long sleep at any trap age (round 1). If waking from a long sleep restarts real work, the sustained-run response should be larger here than in the short-pause G51, where agents are read at the next 5-min gate.
- **N1:** first-nudge ATT on sustained runs in G38 > the G51 estimate (point comparison; sign only, low power: ~100 nudges, few strictly isolated first nudges).
- **N2:** first-nudge ATT on work commits (60 min) has a positive point estimate in G38.
- Counts against the wake-up reading: G38 sustained ATT ≤ G51's.

**Result (round 1b native, run 2026-10-04; `G38/r1b/`).** 25 strictly isolated first nudges (19 with 60-min windows).
- **N1 fails as worded:** sustained ATT +0.058 [+0.011, +0.132] in G38 vs +0.094 in G51 (point lower). Post hoc rate DiD reverses the order (G38 +1.26 runs/h [−0.82, +3.27] vs G51 +0.29), with very wide CIs.
- **N2 fails as worded:** work-commit ATT (60 min) −0.98 [−1.95, −0.03]; placebo −0.38 (not clean); post hoc DiD +0.54 commits/h [−0.73, +1.73].
- Glance +0.037 [0.000, +0.106]. Native verdict: **failed** as worded; the long-pause wake-up may restart work (DiD points), but 25 nudges cannot show it.

## Scorecard (period-specific axes)
C 1 · D 0 (P3 failed) · E 0 · G 1 (H09: only @-mentions get through a pause, seen here as the wake-up effect).

## Notes
- 2026-10-03: folder created with the prediction, before the run.
- 2026-10-03: results filled from the round-1 run (after the prediction above).
