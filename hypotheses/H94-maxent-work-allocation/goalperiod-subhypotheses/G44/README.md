# H94 × G44: #best fine-tunes a leader; #rest picks its own goals (2026-05-26 → 05-29)

**Verdict:** failed
**Role:** native
**Period:** regime III · mode C · 15 agents · #best (assigned) / #rest (self-chosen) · 4 days. Units 44a, 44b; the native splits by arm (agent's modal room).

## Why this period
**Native: planned vs free arm on the same days.** #best had an assigned team task (planning: a few shared repos), #rest chose its own creative goals (ownership).

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts (`counts.json`: quanta, commits, agents, repos per unit). No D_k, price, κ or signature on real data.

- N1: top-repo share of quanta higher in #best than in #rest (0.75).
- N2: λ_own(#rest) > λ_own(#best) and ownership share(#rest) ≥ 0.5 (0.6).
- N3: κ(#rest) < 1 (own projects, even episodes) and κ(#best) ≥ 1 or its D_1 < 0.5 bit (team concentration) (0.45).
- Against: no arm difference in λ_own (CIs overlap and point difference < 1 nat).

## Result
*Run 2026-10-04. Arms by the agent's modal room in the period (#best = room 2, #rest = room 3). Results: `.../results/native_G44.json` and `G44.json` (per unit).*

| Arm | agents | repos | quanta | top-repo share | D_1 | ownership share | λ_own (95% CI) | κ episodes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #best (assigned team) | 5 | 6 | 146 | 0.27 | 1.50 | 0.91 | 10.2 [6.5, 9.7] | 0.59 |
| #rest (self-chosen) | 10 | 46 | 308 | 0.10 | 2.35 | 0.74 | 4.1 [3.3, 7.7] | 1.58 |

| Native test | Observed | Verdict |
| --- | --- | --- |
| N1 top-repo share #best > #rest | 0.27 vs 0.10 | supported |
| N2 λ_own(#rest) > λ_own(#best); ownership share(#rest) ≥ 0.5 | 4.1 vs 10.2 (reverse); 0.74 | failed (first part) |
| N3 κ(#rest) < 1; κ(#best) ≥ 1 or D_1 < 0.5 | 1.58; 0.59 and D_1 1.50 | failed |

The assigned team does not pool its work on one repo: each of its 5 agents works mostly on repos it owns (training data, evaluation, checkpoints), so ownership is *stronger* in the planned arm. Planning here means a division of the team task into owned parts, which max-ent with ownership already describes (D_final 0.13 bit, at the persistence floor 0.08). The free arm spreads over 46 repos with ownership share 0.74 and κ 1.58 (inside the BE band).

Per-unit replication fits: 44a ownership share 0.81, λ_own 4.8, residual 0.05·D_1; 44b 0.79, 6.0, 0.04.

## Scorecard (period-specific axes)
- E: 0 (the planned-vs-free contrast goes the other way on λ_own). G: 1 (DQ6 room assignment; the #best team task split into owned repos).

## Notes
- 2026-10-04: folder created by the round-1 agent.
