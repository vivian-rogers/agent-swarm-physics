# H11 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-23)

**Verdict:** P1 supported; P2 supported; P3 failed
**Verdict (1b):** supported (native: work herds)
**Verdict (r2):** R1 attachment G31 work: supported; R2 stigmergy G31 work: n.s. (+); R3 herding raises output G31: n.s. (+); θ < 1 G31: yes
**Role:** native (round 1b: herding measured in work, DQ4 ledger; round 1: exploratory candidate)
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

## Round 1b: the herding wave in work, not attention (native; DQ4 ledger)
*Design and predictions written 2026-10-04 07:18 UTC, before any work-space statistic was computed.* DQ9: #31 is the week where a field-free herding wave can be measured in work (1,391 agent work commits by 13 agents), not only in artifact attention.

**What I had seen:** round 1 on attention (βJ_CW +4.88, z_N2 +14.3; `village-time-capsule` peaked at 11 agents in one window); the round-1b attention timing run (βJ_CW +4.88, z_N2 +16.0 on shared labels); the work-project table for #31 (top three repos committed to by 11, 9 and 8 distinct agents over the week; top share 0.19); 286 work-labelled agent-windows vs 423 attention ones.

**State:** agent state (categorical, project, work ledger) at W = 30 (repo with the most agent work commits in the window), same estimators and nulls as attention (O1 βJ_CW with jackknife; O2 βJ_PL vs N2, N1d; ±1-window local shift; O3; co-work rate vs N2).

- **W31-a:** work herds: βJ_CW(work) > 0 with |t| > t_crit and z_N2(work) ≥ 2.
- **W31-b:** but more weakly than attention: work excess (βJ_PL − N2 mean) < attention excess.
- **W31-c:** the peak number of agents committing to one repo in one 30-min window is ≤ 6 (attention peaked at 11 on `village-time-capsule`).
- **W31-d:** in windows where an agent has both labels, its work repo equals its attention project in ≥ 50% of agent-windows (attention and work point at the same repo; the difference is intensity, not target).
- **HH266 reading** (counts against W31-a): z_N2(work) < 2 with a co-work excess near 0.

### Result (round 1b, run 2026-10-04)
`analysis/round1b.py replicate` and `work` → `data/processed/H11-potts-labor-vs-herding/r1b/G31/round1b.json`, `r1b/work/G31.json`.

| Test | Prediction | Observed (attention / work) | Verdict |
| --- | --- | --- | --- |
| Replication (shared labels) | unchanged | βJ_CW +4.88 → +4.88 (t 19.9); z_N2 +14.3 → +14.2; local-shift z +8.4 | unchanged |
| W31-a work herds | βJ_CW > 0, abs(t) > t_crit; z_N2 ≥ 2 | work βJ_CW +4.04 (t 10.7); z_N2 +7.2; local-shift z +4.5; held-out gain 5/5 days | **supported** |
| W31-b weaker than attention | work excess < attention excess | +1.87 vs +2.36 (z_N2 +7.2 vs +14.1) | **supported** |
| W31-c peak co-committers | ≤ 6 agents on one repo in one 30-min window | 9 (attention 11) | **failed** (larger wave than predicted) |
| W31-d same target | ≥ 50% of agent-windows with both labels | 0.69 | **supported** |
| HH266 reading | z_N2(work) < 2, co-location excess ≈ 0 | z_N2 +7.2; co-location 0.54 vs 0.47 shift mean (z +3.6), the same excess as attention (0.69 vs 0.62) | **not supported** |

**Reading.** #31's herding is in the work, not only in the links and mentions: up to 9 agents committed to one repo in the same half-hour (`village-time-capsule` and `village-event-log` carry the work onsets H27 found). 25% of the week's 24 work repos have a single committer, but 87% of work agent-windows are on repos with ≥ 2 committers: most projects are private, most work is shared (this reconciles H06's 0.79–0.91 singleton share with H11's herding).

**Scorecard (round 1b, native):** C 2 (work coupling beats N2, N1d and the local shift, held-out gain 5/5); D 1 (attention-derived herding predicts work herding); G 1.

## Round 2 (2026-10-05)
*Predictions: the card's Round 2 block (written 2026-10-05 03:30 UTC, before any round-2 statistic; amendment A1 after the synthetic validation, before real data). Units: whole period (#51: period units). Data: `data/processed/H11-potts-labor-vs-herding/r2/` (`results/real_r2.json`, `score_r2.json`).*

| Unit · channel | α [95% CI] (R1a) | α_FE | lag − lead (R1d) | replay inside: top share / exp(H) (fit · Yule · uniform) | ΔLL artifact − chat (R2a) | OR chat-read \| act · OR commits \| chat (R2b) | read − lead, chat · commits (R2c) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G31 · work (n = 101) | +0.84 [+0.36, +1.32] | +0.69 [+0.18, +1.19] | -0.02 [-0.61, +0.57] | ✓/✓ · ✓/✗ · ✗/✗ | +0.071 [-0.018, +0.160] | 1.96 · 1.89 | -0.41 [-0.82, +0.00] · -0.37 [-0.95, +0.21] |
| G31 · att (n = 185) | +0.33 [+0.11, +0.55] | +0.38 [+0.15, +0.61] | -0.36 [-0.64, -0.08] | ✗/✗ · ✓/✗ · ✗/✗ | +0.024 [-0.052, +0.100] | 2.06 · 1.72 | +0.31 [+0.02, +0.60] · -0.56 [-0.95, -0.18] |

| Unit | log RR herd vs solo, commits (R3a) | landed | matched pairs (mean log ratio) | θ crowding (R3b) | herd / solo windows |
| --- | --- | --- | --- | --- | --- |
| G31 (shared) | +0.01 [-0.32, +0.33] | +0.05 [-0.23, +0.32] | -0.09 ± 0.09 | +0.79 [+0.58, +0.99] | 166/113 |

Reading rules (card): R1a counts α with CI > 0; causal attachment needs α_FE > 0 and lag − lead > 0 together (A1); R2a counts ΔLL > 0 (artifact beats chat), with the CI-based count next to it; R3a counts log RR > 0. n.e. = not estimable (A1: < 5 chosen exposed rows), n.s. = CI includes 0.
