# H16 × NE43: Escape with no kicks (#51, nudger off after 2026-08-20)

**Verdict:** mixed
**Role:** native
**Period:** regime III · #51. B = 08-07 → 08-20 (nudges on, daily bookends already gone) vs C = 08-21 → 09-02 (no nudges). Same goal, room and 8-h days.

## Why this period
If traps deepen because nothing kicks the agent out, removing the nudger should lower escape; if aging is intrinsic to the agent's own loop, the aging slopes should not change. NE43 removes the lever at a known date with everything else fixed (DQ9: "trap escape without kicks").

## Prediction
*Written 2026-10-04, before running (card, "Round 1b", N2). H39's post hoc note (idle escape −13% after the nudger stopped) had been seen.* (a) Aging persists on both sides: TS1r deep β < −0.3 and TS2r β_lnk < 0 in B and in C. Credence 0.7. (b) Gate escape is lower without nudges: the C indicator in the TS2r gate logit (agent FE, ln k, ln declared duration, directed kick) is negative with its Wald CI below 0. Credence 0.4.

## Result
*Run 2026-10-04 (`analysis/native_r1b.py`; `r1b/native_r1b.json`).*

| | B (nudges on) | C (nudger off) |
| --- | --- | --- |
| TS1r deep β (boot CI), escapes | −0.59 [−0.68, −0.39] | −0.53 [−0.56, −0.41], 839 |
| TS2r β on ln k (Wald CI), gates | −0.31 [−0.39, −0.23], 6,855 | −0.26 [−0.36, −0.16], 4,557 |
| gate logit, C indicator | | +0.006 [−0.09, +0.10] (11,412 gates) |
| gate logit, directed kick | | +0.42 [0.28, 0.56] |

(a) **holds**: aging is unchanged when the nudger goes quiet, so it is a property of the agent's own loop, not something kicks create or mask. (b) **failed**: gates are escaped as often without nudges; the nudger's contribution at the gate is too small to see at the swarm level (consistent with H35's 0.5% of activity).

## Scorecard (period-specific axes)
E 1 (an invariance prediction held across the intervention; the predicted drop did not appear).

## Notes
- The bookends ended on 08-05, so B starts on 08-07 to leave the bookend step out.
