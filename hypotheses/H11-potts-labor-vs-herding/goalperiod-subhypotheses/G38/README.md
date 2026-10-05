# H11 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-27)

**Verdict:** P1 failed (significant); P2 failed (significant)
**Verdict (1b):** P1 failed (sig.); P2 failed (was sig.)
**Verdict (r2):** R1 attachment G38 work: n.s. (−); R2 stigmergy G38 work: n.s. (−); R3 herding raises output G38: n.s. (+); θ < 1 G38: no
**Role:** replication (exploratory (transfer))
**Period:** regime III · mode C · N = 12 at start · #best / #rest · 17 active days. Class for H11: **AF**.

## Why this period
Transfer: a 17-day shared objective (charity), so antiferromagnetic by the class rule.

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
| P1 βJ_CW (primary) | < 0 | +4.28 (jackknife SE 0.26, t = +16.71, t_crit 2.12) | βJ = 0; N1 (within-agent permutation) mean +3.16, z_N1 = +21.6 | **failed (significant)** |
| P2 βJ_PL (agent fields) | z ≤ 0 | +4.19; z_N2 = +2.07, z_N1d = +0.97, z_N1 = +12.72 | N2 (circular shift) mean +3.77 | **failed (significant)** |
| O3 agreement ratio R | – | 2.29 | 1 = interchangeable agents | descriptive |
| P4 control: action-class βJ_CW | ≥ 0 or ≈ 0, any class | +0.94 (t = +4.25); action βJ_PL z_N2 = +6.31 | – | consistent |
| P5 held-out PL (coupled vs fields-only) | gain in ≥ 4/5 folds where abs(z_N2) ≥ 2 | 13/17 day folds improve | fields only | inconsistent |
| P6 plmDCA diagonal (secondary) | same sign as βJ_PL | z_N1 = +8.3 | N1 (9 draws) | agrees |
| P7 prior: abs(βJ) < 2 | – | βJ_CW +4.28; drift-corrected excess βJ_PL − N2 mean = +0.41 | – | fails (βJ_CW) |

**Robustness (O9; βJ_CW):** raw labels +4.16, q ≤ 4 +4.51, W = 15 min +4.04, W = 60 min +4.45, computer-use actions only (post hoc) +4.24, day fields +3.31, rooms pooled +1.31.

**Post hoc** (added after the round-1 run, not pre-registered):
- z of βJ_PL vs a ±1-window local shift: +1.23. This tests alignment at the 30-min scale.
- Ownership index (share of agent-windows on projects one agent dominates): 0.12.
- Persistence P(same project next window): 0.85.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 1 | z_N2 = +2.1; held-out gain 13/17 folds |
| D unfitted predictions | 0 | sign by goal mode: failed (significant) (not diagnostic on its own: βJ_CW > 0 in 11/14 tested weeks, whatever the mode) |
| G ground truth | 0 | – |

## Notes
- 2026-10-03 (round 1): 17 days and 246 blocks give high power. βJ_CW is +4.3, but the within-day excess is small (βJ_PL − N2 mean = +0.4; z_N2 = +2.1; ±1-window local shift z = +1.2), so most of the positive βJ_CW here is day-scale structure.

## Round 1b (improved data, 2026-10-04)
*Replication (templated) on the shared deterministic `project_states` labels (`scheme/build_r1b.py`, `analysis/round1b.py replicate`; 99 nulls). Card predictions R1b-1 (replication) and R1b-2 (work space) were written before the run.*

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| βJ_CW (t) | +4.28 (+16.7) | +4.25 (+17.1) |
| z_N2 (βJ_PL vs circular shift) | +2.1 | +1.9 |
| local-shift z (±1 window, post hoc) | +1.2 | +1.2 |
| held-out PL gain (day folds) | 13 | 14/17 |
| P1 / P2 | failed (significant) / failed (significant) | failed (significant) / failed |

**Work space (R1b-2; agent work commits, DQ4 ledger, W = 30):**

| Space | labelled agent-windows | blocks (N ≥ 3) | βJ_CW (t) | z_N2 | local-shift z | excess βJ_PL − N2 | co-location (N2 mean, z) | ownership |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| attention | 1147 | 246 | +4.25 (+17.1) | +2.4 | +1.2 | +0.42 | 0.78 (0.75, +3.6) | 0.12 |
| work | 429 | 59 | +3.35 (+8.0) | +1.8 | +1.3 | +0.62 | 0.75 (0.71, +2.9) | 0.11 |

Agent-windows with both labels: work repo = attention project in 0.85. The attention top project holds 0.33 of attention and 0.24 of work agent-windows.

## Round 2 (2026-10-05)
*Predictions: the card's Round 2 block (written 2026-10-05 03:30 UTC, before any round-2 statistic; amendment A1 after the synthetic validation, before real data). Units: whole period (#51: period units). Data: `data/processed/H11-potts-labor-vs-herding/r2/` (`results/real_r2.json`, `score_r2.json`).*

| Unit · channel | α [95% CI] (R1a) | α_FE | lag − lead (R1d) | replay inside: top share / exp(H) (fit · Yule · uniform) | ΔLL artifact − chat (R2a) | OR chat-read \| act · OR commits \| chat (R2b) | read − lead, chat · commits (R2c) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G38 · work (n = 53) | -0.03 [-1.05, +0.99] | +0.05 [-0.54, +0.65] | +0.17 [-1.05, +1.40] | ✗/✗ · ✗/✗ · ✗/✗ | -0.147 [-0.437, +0.142] | 7.41 · 2.95 | -0.96 [-2.90, +0.97] · -1.48 [-2.99, +0.03] |
| G38 · att (n = 187) | +0.54 [+0.29, +0.78] | +0.55 [-0.08, +1.18] | -0.40 [-1.31, +0.52] | ✓/✗ · ✗/✗ · ✗/✗ | -0.056 [-0.158, +0.046] | 2.29 · 0.79 | -1.08 [-1.70, -0.46] · -0.71 [-1.56, +0.14] |

| Unit | log RR herd vs solo, commits (R3a) | landed | matched pairs (mean log ratio) | θ crowding (R3b) | herd / solo windows |
| --- | --- | --- | --- | --- | --- |
| G38 (shared) | +0.49 [-0.19, +1.17] | +0.63 [-0.01, +1.26] | +0.16 ± 0.07 | +0.73 [+0.43, +1.02] | 224/139 |

Reading rules (card): R1a counts α with CI > 0; causal attachment needs α_FE > 0 and lag − lead > 0 together (A1); R2a counts ΔLL > 0 (artifact beats chat), with the CI-based count next to it; R3a counts log RR > 0. n.e. = not estimable (A1: < 5 chosen exposed rows), n.s. = CI includes 0.
