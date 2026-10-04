# H11 × G18: Reduce global poverty as much as you can (2025-10-20 → 2025-11-03)

**Verdict:** P1 failed (significant); P2 failed (significant)
**Verdict (1b):** P1 failed (sig.); P2 failed (sig.) (unchanged)
**Role:** replication (exploratory (candidate))
**Period:** regime I · mode C · N = 7 at start · one room (#general) · 10 active days. Class for H11: **AF**.

## Why this period
A two-week shared objective with many interventions and sites: a divisible portfolio, so antiferromagnetic.

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
| P1 βJ_CW (primary) | < 0 | +5.00 (jackknife SE 0.75, t = +6.66, t_crit 2.26) | βJ = 0; N1 (within-agent permutation) mean -0.40, z_N1 = +8.7 | **failed (significant)** |
| P2 βJ_PL (agent fields) | z ≤ 0 | +6.85; z_N2 = +8.68, z_N1d = +9.74, z_N1 = +9.88 | N2 (circular shift) mean +4.47 | **failed (significant)** |
| O3 agreement ratio R | – | 3.86 | 1 = interchangeable agents | descriptive |
| P4 control: action-class βJ_CW | ≥ 0 or ≈ 0, any class | +1.69 (t = +7.83); action βJ_PL z_N2 = +4.01 | – | consistent |
| P5 held-out PL (coupled vs fields-only) | gain in ≥ 4/5 folds where abs(z_N2) ≥ 2 | 10/10 day folds improve | fields only | consistent |
| P6 plmDCA diagonal (secondary) | same sign as βJ_PL | z_N1 = +12.1 | N1 (9 draws) | agrees |
| P7 prior: abs(βJ) < 2 | – | βJ_CW +5.00; drift-corrected excess βJ_PL − N2 mean = +2.38 | – | fails (βJ_CW) |

**Robustness (O9; βJ_CW):** raw labels +5.20, q ≤ 4 +4.76, W = 15 min +4.67, W = 60 min +5.02, computer-use actions only (post hoc) +4.12, day fields +2.51.

**Post hoc** (added after the round-1 run, not pre-registered):
- z of βJ_PL vs a ±1-window local shift: +4.06. This tests alignment at the 30-min scale.
- Ownership index (share of agent-windows on projects one agent dominates): 0.14.
- Persistence P(same project next window): 0.66.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | z_N2 = +8.7; held-out gain 10/10 folds |
| D unfitted predictions | 0 | sign by goal mode: failed (significant) (not diagnostic on its own: βJ_CW > 0 in 11/14 tested weeks, whatever the mode) |
| G ground truth | 0 | – |

## Notes
- 2026-10-03 (round 1): the final-day dominant repo (`o3-ux/poverty-etl`) jumps from ≈ 0 to ≈ 1 on the last day, a deadline-driven convergence in a week predicted to be AF.

## Round 1b (improved data, 2026-10-04)
*Replication (templated) on the shared deterministic `project_states` labels (`scheme/build_r1b.py`, `analysis/round1b.py replicate`; 99 nulls). Card predictions R1b-1 (replication) and R1b-2 (work space) were written before the run.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| βJ_CW (t) | +5.00 (+6.7) | +4.91 (+6.2) |
| z_N2 (βJ_PL vs circular shift) | +8.7 | +8.5 |
| local-shift z (±1 window, post hoc) | +4.1 | +4.1 |
| held-out PL gain (day folds) | 10 | 9/10 |
| P1 / P2 | failed (significant) / failed (significant) | failed (significant) / failed (significant) |
