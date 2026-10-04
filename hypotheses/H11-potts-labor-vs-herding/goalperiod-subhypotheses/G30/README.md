# H11 × G30: Adopt a park and get it cleaned! (2026-02-09 → 2026-02-16)

**Verdict:** P1 failed (significant); P2 failed (significant)
**Verdict (1b):** P1 failed (sig.); P2 failed (sig.) (unchanged)
**Role:** exploratory (transfer)
**Period:** regime I · mode C · N = 12 at start · one room (#general) · 5 active days. Class for H11: **AF**.

## Why this period
Transfer: shared objective with a shared repo and two parks, so antiferromagnetic by the class rule. Note the shared repo, which may make it look like herding.

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
| P1 βJ_CW (primary) | < 0 | +2.01 (jackknife SE 0.25, t = +8.01, t_crit 2.78) | βJ = 0; N1 (within-agent permutation) mean -0.34, z_N1 = +2.7 | **failed (significant)** |
| P2 βJ_PL (agent fields) | z ≤ 0 | +2.67; z_N2 = +4.33, z_N1d = +3.89, z_N1 = +3.85 | N2 (circular shift) mean +1.02 | **failed (significant)** |
| O3 agreement ratio R | – | 1.12 | 1 = interchangeable agents | descriptive |
| P4 control: action-class βJ_CW | ≥ 0 or ≈ 0, any class | -0.41 (t = -0.97); action βJ_PL z_N2 = +2.01 | – | consistent |
| P5 held-out PL (coupled vs fields-only) | gain in ≥ 4/5 folds where abs(z_N2) ≥ 2 | 4/5 day folds improve | fields only | consistent |
| P6 plmDCA diagonal (secondary) | same sign as βJ_PL | z_N1 = +6.9 | N1 (9 draws) | agrees |
| P7 prior: abs(βJ) < 2 | – | βJ_CW +2.01; drift-corrected excess βJ_PL − N2 mean = +1.65 | – | fails (βJ_CW) |

**Robustness (O9; βJ_CW):** raw labels +2.01, q ≤ 4 +2.01, W = 15 min +1.84, W = 60 min +2.16, computer-use actions only (post hoc) +1.93, day fields +1.68.

**Post hoc** (added after the round-1 run, not pre-registered):
- z of βJ_PL vs a ±1-window local shift: +3.54. This tests alignment at the 30-min scale.
- Ownership index (share of agent-windows on projects one agent dominates): 0.01.
- Persistence P(same project next window): 0.60.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | z_N2 = +4.3; held-out gain 4/5 folds |
| D unfitted predictions | 0 | sign by goal mode: failed (significant) (not diagnostic on its own: βJ_CW > 0 in 11/14 tested weeks, whatever the mode) |
| G ground truth | 0 | – |

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication (templated) on the shared deterministic `project_states` labels (`scheme/build_r1b.py`, `analysis/round1b.py replicate`; 99 nulls). Card predictions R1b-1 (replication) and R1b-2 (work space) were written before the run.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| βJ_CW (t) | +2.01 (+8.0) | +1.97 (+8.1) |
| z_N2 (βJ_PL vs circular shift) | +4.3 | +4.1 |
| local-shift z (±1 window, post hoc) | +3.5 | +3.5 |
| held-out PL gain (day folds) | 4 | 4/5 |
| P1 / P2 | failed (significant) / failed (significant) | failed (significant) / failed (significant) |

**Work space (R1b-2; agent work commits, DQ4 ledger, W = 30):**

| Space | labelled agent-windows | blocks (N ≥ 3) | βJ_CW (t) | z_N2 | local-shift z | excess βJ_PL − N2 | co-location (N2 mean, z) | ownership |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attention | 439 | 40 | +1.97 (+8.1) | +5.1 | +3.3 | +1.60 | 0.94 (0.92, +2.6) | 0.00 |
| work | 161 | 35 | -0.39 (-0.5) | +0.8 | -0.0 | +0.43 | 0.86 (0.85, +0.7) | 0.00 |

Agent-windows with both labels: work repo = attention project in 0.83. The attention top project holds 0.70 of attention and 0.74 of work agent-windows.
