# H11 × G39: Build your own interactive world! (2026-04-27 → 2026-05-04)

**Verdict:** descriptive
**Role:** exploratory (transfer)
**Period:** regime III · mode I · N = 15 at start · #best / #rest · 5 active days. Class for H11: **none-I**.

## Why this period
Descriptive: each agent its own world. No sign prediction.

## Prediction
*Written 2026-10-03, before running on this period.*
- **Class prediction:** no sign prediction (individual objectives); reported descriptively. Per-period verdict on P1: **supported** if the sign is right and |t| > t_(D−1, 0.975) (leave-one-day-out jackknife); **weak** if the sign is right but not significant; **failed** if the sign is wrong.
- **P4 (control):** the action-class βJ_CW is positive or ≈ 0 whatever the class.
- **P7 (prior):** |βJ_CW| < 2, below βJ_s(q), so no spontaneous first-order transition.
- **Minimum data:** ≥ 15 room blocks with N_b ≥ 3 at W = 30; otherwise n/a.
- **What would count against it:** the opposite sign of βJ_CW (P1), or, for an FM class, a positive βJ_CW that disappears under the within-agent permutation null N1 (spread carried entirely by agent fields, R1).

## Result
| Test | Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- | --- |
| P1 βJ_CW (primary) | none | -8.61 (jackknife SE 2.82, t = -3.05, t_crit 2.78) | βJ = 0; N1 (within-agent permutation) mean -8.63, z_N1 = +0.0 | **descriptive** |
| P2 βJ_PL (agent fields) | none | -1.84; z_N2 = -1.27, z_N1d = -1.40, z_N1 = -0.26 | N2 (circular shift) mean +0.31 | **descriptive** |
| O3 agreement ratio R | – | 0.29 | 1 = interchangeable agents | descriptive |
| P4 control: action-class βJ_CW | ≥ 0 or ≈ 0, any class | -1.00 (t = -1.56); action βJ_PL z_N2 = +0.67 | – | consistent |
| P5 held-out PL (coupled vs fields-only) | gain in ≥ 4/5 folds where abs(z_N2) ≥ 2 | 1/5 day folds improve | fields only | not applicable |
| P6 plmDCA diagonal (secondary) | same sign as βJ_PL | z_N1 = -0.2 | N1 (9 draws) | agrees |
| P7 prior: abs(βJ) < 2 | – | βJ_CW -8.61; drift-corrected excess βJ_PL − N2 mean = -2.15 | – | fails (βJ_CW) |

**Robustness (O9; βJ_CW):** raw labels -9.87, q ≤ 4 -5.94, W = 15 min -6.95, W = 60 min -7.92, computer-use actions only (post hoc) -6.84, day fields -9.22, rooms pooled -30.00.

**Post hoc** (added after the round-1 run, not pre-registered):
- z of βJ_PL vs a ±1-window local shift: -1.41. This tests alignment at the 30-min scale.
- Ownership index (share of agent-windows on projects one agent dominates): 1.00.
- Persistence P(same project next window): 0.92.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | z_N2 = -1.3; held-out gain 1/5 folds |
| D unfitted predictions | 0 | sign by goal mode: descriptive (not diagnostic on its own: βJ_CW > 0 in 11/14 tested weeks, whatever the mode) |
| G ground truth | 1 | per-agent worlds → strong spread, matching 'each agent builds a world' |

## Notes
