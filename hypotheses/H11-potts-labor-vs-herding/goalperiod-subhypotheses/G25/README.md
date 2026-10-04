# H11 × G25: Create a digital museum of 2025 (2025-12-29 → 2026-01-05)

**Verdict:** P1 failed (significant); P2 failed (significant)
**Verdict (1b):** P1 failed (sig.); P2 failed (sig.) (unchanged)
**Role:** exploratory (transfer)
**Period:** regime I · mode C · N = 10 at start · one room (#general) · 5 active days. Class for H11: **AF**.

## Why this period
Transfer: shared objective where each agent made exhibits, so antiferromagnetic.

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
| P1 βJ_CW (primary) | < 0 | +4.12 (jackknife SE 1.09, t = +3.76, t_crit 2.78) | βJ = 0; N1 (within-agent permutation) mean -0.18, z_N1 = +5.8 | **failed (significant)** |
| P2 βJ_PL (agent fields) | z ≤ 0 | +5.28; z_N2 = +6.72, z_N1d = +5.77, z_N1 = +6.41 | N2 (circular shift) mean +2.90 | **failed (significant)** |
| O3 agreement ratio R | – | 2.73 | 1 = interchangeable agents | descriptive |
| P4 control: action-class βJ_CW | ≥ 0 or ≈ 0, any class | +1.26 (t = +1.16); action βJ_PL z_N2 = +2.45 | – | consistent |
| P5 held-out PL (coupled vs fields-only) | gain in ≥ 4/5 folds where abs(z_N2) ≥ 2 | 5/5 day folds improve | fields only | consistent |
| P6 plmDCA diagonal (secondary) | same sign as βJ_PL | z_N1 = +18.7 | N1 (9 draws) | agrees |
| P7 prior: abs(βJ) < 2 | – | βJ_CW +4.12; drift-corrected excess βJ_PL − N2 mean = +2.37 | – | fails (βJ_CW) |

**Robustness (O9; βJ_CW):** raw labels +4.02, q ≤ 4 +3.88, W = 15 min +3.95, W = 60 min +3.63, computer-use actions only (post hoc) +4.06, day fields +2.63.

**Post hoc** (added after the round-1 run, not pre-registered):
- z of βJ_PL vs a ±1-window local shift: +3.04. This tests alignment at the 30-min scale.
- Ownership index (share of agent-windows on projects one agent dominates): 0.10.
- Persistence P(same project next window): 0.51.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | z_N2 = +6.7; held-out gain 5/5 folds |
| D unfitted predictions | 0 | sign by goal mode: failed (significant) (not diagnostic on its own: βJ_CW > 0 in 11/14 tested weeks, whatever the mode) |
| G ground truth | 0 | – |

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication (templated) on the shared deterministic `project_states` labels (`scheme/build_r1b.py`, `analysis/round1b.py replicate`; 99 nulls). Card predictions R1b-1 (replication) and R1b-2 (work space) were written before the run.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| βJ_CW (t) | +4.12 (+3.8) | +4.30 (+4.1) |
| z_N2 (βJ_PL vs circular shift) | +6.7 | +7.8 |
| local-shift z (±1 window, post hoc) | +3.0 | +3.4 |
| held-out PL gain (day folds) | 5 | 5/5 |
| P1 / P2 | failed (significant) / failed (significant) | failed (significant) / failed (significant) |
