# H30 × NE44: the pause default changes from 12 h to 5 min (2026-06-11)

**Verdict:** failed
**Role:** native (round 1b, non-holdout; comparison of fitted period parameters across a step, exception c)
**Period:** the step itself lies inside the held-out NE21+NE23 window (06-08 → 07-06), so it is never touched. Instead the per-period χ_act(N_tgt) on either side are compared as points: **12-h side** G37, G38, G39, G40, G41, G42, G44 (regime III, 4-h days, two rooms except G40); **5-min side** G51 (07-06 → 08-20, 8-h days, one room).

## Why this test
H35 found that before the 06-11 change a nudge wakes a pausing agent at any trap age (escape 0.86–1.0), while after it agents wake at a 5-min timer anyway and only early re-pauses respond. If that is right, an operator's nudge should buy more extra activity per nudge under the long default than under the short one: the susceptibility depends on the scaffold's pause rule, not only on the agent.

## Prediction
*Written 2026-10-04 07:31 UTC, before any round-1b χ_act was computed for these periods (the round-1 values in the card were seen: G51 0.59 pre-registered, G38 −0.08, G41 0.86, small periods noisy).*

Observable: round-1b χ_act(N_tgt) (fixed bins, leading @, receiving-call timing, past-only, day fixed effect) per period with its day-bootstrap SE; the 12-h side pooled by random effects (DerSimonian–Laird); difference Δ = χ(12-h pooled) − χ(G51) with a normal CI from the two SEs.
- **N1:** Δ > 0 (point).
- **N2:** the first-nudge χ_act shows the same ordering (12-h pooled > G51).
- **Verdict rule:** supported if Δ > 0 with CI excluding 0; mixed if Δ > 0 with CI including 0; failed if Δ ≤ 0. Confounds named in advance: 4-h vs 8-h days, N 10–17 vs 21–32, two rooms vs one, different goals; the 12-h side is small (≈ 7–120 nudges per period). Credence (N1) 0.6.

## Result
*Run 2026-10-04 ~08:20 UTC (`analysis/r1b_extra.py`; per-period values from `r1b/G<NN>/results.json`).*

| Statistic | 12-h side (pooled, random effects) | G51 (5-min) | Δ (12-h − 5-min) [95% CI] |
| --- | --- | --- | --- |
| χ_act(N_tgt), day FE, past-only | 0.57 [0.04, 1.10] (7 periods, I² 0.17) | 0.98 [0.63, 1.37] | **-0.41 [-1.05, 0.24]** |
| first nudge of an episode | 0.52 [0.01, 1.04] | 1.21 [0.80, 1.66] | **-0.69 [-1.36, -0.02]** |

Per period (12-h side): G37 2.37, G38 0.95, G39 0.31, G40 −1.12, G41 1.02, G42 −0.55, G44 0.01.

**Verdict: failed (reversed).** N1 and N2 both point the other way: a nudge buys more extra activity under the 5-min default, and for first nudges the difference excludes 0. This agrees with RE-V1 (H04 round 1b: no early wakes at nudge-receiving calls either side of NE44; the response is immediate at the receiving call) and argues against reading the 12-h scaffold as "a nudge wakes a sleeping agent": the long default leaves more of the 30-min window in a pause the nudge does not end. Confounds as named (4-h vs 8-h days, roster size, rooms, goals).
