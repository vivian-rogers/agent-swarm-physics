# H30 × NE10: the first nudges ever (2026-02-13, #30) and the nudger's first fortnight (#31)

**Verdict:** failed
**Role:** native (round 1b, non-holdout)
**Period:** #30 (regime I; the first 12 nudges in the record, all on 02-13, the last day of #30; DQ9) and #31 (25 nudges, 02-16 → 02-20, the next week). Comparison: G51's first nudges (round 1b).

## Why this test
Every later nudge period has agents that have been nudged before. NE10 is the only place where the lever is new to every agent. If a nudge works through novelty (the agent has not yet learned to ignore the template), the first nudges ever should respond more than the well-worn #51 nudges; if a nudge works as a read-out kick, the response should be similar.

## Prediction
*Written 2026-10-04 07:31 UTC, before any round-1b statistic on #30/#31 (round-1 G30 had 11 nudge kicks with an unstable CI; G31 0.68 [−0.25, 2.00]).*

Observable: round-1b χ_act(N_tgt) in G30 and G31, pooled by random effects, vs G51's round-1b first-nudge χ_act.
- **N1:** the pooled first-fortnight χ_act is > 0 (point); its CI is expected to include 0 (≈ 37 nudges).
- **N2 (no novelty premium):** the pooled value does not exceed G51's first-nudge χ_act by more than the pooled CI half-width.
- **Verdict rule:** supported if N1 and N2 hold; failed if the pooled point is ≤ 0; mixed otherwise. Low power is expected; the verdict is flagged as such.

## Result
*Run 2026-10-04 ~08:20 UTC (`analysis/r1b_extra.py`).*

| Statistic | value |
| --- | --- |
| G30 χ_act(N_tgt) (9 nudge kicks read in-window) | -0.14 [CI unstable: one nudge day] |
| G31 χ_act(N_tgt) (13 kicks) | -0.43 [-1.26, 0.45] |
| pooled (random effects) | **-0.42 [-1.27, 0.42]** |
| G51 first nudge (round 1b) | 1.21 [0.80, 1.66] |

**Verdict: failed (low power).** N1 fails (pooled point ≤ 0); N2 holds trivially (no novelty premium: the first nudges ever do not respond more than #51's). With 22 kicks the test cannot separate "no effect in regime I" from noise; regime-I nudges land between discrete sessions, where the minute-grid outcome is coarse.
