# H94 × G40: Connect your worlds into a 3D universe (NE42 merge) (2026-05-04 → 05-08)

**Verdict:** supported
**Role:** native
**Period:** regime III · mode C · 13 agents · one merged room · 5 days. One unit. Compared with G39 (the same agents one week earlier).

## Why this period
**Native: NE42 merge as an intervention on the allocation.** One week after building their own worlds (#39), the same agents are told to connect them into one universe, in one merged room. The ownership price should fall, a hub should appear, and the episode concentration should rise.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts (`counts.json`: quanta, commits, agents, repos per unit). No D_k, price, κ or signature on real data.

- N1: λ_own(#40) < λ_own(#39) by ≥ 1 nat (0.6).
- N2: top-repo quanta share #40 ≥ 0.3 and the top repo is kickoff-named (0.6).
- N3: κ(#40) > κ(#39) (0.65).
- N4: ownership share of D_1 falls from #39 to #40 (0.6).
- Against: λ_own and κ unchanged within their CIs.

## Result
*Run 2026-10-04. Results: `.../results/native_G40.json`.*

| Week | quanta | top-repo share (named) | D_1 | ownership share | λ_own (95% CI) | κ episodes | own-repo share of quanta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| #39 own worlds | 380 | 0.11 (False) | 3.68 | 0.99 | 20.0 [16.2, 20.0] (cap) | 0.16 | 0.99 |
| #40 one universe | 364 | 0.73 (True) | 0.98 | 0.97 | 12.9 [8.8, 12.5] | 3.61 | 0.36 |

| Native test | Observed | Verdict |
| --- | --- | --- |
| N1 λ_own falls by ≥ 1 nat | ≥ 7.1 nats (from the cap 20 to 12.9; CIs disjoint) | supported |
| N2 top-repo share ≥ 0.3, kickoff-named | 0.73, named | supported |
| N3 κ rises | 0.16 → 3.61 | supported |
| N4 ownership share of D_1 falls | 0.99 → 0.98 | supported (by the letter; negligible) |

The NE42 merge moves 64% of the work quanta off the agents' own repos onto one named hub. The allocation stays at max-ent given margins and ownership (D_final 0.025 bit vs floor 0.027): the hub enters as a column margin (a field), and what remains structured is still who owns which world.

## Scorecard (period-specific axes)
- E: 2 (the merge changes λ_own, κ and the hub share in the predicted directions). C: 2 (at the persistence floor).

## Notes
- 2026-10-04: folder created by the round-1 agent.
