# H18 × NE15: the #best / #rest split (2026-03-16)

**Verdict:** mixed
**Role:** exploratory (post-split side only); the before/after comparison is confirmatory
**Period:** NE15 splits the 13-agent village into #best (3: GPT-5.4, Opus 4.6, Gemini 3.1 Pro) and #rest (10) on 2026-03-16, the first day of #35 (regime II). The pre-split days (#34, 03-05 → 03-13) are in the locked holdout (NE30 window and #34), so exploration can only use the post-split days.

## Why this event
A fixed attention budget predicts that splitting a room raises each remaining pair's coupling (HH90; H05 saw within-room J rise ~6× after this split). Before/after needs the holdout. What exploration can test is the same mechanism as a cross-section: on the same post-split days, with the same goal, agents in a 3-agent room face much smaller k than agents in a 10-agent room.

## Prediction
*Written 2026-10-03, before any H18 real-data run.*
- **Exploratory (#35, and the two-room days of #36–#44 as replication):** k̄ per talk turn is smaller in the small room; per-pair uptake p̄ is higher there, with p̄_small/p̄_large within ×2 of k̄_large/k̄_small; with agent and day effects, the room coefficient on uptake shrinks toward 0 (CI includes 0) once k is in the model (M_pow). The effective budget S per talk turn is similar in both rooms (ratio within [0.67, 1.5]).
- **Confirmatory (holdout; `analysis/confirm_holdout.py`, not run):** for the 13 agents, per-pair uptake after the split (#35) vs. before (#34 days outside #voted-out, 03-09 → 03-13) rises by about the k̄ ratio for #best agents, and S per talk turn changes by < 30%.
- Counts against: the small room has lower uptake, or the room effect survives k.

## Result
*Run 2026-10-03 (`analysis/fit_periods.py` room contrast; `spanning.json`; figure `figures/rooms.pdf`).* Same-day contrast: clusters = day × room, so the room's log-uptake effect is averaged over days. It is shown without k (M_const) and with k (M_pow).

| Period | days with two rooms | k̄ ratio large/small | p̄ ratio small/large | S ratio small/large | room log-effect, no k | room log-effect, with k |
| --- | --- | --- | --- | --- | --- | --- |
| G35 | 3 | 3.62 | 2.05 | 0.73 | 0.95 [0.87, 1.04] | -0.14 [-0.19, -0.09] |
| G36 | 5 | 2.00 | 0.99 | 0.63 | -0.13 [-1.09, 0.48] | -0.62 [-1.25, -0.18] |
| G37 | 3 | 1.82 | 1.38 | 0.76 | 0.64 [0.08, 1.19] | 0.06 [-0.30, 0.73] |
| G38 | 16 | 0.91 | 2.76 | 2.23 | 0.62 [0.23, 0.92] | 0.66 [0.32, 1.01] |
| G39 | 2 | 2.04 | 2.95 | 1.17 | 0.78 [0.26, 1.35] | 0.52 [0.10, 0.96] |
| G41 | 5 | 2.45 | 1.50 | 0.78 | 0.72 [0.52, 0.89] | 0.07 [-0.14, 0.30] |
| G42 | 5 | 2.00 | 2.97 | 1.44 | 0.61 [0.28, 0.88] | 0.08 [-0.29, 0.29] |
| G44 | 4 | 1.76 | 0.89 | 0.58 | 0.05 [-0.21, 0.27] | -0.46 [-0.60, -0.36] |

**#35 (the NE15 week):**
- the 3-agent #best room faced 3.6× smaller k̄ and addressed each pending peer 2.05× more often;
- β̂ = 0.75 predicts 3.6^0.75 ≈ 2.6×;
- once k is in the model the room effect collapses from 0.95 to −0.14 (slightly over-absorbed; the CI excludes 0, so the strict "CI includes 0" criterion fails narrowly);
- S per turn in the small room is 0.73× the large room's (within [0.67, 1.5]).

**Replications:**
- the effect is absorbed by k in #37, #41 and #42;
- it survives k in #38 and #39 (#38's small room was as busy per turn as the large one, k̄ ratio 0.91, yet addressed 2.8× more);
- there is no small-room advantage in #36 and #44.

**Caveat:** rooms hold different agents, so agent style is not removed.

**Verdict: mixed** (the #35 side behaves as predicted, quantitatively; replications 3 of 7). The before/after comparison waits for the confirmatory run (C5).


## Notes
- 2026-10-03: H05 already saw NE15's post-split #35 window in round 1 (activity couplings, not mentions); H18's observable (mention responses vs. k) has not been computed on it by anyone.
- 2026-10-03: exploratory side run; results above.
