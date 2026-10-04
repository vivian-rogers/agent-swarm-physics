# H11 × G19: Create a popular daily puzzle game like Wordle (2025-11-03 → 2025-11-17)

**Verdict:** P1 supported; P2 supported; P3 failed
**Verdict (1b):** P1 supported; P2 supported (unchanged)
**Role:** replication (exploratory (candidate))
**Period:** regime I · mode C · N = 7 at start · one room (#general) · 10 active days. Class for H11: **FM-consensus**.

## Why this period
HH25's case: many candidate puzzle concepts, then convergence on one build. A consensus choice, so ferromagnetic with a first-order jump (HH84). Project labels capture the build the swarm converges on, not the concept names in chat; concept-mention states are a round-2 item.

## Prediction
*Written 2026-10-03, before running on this period.*
- **Class prediction:** ferromagnetic (consensus on a shared choice): βJ_CW > 0 (P1), βJ_PL z_N2 ≥ +2 (P2), and a first-order jump in the dominant share (P3). Per-period verdict on P1: **supported** if the sign is right and |t| > t_(D−1, 0.975) (leave-one-day-out jackknife); **weak** if the sign is right but not significant; **failed** if the sign is wrong.
- **P3 (consensus jump):** the share x₁ of the final-day dominant project shows an O4 'jump' (Δ ≥ 0.3, τ ≤ 2 windows, persistence ≤ 0.15), and βJ_CW ≥ βJ_s(q_eff) (first-order region). A jump with βJ_CW < βJ_s is scored as a field-driven step; a gradual rise counts against P3.
- **P4 (control):** the action-class βJ_CW is positive or ≈ 0 whatever the class.
- **P7 (prior):** |βJ_CW| < 2, below βJ_s(q), so no spontaneous first-order transition.
- **Minimum data:** ≥ 15 room blocks with N_b ≥ 3 at W = 30; otherwise n/a.
- **What would count against it:** the opposite sign of βJ_CW (P1), or, for an FM class, a positive βJ_CW that disappears under the within-agent permutation null N1 (spread carried entirely by agent fields, R1).

## Result
| Test | Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- | --- |
| P1 βJ_CW (primary) | > 0 | +2.76 (jackknife SE 0.29, t = +9.60, t_crit 2.26) | βJ = 0; N1 (within-agent permutation) mean -0.12, z_N1 = +5.2 | **supported** |
| P2 βJ_PL (agent fields) | z ≥ +2 | +3.13; z_N2 = +5.21, z_N1d = +5.93, z_N1 = +6.61 | N2 (circular shift) mean +1.32 | **supported** |
| O3 agreement ratio R | – | 1.38 | 1 = interchangeable agents | descriptive |
| P3 consensus jump (project labels) | jump, Δ ≥ 0.3, τ ≤ 2, persistence ≤ 0.15; βJ_CW ≥ βJ_s(q_eff) | none (Δ = +0.31, τ = 0.04 win, persistence +0.22); q_eff = 2.1, βJ_s = 2.00, first-order region: yes | constant / linear fits | **failed** |
| P4 control: action-class βJ_CW | ≥ 0 or ≈ 0, any class | +1.96 (t = +7.02); action βJ_PL z_N2 = +5.32 | – | consistent |
| P5 held-out PL (coupled vs fields-only) | gain in ≥ 4/5 folds where abs(z_N2) ≥ 2 | 10/10 day folds improve | fields only | consistent |
| P6 plmDCA diagonal (secondary) | same sign as βJ_PL | z_N1 = +8.8 | N1 (9 draws) | agrees |
| P7 prior: abs(βJ) < 2 | – | βJ_CW +2.76; drift-corrected excess βJ_PL − N2 mean = +1.81 | – | fails (βJ_CW) |

**Robustness (O9; βJ_CW):** raw labels +2.88, q ≤ 4 +2.76, W = 15 min +2.68, W = 60 min +2.62, computer-use actions only (post hoc) +1.90, day fields +1.61.

**Post hoc** (added after the round-1 run, not pre-registered):
- z of βJ_PL vs a ±1-window local shift: +3.94. This tests alignment at the 30-min scale.
- Ownership index (share of agent-windows on projects one agent dominates): 0.09.
- Persistence P(same project next window): 0.62.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | z_N2 = +5.2; held-out gain 10/10 folds |
| D unfitted predictions | 1 | sign by goal mode: supported (not diagnostic on its own: βJ_CW > 0 in 11/14 tested weeks, whatever the mode) |
| G ground truth | 0 | – |

## Notes
- 2026-10-03 (round 1): the project label tracks the build repo (`o3-ux/daily-puzzle`). It held about 0.6 of labeled agent-windows from the first windows, so the concept choice (HH25) happened before or outside the artifact record. Concept-mention states from chat are needed to test HH25 (round 2). The P3 'none' verdict is the frozen-consensus case in synthetic S3, not evidence of a gradual choice.

## Round 1b (improved data, 2026-10-04)
*Replication (templated) on the shared deterministic `project_states` labels (`scheme/build_r1b.py`, `analysis/round1b.py replicate`; 99 nulls). Card predictions R1b-1 (replication) and R1b-2 (work space) were written before the run.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| βJ_CW (t) | +2.76 (+9.6) | +2.75 (+7.9) |
| z_N2 (βJ_PL vs circular shift) | +5.2 | +4.7 |
| local-shift z (±1 window, post hoc) | +3.9 | +3.4 |
| held-out PL gain (day folds) | 10 | 9/10 |
| P1 / P2 | supported / supported | supported / supported |
