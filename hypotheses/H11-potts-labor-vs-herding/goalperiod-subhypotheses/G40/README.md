# H11 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 2026-05-11)

**Verdict:** P1 failed; P2 failed; P3 failed
**Verdict (1b):** mixed (native: work spread; hub worked as much as attended)
**Role:** native (round 1b: hub vs own worlds in work, DQ4 ledger; round 1: exploratory candidate)
**Period:** regime III · mode C · N = 15 at start · #universe-coordination + #rest · 5 active days. Class for H11: **FM-consensus**.

## Why this period
Shared interfaces and standards in a shared universe hub: consensus, so ferromagnetic. Regime III, with one dedicated coordination room.

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
| P1 βJ_CW (primary) | > 0 | -17.89 (jackknife SE 6.88, t = -2.60, t_crit 2.78) | βJ = 0; N1 (within-agent permutation) mean -15.59, z_N1 = -0.9 | **failed** |
| P2 βJ_PL (agent fields) | z ≥ +2 | +4.15; z_N2 = -0.13, z_N1d = -0.98, z_N1 = -1.79 | N2 (circular shift) mean +4.25 | **failed** |
| O3 agreement ratio R | – | 1.06 | 1 = interchangeable agents | descriptive |
| P3 consensus jump (project labels) | jump, Δ ≥ 0.3, τ ≤ 2, persistence ≤ 0.15; βJ_CW ≥ βJ_s(q_eff) | none (Δ = +0.12, τ = 0.02 win, persistence +0.10); q_eff = 2.0, βJ_s = 2.00, first-order region: no | constant / linear fits | **failed** |
| P4 control: action-class βJ_CW | ≥ 0 or ≈ 0, any class | +0.16 (t = +0.18); action βJ_PL z_N2 = -0.06 | – | consistent |
| P5 held-out PL (coupled vs fields-only) | gain in ≥ 4/5 folds where abs(z_N2) ≥ 2 | 1/5 day folds improve | fields only | not applicable |
| P6 plmDCA diagonal (secondary) | same sign as βJ_PL | z_N1 = -0.4 | N1 (9 draws) | disagrees |
| P7 prior: abs(βJ) < 2 | – | βJ_CW -17.89; drift-corrected excess βJ_PL − N2 mean = -0.09 | – | fails (βJ_CW) |

**Robustness (O9; βJ_CW):** raw labels -17.46, q ≤ 4 -17.89, W = 15 min -13.99, W = 60 min -11.69, computer-use actions only (post hoc) -23.26, day fields -21.45, rooms pooled -15.35.

**Post hoc** (added after the round-1 run, not pre-registered):
- z of βJ_PL vs a ±1-window local shift: +0.13. This tests alignment at the 30-min scale.
- Ownership index (share of agent-windows on projects one agent dominates): 0.26.
- Persistence P(same project next window): 0.94.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | z_N2 = -0.1; held-out gain 1/5 folds |
| D unfitted predictions | 0 | sign by goal mode: failed (not diagnostic on its own: βJ_CW > 0 in 11/14 tested weeks, whatever the mode) |
| G ground truth | 1 | hub plus own worlds gives spread by fields, not the predicted consensus |

## Notes
- 2026-10-03 (round 1): `the-universe` hub held 0.74 of labeled agent-windows from the start, and each agent also kept its own world repo. The occupancy is far steadier than binomial, so the uniform-field βJ_CW is strongly negative. That is specialization through fields (N1 reproduces it: N1 mean −15.6). βJ_PL against N2 is ≈ 0. The a-priori FM-consensus class was wrong for this week: the 'consensus' (the hub) was given by the goal, not reached.

## Round 1b: hub vs own worlds in work (native; DQ4 ledger)
*Design and predictions written 2026-10-04 07:18 UTC, before any work-space statistic was computed.* DQ9: #40 is one room, one shared artifact (the universe hub) plus each agent's own world, with 2,945 agent work commits by 13 agents (bulk commits common). Round 1 found spread by fields in attention (hub 0.74 of labelled agent-windows from the start, βJ_CW −17.9, z_N2 ≈ 0). H53 found that the hub was link-seeded 2.4 min into the kickoff.

**What I had seen:** the round-1 attention results above; 325 work-labelled agent-windows at W = 30; nothing about which repos carry #40's work commits.

- **W40-a:** work is spread by fields too: βJ_CW(work) ≤ 0 and z_N2(work) < 2.
- **W40-b:** agents commit mainly to their own world repos: the hub's share of work-labelled agent-windows is below its attention share by ≥ 0.2.
- **W40-c:** the ownership index (share of agent-windows on repos one agent dominates) is higher in work than in attention.
- **HH266 reading:** W40-b is what "attention herds (on the hub), work stays private (own worlds)" predicts for this week; a work share of the hub as high as its attention share counts against it.

### Result (round 1b, run 2026-10-04)
`analysis/round1b.py replicate` and `work` → `r1b/G40/round1b.json`, `r1b/work/G40.json`.

| Test | Prediction | Observed (attention / work) | Verdict |
| --- | --- | --- | --- |
| Replication (shared labels) | unchanged | βJ_CW −17.9 → −17.9 (t −2.6); z_N2 −0.1 → +0.1; q 4 → 5 | P2 "failed" → "weak" (z ≈ 0) |
| W40-a spread by fields in work | βJ_CW(work) ≤ 0, z_N2 < 2 | −17.4 (t −3.1); z_N2 +0.6 | **supported** |
| W40-b hub work share below attention by ≥ 0.2 | ≤ 0.54 | 0.73 (attention 0.74); the hub is the top work repo too | **failed** |
| W40-c ownership higher in work | work > attention | 0.27 vs 0.26 | **failed** (no difference) |

**Reading.** #40 is not "attention on the hub, work in private worlds". Agents committed to the shared hub as often as they mentioned it (0.73 of work agent-windows; 9 agents in one 30-min window), and to their own world repos for the rest; the occupancy is steadier than binomial in both spaces, so the uniform-field coupling is strongly negative in both and nothing is left beyond agent fields. Division of labor here is fixed staffing (fields), and it is the same in work and attention.

**Scorecard (round 1b, native):** D 1 (own-artifact spread predicted in work and observed); G 1.
