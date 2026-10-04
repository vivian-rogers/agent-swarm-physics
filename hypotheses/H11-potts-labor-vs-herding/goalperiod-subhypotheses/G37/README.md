# H11 × G37: Pick your own goal! (2026-03-30 → 2026-04-02)

**Verdict:** P1 supported; P2 supported
**Verdict (1b):** P1 supported; P2 supported (unchanged)
**Role:** exploratory (transfer)
**Period:** regime III · mode F · N = 13 at start · #best / #rest · 3 active days. Class for H11: **FM-free**.

## Why this period
Transfer: free week (regime III, #best / #rest), so ferromagnetic by the class rule.

## Prediction
*Written 2026-10-03, before running on this period.*
- **Class prediction:** ferromagnetic (herding in a free week): βJ_CW > 0 (P1), βJ_PL z_N2 ≥ +2 (P2). Per-period verdict on P1: **supported** if the sign is right and |t| > t_(D−1, 0.975) (leave-one-day-out jackknife); **weak** if the sign is right but not significant; **failed** if the sign is wrong.
- **P4 (control):** the action-class βJ_CW is positive or ≈ 0 whatever the class.
- **P7 (prior):** |βJ_CW| < 2, below βJ_s(q), so no spontaneous first-order transition.
- **Minimum data:** ≥ 15 room blocks with N_b ≥ 3 at W = 30; otherwise n/a.
- **What would count against it:** the opposite sign of βJ_CW (P1), or, for an FM class, a positive βJ_CW that disappears under the within-agent permutation null N1 (spread carried entirely by agent fields, R1).

## Result
| Test | Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- | --- |
| P1 βJ_CW (primary) | > 0 | +3.73 (jackknife SE 0.16, t = +23.13, t_crit 4.30) | βJ = 0; N1 (within-agent permutation) mean +1.95, z_N1 = +6.7 | **supported** |
| P2 βJ_PL (agent fields) | z ≥ +2 | +5.44; z_N2 = +6.88, z_N1d = +5.84, z_N1 = +6.89 | N2 (circular shift) mean +2.13 | **supported** |
| O3 agreement ratio R | – | 2.67 | 1 = interchangeable agents | descriptive |
| P4 control: action-class βJ_CW | ≥ 0 or ≈ 0, any class | -0.76 (t = -2.43); action βJ_PL z_N2 = +2.00 | – | consistent |
| P5 held-out PL (coupled vs fields-only) | gain in ≥ 4/5 folds where abs(z_N2) ≥ 2 | 3/3 day folds improve | fields only | consistent |
| P6 plmDCA diagonal (secondary) | same sign as βJ_PL | z_N1 = +16.4 | N1 (9 draws) | agrees |
| P7 prior: abs(βJ) < 2 | – | βJ_CW +3.73; drift-corrected excess βJ_PL − N2 mean = +3.31 | – | fails (βJ_CW) |

**Robustness (O9; βJ_CW):** raw labels +3.64, q ≤ 4 +3.98, W = 15 min +3.33, W = 60 min +3.81, computer-use actions only (post hoc) +3.50, day fields +2.89, rooms pooled +3.13.

**Post hoc** (added after the round-1 run, not pre-registered):
- z of βJ_PL vs a ±1-window local shift: +2.71. This tests alignment at the 30-min scale.
- Ownership index (share of agent-windows on projects one agent dominates): 0.13.
- Persistence P(same project next window): 0.62.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | z_N2 = +6.9; held-out gain 3/3 folds |
| D unfitted predictions | 1 | sign by goal mode: supported (not diagnostic on its own: βJ_CW > 0 in 11/14 tested weeks, whatever the mode) |
| G ground truth | 0 | – |

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication (templated) on the shared deterministic `project_states` labels (`scheme/build_r1b.py`, `analysis/round1b.py replicate`; 99 nulls). Card predictions R1b-1 (replication) and R1b-2 (work space) were written before the run.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| βJ_CW (t) | +3.73 (+23.1) | +3.68 (+27.4) |
| z_N2 (βJ_PL vs circular shift) | +6.9 | +6.9 |
| local-shift z (±1 window, post hoc) | +2.7 | +2.7 |
| held-out PL gain (day folds) | 3 | 3/3 |
| P1 / P2 | supported / supported | supported / supported |

**Work space (R1b-2; agent work commits, DQ4 ledger, W = 30):**

| Space | labelled agent-windows | blocks (N ≥ 3) | βJ_CW (t) | z_N2 | local-shift z | excess βJ_PL − N2 | co-location (N2 mean, z) | ownership |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attention | 202 | 28 | +3.68 (+27.4) | +7.8 | +3.4 | +3.16 | 0.63 (0.48, +4.7) | 0.13 |
| work | 84 | 12 (< 15: descriptive) | +1.58 (+1.3) | +2.3 | +1.2 | +1.38 | 0.58 (0.53, +1.0) | 0.29 |

Agent-windows with both labels: work repo = attention project in 0.78. The attention top project holds 0.16 of attention and 0.21 of work agent-windows.
