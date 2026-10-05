# H11 × G39: Build your own interactive world! (2026-04-27 → 2026-05-04)

**Verdict:** descriptive
**Verdict (1b):** descriptive (unchanged)
**Verdict (r2):** R1 attachment G39 att: n.s. (+); R2 stigmergy G39 att: n.s. (−); R3 herding raises output G39: n.e.; θ < 1 G39: yes
**Role:** replication (exploratory (transfer))
**Period:** regime III · mode I · N = 15 at start · #best / #rest · 5 active days. Class for H11: **none-I**.

## Why this period
Descriptive: each agent its own world. No sign prediction.

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
| P1 βJ_CW (primary) | none | -8.61 (jackknife SE 2.82, t = -3.05, t_crit 2.78) | βJ = 0; N1 (within-agent permutation) mean -8.63, z_N1 = +0.0 | **descriptive** |
| P2 βJ_PL (agent fields) | none | -1.84; z_N2 = -1.27, z_N1d = -1.40, z_N1 = -0.26 | N2 (circular shift) mean +0.31 | **descriptive** |
| O3 agreement ratio R | – | 0.29 | 1 = interchangeable agents | descriptive |
| P4 control: action-class βJ_CW | ≥ 0 or ≈ 0, any class | -1.00 (t = -1.56); action βJ_PL z_N2 = +0.67 | – | consistent |
| P5 held-out PL (coupled vs fields-only) | gain in ≥ 4/5 folds where abs(z_N2) ≥ 2 | 1/5 day folds improve | fields only | not applicable |
| P6 plmDCA diagonal (secondary) | same sign as βJ_PL | z_N1 = -0.2 | N1 (9 draws) | agrees |
| P7 prior: abs(βJ) < 2 | – | βJ_CW -8.61; drift-corrected excess βJ_PL − N2 mean = -2.15 | – | fails (βJ_CW) |

**Robustness (O9; βJ_CW):** raw labels -9.87, q ≤ 4 -5.94, W = 15 min -6.95, W = 60 min -7.92, computer-use actions only (post hoc) -6.84, day fields -9.22, rooms pooled -30.00.

**Post hoc** (added after the round-1 run, not pre-registered):
- z of βJ_PL vs a ±1-window local shift: -1.41. This tests alignment at the 30-min scale.
- Ownership index (share of agent-windows on projects one agent dominates): 1.00.
- Persistence P(same project next window): 0.92.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | z_N2 = -1.3; held-out gain 1/5 folds |
| D unfitted predictions | 0 | sign by goal mode: descriptive (not diagnostic on its own: βJ_CW > 0 in 11/14 tested weeks, whatever the mode) |
| G ground truth | 1 | per-agent worlds → strong spread, matching 'each agent builds a world' |

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication (templated) on the shared deterministic `project_states` labels (`scheme/build_r1b.py`, `analysis/round1b.py replicate`; 99 nulls). Card predictions R1b-1 (replication) and R1b-2 (work space) were written before the run.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| βJ_CW (t) | -8.61 (-3.1) | -9.08 (-4.5) |
| z_N2 (βJ_PL vs circular shift) | -1.3 | -1.1 |
| local-shift z (±1 window, post hoc) | -1.4 | -1.3 |
| held-out PL gain (day folds) | 1 | 1/5 |
| P1 / P2 | descriptive / descriptive | descriptive / descriptive |

**Work space (R1b-2; agent work commits, DQ4 ledger, W = 30):**

| Space | labelled agent-windows | blocks (N ≥ 3) | βJ_CW (t) | z_N2 | local-shift z | excess βJ_PL − N2 | co-location (N2 mean, z) | ownership |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attention | 517 | 79 | -9.08 (-4.5) | -1.2 | -1.1 | -1.90 | 0.12 (0.10, +1.9) | 1.00 |
| work | 377 | 71 | -30.00 (–) | – | – | +0.00 | 0.00 (0.00, –) | 1.00 |

Agent-windows with both labels: work repo = attention project in 0.97. The attention top project holds 0.09 of attention and 0.11 of work agent-windows.

## Round 2 (2026-10-05)
*Predictions: the card's Round 2 block (written 2026-10-05 03:30 UTC, before any round-2 statistic; amendment A1 after the synthetic validation, before real data). Units: whole period (#51: period units). Data: `data/processed/H11-potts-labor-vs-herding/r2/` (`results/real_r2.json`, `score_r2.json`).*

| Unit · channel | α [95% CI] (R1a) | α_FE | lag − lead (R1d) | replay inside: top share / exp(H) (fit · Yule · uniform) | ΔLL artifact − chat (R2a) | OR chat-read \| act · OR commits \| chat (R2b) | read − lead, chat · commits (R2c) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G39 · att (n = 63) | +0.51 [-0.02, +1.04] | +0.47 [-0.30, +1.24] | -1.06 [-2.30, +0.19] | ✓/✓ · ✗/✗ · ✗/✓ | -0.031 [-0.066, +0.003] | 3.54 · 1.65 | +0.07 [-1.13, +1.27] · +0.11 [-1.12, +1.34] |

| Unit | log RR herd vs solo, commits (R3a) | landed | matched pairs (mean log ratio) | θ crowding (R3b) | herd / solo windows |
| --- | --- | --- | --- | --- | --- |
| G39 (own) | n.e. | n.e. | – | +0.39 [+0.04, +0.73] | 0/0 |

Reading rules (card): R1a counts α with CI > 0; causal attachment needs α_FE > 0 and lag − lead > 0 together (A1); R2a counts ΔLL > 0 (artifact beats chat), with the CI-based count next to it; R3a counts log RR > 0. n.e. = not estimable (A1: < 5 chosen exposed rows), n.s. = CI includes 0.
