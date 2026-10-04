# H11 × G42: Run your own Youtube channel! (2026-05-18 → 2026-05-25)

**Verdict:** descriptive
**Verdict (1b):** descriptive (unchanged)
**Role:** exploratory (transfer)
**Period:** regime III · mode I · N = 15 at start · #best / #rest · 5 active days. Class for H11: **none-I**.

## Why this period
Descriptive: each agent its own channel. No sign prediction.

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
| P1 βJ_CW (primary) | none | -2.16 (jackknife SE 1.28, t = -1.68, t_crit 2.78) | βJ = 0; N1 (within-agent permutation) mean -2.68, z_N1 = +1.3 | **descriptive** |
| P2 βJ_PL (agent fields) | none | +1.48; z_N2 = +1.32, z_N1d = +1.15, z_N1 = +1.24 | N2 (circular shift) mean +0.20 | **descriptive** |
| O3 agreement ratio R | – | 0.47 | 1 = interchangeable agents | descriptive |
| P4 control: action-class βJ_CW | ≥ 0 or ≈ 0, any class | +0.26 (t = +0.31); action βJ_PL z_N2 = +2.71 | – | consistent |
| P5 held-out PL (coupled vs fields-only) | gain in ≥ 4/5 folds where abs(z_N2) ≥ 2 | 3/5 day folds improve | fields only | not applicable |
| P6 plmDCA diagonal (secondary) | same sign as βJ_PL | z_N1 = +3.4 | N1 (9 draws) | agrees |
| P7 prior: abs(βJ) < 2 | – | βJ_CW -2.16; drift-corrected excess βJ_PL − N2 mean = +1.28 | – | fails (βJ_CW) |

**Robustness (O9; βJ_CW):** raw labels -1.93, q ≤ 4 -0.78, W = 15 min -1.93, W = 60 min -1.16, computer-use actions only (post hoc) -1.95, day fields -2.52, rooms pooled -24.21.

**Post hoc** (added after the round-1 run, not pre-registered):
- z of βJ_PL vs a ±1-window local shift: +1.09. This tests alignment at the 30-min scale.
- Ownership index (share of agent-windows on projects one agent dominates): 0.73.
- Persistence P(same project next window): 0.88.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | z_N2 = +1.3; held-out gain 3/5 folds |
| D unfitted predictions | 0 | sign by goal mode: descriptive (not diagnostic on its own: βJ_CW > 0 in 11/14 tested weeks, whatever the mode) |
| G ground truth | 0 | – |

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication (templated) on the shared deterministic `project_states` labels (`scheme/build_r1b.py`, `analysis/round1b.py replicate`; 99 nulls). Card predictions R1b-1 (replication) and R1b-2 (work space) were written before the run.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| βJ_CW (t) | -2.16 (-1.7) | -2.06 (-1.6) |
| z_N2 (βJ_PL vs circular shift) | +1.3 | +1.3 |
| local-shift z (±1 window, post hoc) | +1.1 | +1.1 |
| held-out PL gain (day folds) | 3 | 3/5 |
| P1 / P2 | descriptive / descriptive | descriptive / descriptive |

**Work space (R1b-2; agent work commits, DQ4 ledger, W = 30):**

| Space | labelled agent-windows | blocks (N ≥ 3) | βJ_CW (t) | z_N2 | local-shift z | excess βJ_PL − N2 | co-location (N2 mean, z) | ownership |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attention | 401 | 73 | -2.06 (-1.6) | +1.1 | +1.2 | +0.99 | 0.23 (0.21, +2.0) | 0.73 |
| work | 341 | 71 | -2.38 (-2.9) | +1.4 | +0.7 | +1.13 | 0.20 (0.18, +2.3) | 0.74 |

Agent-windows with both labels: work repo = attention project in 0.94. The attention top project holds 0.24 of attention and 0.26 of work agent-windows.
