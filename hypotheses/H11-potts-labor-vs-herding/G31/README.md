# H11 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-23)

**Verdict:** P1 supported; P2 supported; P3 failed
**Role:** exploratory (candidate)
**Period:** regime I · mode F · N = 12 at start · one room (#general) · 5 active days. Class for H11: **FM-free**.

## Why this period
HH26's case: about nine agents condensed onto one project in a free week. Herding with no field, so ferromagnetic.

## Prediction
*Written 2026-10-03, before running on this period.*
- **Class prediction:** ferromagnetic (herding in a free week): βJ_CW > 0 (P1), βJ_PL z_N2 ≥ +2 (P2). Per-period verdict on P1: **supported** if the sign is right and |t| > t_(D−1, 0.975) (leave-one-day-out jackknife); **weak** if the sign is right but not significant; **failed** if the sign is wrong.
- **P3 (consensus jump):** the share x₁ of the final-day dominant project shows an O4 'jump' (Δ ≥ 0.3, τ ≤ 2 windows, persistence ≤ 0.15), and βJ_CW ≥ βJ_s(q_eff) (first-order region). A jump with βJ_CW < βJ_s is scored as a field-driven step; a gradual rise counts against P3.
- **P4 (control):** the action-class βJ_CW is positive or ≈ 0 whatever the class.
- **P7 (prior):** |βJ_CW| < 2, below βJ_s(q), so no spontaneous first-order transition.
- **Minimum data:** ≥ 15 room blocks with N_b ≥ 3 at W = 30; otherwise n/a.
- **What would count against it:** the opposite sign of βJ_CW (P1), or, for an FM class, a positive βJ_CW that disappears under the within-agent permutation null N1 (spread carried entirely by agent fields, R1).

## Result
| Test | Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- | --- |
| P1 βJ_CW (primary) | > 0 | +4.88 (jackknife SE 0.24, t = +20.43, t_crit 2.78) | βJ = 0; N1 (within-agent permutation) mean -1.11, z_N1 = +6.3 | **supported** |
| P2 βJ_PL (agent fields) | z ≥ +2 | +7.28; z_N2 = +14.25, z_N1d = +16.13, z_N1 = +7.52 | N2 (circular shift) mean +4.90 | **supported** |
| O3 agreement ratio R | – | 3.45 | 1 = interchangeable agents | descriptive |
| P3 consensus jump (project labels) | jump, Δ ≥ 0.3, τ ≤ 2, persistence ≤ 0.15; βJ_CW ≥ βJ_s(q_eff) | jump (Δ = +0.51, τ = 0.42 win, persistence +0.27); q_eff = 4.1, βJ_s = 3.22, first-order region: yes | constant / linear fits | **failed** |
| P4 control: action-class βJ_CW | ≥ 0 or ≈ 0, any class | -1.96 (t = -2.32); action βJ_PL z_N2 = +0.62 | – | consistent |
| P5 held-out PL (coupled vs fields-only) | gain in ≥ 4/5 folds where abs(z_N2) ≥ 2 | 5/5 day folds improve | fields only | consistent |
| P6 plmDCA diagonal (secondary) | same sign as βJ_PL | z_N1 = +14.1 | N1 (9 draws) | agrees |
| P7 prior: abs(βJ) < 2 | – | βJ_CW +4.88; drift-corrected excess βJ_PL − N2 mean = +2.37 | – | fails (βJ_CW) |

**Robustness (O9; βJ_CW):** raw labels +4.87, q ≤ 4 +5.05, W = 15 min +4.80, W = 60 min +4.59, computer-use actions only (post hoc) +4.76, day fields +3.49.

**Post hoc** (added after the round-1 run, not pre-registered):
- z of βJ_PL vs a ±1-window local shift: +8.32. This tests alignment at the 30-min scale.
- Ownership index (share of agent-windows on projects one agent dominates): 0.07.
- Persistence P(same project next window): 0.52.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | z_N2 = +14.3; held-out gain 5/5 folds |
| D unfitted predictions | 1 | sign by goal mode: supported (not diagnostic on its own: βJ_CW > 0 in 11/14 tested weeks, whatever the mode) |
| G ground truth | 1 | herding onto shared repos matches the summary ("about nine agents converged") |

## Notes
- 2026-10-03 (round 1, post hoc): the pre-registered rule picked the final-day dominant repo (`village-event-log`), not the narrative's `civic-safety-guardrails`. The guardrails repo was touched by 11 agents, with a peak of 8 in one window, but its share shows no step (verdict 'none'). `village-time-capsule` peaked at 11 agents in one window, then declined. So #31 is a sequence of herding waves onto shared repos, not one consensus. Details: `data/processed/H11-potts-labor-vs-herding/G31/posthoc_named_projects.json`.
