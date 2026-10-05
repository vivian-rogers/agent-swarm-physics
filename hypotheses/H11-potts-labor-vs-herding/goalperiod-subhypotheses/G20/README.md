# H11 × G20: Start a Substack and join the blogosphere (2025-11-17 → 2025-12-01)

**Verdict:** descriptive
**Verdict (1b):** descriptive (unchanged)
**Verdict (r2):** R1 attachment G20 att: supported; R2 stigmergy G20 att: n.s. (−)
**Role:** replication (exploratory (transfer))
**Period:** regime I · mode I · N = 8 at start · one room (#general) · 10 active days. Class for H11: **none-I**.

## Why this period
Descriptive: each agent its own Substack. No sign prediction.

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
| P1 βJ_CW (primary) | none | +2.18 (jackknife SE 0.34, t = +6.33, t_crit 2.26) | βJ = 0; N1 (within-agent permutation) mean -0.50, z_N1 = +4.6 | **descriptive** |
| P2 βJ_PL (agent fields) | none | +2.93; z_N2 = +1.88, z_N1d = +1.80, z_N1 = +5.24 | N2 (circular shift) mean +2.51 | **descriptive** |
| O3 agreement ratio R | – | 2.10 | 1 = interchangeable agents | descriptive |
| P4 control: action-class βJ_CW | ≥ 0 or ≈ 0, any class | +2.20 (t = +6.28); action βJ_PL z_N2 = +4.45 | – | consistent |
| P5 held-out PL (coupled vs fields-only) | gain in ≥ 4/5 folds where abs(z_N2) ≥ 2 | 8/10 day folds improve | fields only | consistent |
| P6 plmDCA diagonal (secondary) | same sign as βJ_PL | z_N1 = +9.3 | N1 (9 draws) | agrees |
| P7 prior: abs(βJ) < 2 | – | βJ_CW +2.18; drift-corrected excess βJ_PL − N2 mean = +0.42 | – | fails (βJ_CW) |

**Robustness (O9; βJ_CW):** raw labels +2.39, q ≤ 4 +2.34, W = 15 min +1.97, W = 60 min +2.25, computer-use actions only (post hoc) +2.56, day fields -0.97.

**Post hoc** (added after the round-1 run, not pre-registered):
- z of βJ_PL vs a ±1-window local shift: +0.50. This tests alignment at the 30-min scale.
- Ownership index (share of agent-windows on projects one agent dominates): 0.14.
- Persistence P(same project next window): 0.62.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | z_N2 = +1.9; held-out gain 8/10 folds |
| D unfitted predictions | 0 | sign by goal mode: descriptive (not diagnostic on its own: βJ_CW > 0 in 11/14 tested weeks, whatever the mode) |
| G ground truth | 0 | – |

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication (templated) on the shared deterministic `project_states` labels (`scheme/build_r1b.py`, `analysis/round1b.py replicate`; 99 nulls). Card predictions R1b-1 (replication) and R1b-2 (work space) were written before the run.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| βJ_CW (t) | +2.18 (+6.3) | +2.31 (+6.2) |
| z_N2 (βJ_PL vs circular shift) | +1.9 | +2.1 |
| local-shift z (±1 window, post hoc) | +0.5 | +0.8 |
| held-out PL gain (day folds) | 8 | 8/10 |
| P1 / P2 | descriptive / descriptive | descriptive / descriptive |

## Round 2 (2026-10-05)
*Predictions: the card's Round 2 block (written 2026-10-05 03:30 UTC, before any round-2 statistic; amendment A1 after the synthetic validation, before real data). Units: whole period (#51: period units). Data: `data/processed/H11-potts-labor-vs-herding/r2/` (`results/real_r2.json`, `score_r2.json`).*

| Unit · channel | α [95% CI] (R1a) | α_FE | lag − lead (R1d) | replay inside: top share / exp(H) (fit · Yule · uniform) | ΔLL artifact − chat (R2a) | OR chat-read \| act · OR commits \| chat (R2b) | read − lead, chat · commits (R2c) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G20 · att (n = 84) | +0.64 [+0.23, +1.06] | +0.66 [+0.00, +1.33] | -0.17 [-0.93, +0.59] | ✗/✗ · ✓/✓ · ✗/✗ | -0.008 [-0.178, +0.162] | 2.91 · 25.12 | +1.04 [+0.32, +1.76] · -1.61 [-4.71, +1.50] |

Reading rules (card): R1a counts α with CI > 0; causal attachment needs α_FE > 0 and lag − lead > 0 together (A1); R2a counts ΔLL > 0 (artifact beats chat), with the CI-based count next to it; R3a counts log RR > 0. n.e. = not estimable (A1: < 5 chosen exposed rows), n.s. = CI includes 0.
