# H11 × G41: Perform novel research! (2026-05-11 → 2026-05-18)

**Verdict:** P1 supported; P2 supported
**Verdict (1b):** P1 supported; P2 supported (unchanged)
**Role:** exploratory (candidate)
**Period:** regime III · mode I · N = 15 at start · #best / #rest · 5 active days. Class for H11: **FM-convergence**.

## Why this period
Many #rest agents independently proposed the same research topic: convergence, so ferromagnetic (the card's 'research convergence').

## Prediction
*Written 2026-10-03, before running on this period.*
- **Class prediction:** ferromagnetic (convergence on one topic): βJ_CW > 0 (P1), βJ_PL z_N2 ≥ +2 (P2). Per-period verdict on P1: **supported** if the sign is right and |t| > t_(D−1, 0.975) (leave-one-day-out jackknife); **weak** if the sign is right but not significant; **failed** if the sign is wrong.
- **P4 (control):** the action-class βJ_CW is positive or ≈ 0 whatever the class.
- **P7 (prior):** |βJ_CW| < 2, below βJ_s(q), so no spontaneous first-order transition.
- **Minimum data:** ≥ 15 room blocks with N_b ≥ 3 at W = 30; otherwise n/a.
- **What would count against it:** the opposite sign of βJ_CW (P1), or, for an FM class, a positive βJ_CW that disappears under the within-agent permutation null N1 (spread carried entirely by agent fields, R1).

## Result
| Test | Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- | --- |
| P1 βJ_CW (primary) | > 0 | +4.30 (jackknife SE 0.17, t = +24.89, t_crit 2.78) | βJ = 0; N1 (within-agent permutation) mean +3.48, z_N1 = +24.8 | **supported** |
| P2 βJ_PL (agent fields) | z ≥ +2 | +7.95; z_N2 = +5.44, z_N1d = +4.34, z_N1 = +10.40 | N2 (circular shift) mean +6.61 | **supported** |
| O3 agreement ratio R | – | 2.43 | 1 = interchangeable agents | descriptive |
| P4 control: action-class βJ_CW | ≥ 0 or ≈ 0, any class | +0.27 (t = +0.90); action βJ_PL z_N2 = +3.08 | – | consistent |
| P5 held-out PL (coupled vs fields-only) | gain in ≥ 4/5 folds where abs(z_N2) ≥ 2 | 5/5 day folds improve | fields only | consistent |
| P6 plmDCA diagonal (secondary) | same sign as βJ_PL | z_N1 = +7.0 | N1 (9 draws) | agrees |
| P7 prior: abs(βJ) < 2 | – | βJ_CW +4.30; drift-corrected excess βJ_PL − N2 mean = +1.34 | – | fails (βJ_CW) |

**Robustness (O9; βJ_CW):** raw labels +4.25, q ≤ 4 +4.77, W = 15 min +4.29, W = 60 min +4.43, computer-use actions only (post hoc) +4.32, day fields +3.55, rooms pooled +2.62.

**Post hoc** (added after the round-1 run, not pre-registered):
- z of βJ_PL vs a ±1-window local shift: +4.18. This tests alignment at the 30-min scale.
- Ownership index (share of agent-windows on projects one agent dominates): 0.16.
- Persistence P(same project next window): 0.80.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | z_N2 = +5.4; held-out gain 5/5 folds |
| D unfitted predictions | 1 | sign by goal mode: supported (not diagnostic on its own: βJ_CW > 0 in 11/14 tested weeks, whatever the mode) |
| G ground truth | 0 | – |

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication (templated) on the shared deterministic `project_states` labels (`scheme/build_r1b.py`, `analysis/round1b.py replicate`; 99 nulls). Card predictions R1b-1 (replication) and R1b-2 (work space) were written before the run.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| βJ_CW (t) | +4.30 (+24.9) | +4.23 (+25.6) |
| z_N2 (βJ_PL vs circular shift) | +5.4 | +5.8 |
| local-shift z (±1 window, post hoc) | +4.2 | +3.6 |
| held-out PL gain (day folds) | 5 | 5/5 |
| P1 / P2 | supported / supported | supported / supported |

**Work space (R1b-2; agent work commits, DQ4 ledger, W = 30):**

| Space | labelled agent-windows | blocks (N ≥ 3) | βJ_CW (t) | z_N2 | local-shift z | excess βJ_PL − N2 | co-location (N2 mean, z) | ownership |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attention | 516 | 78 | +4.23 (+25.6) | +5.3 | +3.5 | +1.43 | 0.72 (0.68, +4.0) | 0.10 |
| work | 331 | 66 | +3.72 (+14.3) | +3.8 | +1.8 | +1.13 | 0.65 (0.61, +3.1) | 0.25 |

Agent-windows with both labels: work repo = attention project in 0.89. The attention top project holds 0.26 of attention and 0.28 of work agent-windows.
