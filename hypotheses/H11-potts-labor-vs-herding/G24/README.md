# H11 × G24: Do random acts of kindness! (2025-12-22 → 2025-12-29)

**Verdict:** P1 failed; P2 failed (significant)
**Role:** exploratory (transfer)
**Period:** regime I · mode C · N = 10 at start · one room (#general) · 5 active days. Class for H11: **AF**.

## Why this period
Transfer: shared objective where agents divided up approaches, so antiferromagnetic.

## Prediction
*Written 2026-10-03, before running on this period.*
- **Class prediction:** antiferromagnetic (division of labor): βJ_CW < 0 (P1) and βJ_PL ≤ 0 vs the circular-shift null N2 (P2). Per-period verdict on P1: **supported** if the sign is right and |t| > t_(D−1, 0.975) (leave-one-day-out jackknife); **weak** if the sign is right but not significant; **failed** if the sign is wrong.
- **P4 (control):** the action-class βJ_CW is positive or ≈ 0 whatever the class.
- **P7 (prior):** |βJ_CW| < 2, below βJ_s(q), so no spontaneous first-order transition.
- **Minimum data:** ≥ 15 room blocks with N_b ≥ 3 at W = 30; otherwise n/a.
- **What would count against it:** the opposite sign of βJ_CW (P1), or, for an FM class, a positive βJ_CW that disappears under the within-agent permutation null N1 (spread carried entirely by agent fields, R1).

## Result
| Test | Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- | --- |
| P1 βJ_CW (primary) | < 0 | +3.25 (jackknife SE 26.59, t = +0.12, t_crit 2.78) | βJ = 0; N1 (within-agent permutation) mean -0.75, z_N1 = +2.3 | **failed** |
| P2 βJ_PL (agent fields) | z ≤ 0 | +6.67; z_N2 = +2.74, z_N1d = +3.09, z_N1 = +2.55 | N2 (circular shift) mean +3.45 | **failed (significant)** |
| O3 agreement ratio R | – | 7.99 | 1 = interchangeable agents | descriptive |
| P4 control: action-class βJ_CW | ≥ 0 or ≈ 0, any class | -3.38 (t = -1.17); action βJ_PL z_N2 = +0.54 | – | consistent |
| P5 held-out PL (coupled vs fields-only) | gain in ≥ 4/5 folds where abs(z_N2) ≥ 2 | 3/5 day folds improve | fields only | inconsistent |
| P6 plmDCA diagonal (secondary) | same sign as βJ_PL | z_N1 = +8.1 | N1 (9 draws) | agrees |
| P7 prior: abs(βJ) < 2 | – | βJ_CW +3.25; drift-corrected excess βJ_PL − N2 mean = +3.21 | – | fails (βJ_CW) |

**Robustness (O9; βJ_CW):** raw labels +2.55, q ≤ 4 +3.67, W = 15 min +2.95, W = 60 min +2.66, computer-use actions only (post hoc) +1.98, day fields +2.19.

**Post hoc** (added after the round-1 run, not pre-registered):
- z of βJ_PL vs a ±1-window local shift: +2.40. This tests alignment at the 30-min scale.
- Ownership index (share of agent-windows on projects one agent dominates): 0.65.
- Persistence P(same project next window): 0.60.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 1 | z_N2 = +2.7; held-out gain 3/5 folds |
| D unfitted predictions | 0 | sign by goal mode: failed (not diagnostic on its own: βJ_CW > 0 in 11/14 tested weeks, whatever the mode) |
| G ground truth | 0 | – |

## Notes
