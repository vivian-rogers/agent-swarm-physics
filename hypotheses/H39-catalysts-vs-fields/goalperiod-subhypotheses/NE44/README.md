# H39 × NE44: nudges before and after the pause default changes from 12 h to 5 min (2026-06-11)

**Verdict:** failed
**Role:** native (round 1b, non-holdout; comparison of fitted period parameters across a step, exception c)
**Period:** the step lies inside the held-out NE21+NE23 window and is never touched. **12-h side:** nudge episodes in G37, G38, G39, G40, G41, G42, G44 (regime III, 4-h days); **5-min side:** G51 (nudger-on days).

## Why this test
Under the 12-h default a pausing agent sleeps until something wakes it, so a nudge is a pure wake-up of a trapped agent (H35: escape 0.86–1.0 at any trap age); under the 5-min default agents wake on their own and a nudge competes with the timer. In H39's terms the nudge's catalytic part (raising idle escape) should be larger before the change.

## Prediction
*Written 2026-10-04 07:31 UTC, before any round-1b point-lever statistic for these periods (round-1 values seen: G38 nudges n 32, K +0.13, n.s.; G51 K +0.16, idle escape +0.45).*

Observables: round-1b B4 point-lever statistics for N_tgt (leading @, presence-cut windows): the idle escape log ratio ln(e^K_idle / e^C_idle), K and Δπ_idle per period; the 12-h side pooled by random effects; difference 12-h − G51 with a normal CI.
- **N1:** the idle escape log ratio is larger on the 12-h side (point).
- **N2:** Δπ_idle is more negative on the 12-h side (point).
- **Verdict rule:** supported if N1 holds with the difference CI excluding 0; mixed if N1 holds in point only; failed if N1 is reversed. Low power expected (12-h side ≈ 40–60 episodes in total).

## Result
*Run 2026-10-04 ~08:40 UTC (`analysis/r1b_summary.py`; periods G37, G38, G40, G41, G42, G44, 72 nudge episodes on the 12-h side).*

| Statistic | 12-h side (random effects) | G51 | Δ [95% CI] |
| --- | --- | --- | --- |
| idle escape ln ratio | +0.14 [-0.35, +0.64] (I² 0.89) | +0.40 | -0.26 [-0.78, +0.26] |
| Δπ_idle | -0.037 | -0.058 | +0.021 [-0.030, +0.072] |
| K | +0.11 | +0.16 | -0.05 [-0.24, +0.14] |

**Verdict: failed** (N1 and N2 reversed in point, n.s.). Nudge catalysis is not larger under the long pause default; H30's NE44 test (activity) points the same way, and RE-V1 finds no early wakes at nudge-receiving calls either side of the step.
