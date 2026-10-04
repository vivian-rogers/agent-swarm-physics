# H118 × G35: #35 Test your game (2026-03-16 → 03-20)

**Verdict:** mixed
**Role:** exploratory (native (NE15 fork))
**Period:** regime II · mode C · 12 agents (#best 3, #rest 9–10) · rooms #best/#rest · 5 days (4 active h each). No split inside the period.

## Why this period
The NE15 fork: both rooms start from the same RPG (ancestor `abc7c37`) and the same #34 history, with different players. It is the only non-holdout event where two rooms run the same artifact as two copies, so it is the HH's own test. Game state (H07's lineage trees) is available at commit resolution only here.

## Prediction
*Written 2026-10-04 22:05 UTC, before running on this period.* Numbers in brackets are credences; verdict rules are in the main card.
- Content: τ_D ≤ 4 active h (agent-bootstrap upper bound ≤ 8 h) and M(d) covers 0 for d ≥ 2 (P1) [0.55]; q_∞^late ≤ the identical-kickoff band max (P2) [0.4]. HH kill: q_eq(d) lower bound above the band max on all 5 days [0.35].
- Game state (informed by H07, not blind): src q_code ≥ 0.85 at the end of day 1 and in [0.45, 0.75] at the end of #35; frozen core ≥ 0.40; identity excess X > 0 with key-permutation p < 0.05 (P3) [0.75]. The HH's game-state clause fails [0.8].
- Against: content q_eq flat over 5 days at its first-hour level (frozen) or above the band (rules field); code identity at the independent-replica product (no hot spots).

## Result
*Run 2026-10-04 (exploratory, non-holdout). bge style_resid; gte in brackets; agent × bin bootstrap 95% intervals. Figure: [`figures/g35_overlap.pdf`](figures/g35_overlap.pdf). Data: `data/processed/H118-forked-rpg-replicas/results/` (`results.json`, `code_overlap.parquet`).*

**Content.**
| Quantity | Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- | --- |
| q_eq first active hour | – | 0.51 (0.37) | relabel 0.80 | rooms apart from hour 1 |
| q_eq by day | – | 0.37, 0.49, 0.13, 0.39, 0.27 (0.27, 0.38, 0.20, 0.49, 0.24) | q_lag 0.24–0.30; q_rel 0.73–0.82 | no trend |
| M_late (days ≥ 2) | covers 0 | 0.07 [−0.03, 0.17] (0.12 [−0.01, 0.22]) | 0 | supported |
| τ_D | ≤ 4 h | 0.6 h [0.25, 80] (5.2 h, no decay) | unpowered (Amendment 1) | inconclusive |
| q_∞^late | ≤ band max; PI rule silent | 0.25 [0.11, 0.35] (0.29 [0.14, 0.39]); band rank 2/5; PI threshold 1.16 | band 0.01–0.83 (−0.22–0.79); 36a 0.62 (0.66) | no plateau seen; inconclusive (power 0.16–0.29) |
| HH kill (every day above band max) | does not fire | does not fire | – | – |

**Game state** (190 ancestor src files, 1,836 functions, 474 files).
| Quantity | Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- | --- |
| src q_code end of day 1 | ≥ 0.85 | 0.837 | q_ind 0.804 | narrowly missed |
| src q_code end of #35 | 0.45–0.75 | 0.500 | q_ind 0.384 | supported |
| frozen core (src) end of #35 | ≥ 0.40 | 0.500 (functions 0.892) | – | supported |
| identity excess X end of #35 | > 0, p < 0.05 | src 0.116 (p 6e-12); functions 0.029 (p 1e-41); same new value 0.0011 | hypergeometric key permutation | supported |
| HH clause "game state decays within a day" | fails | damage grows over 5 days (half after ≈ 6.5 active h), then freezes | – | failed (as predicted) |

Content verdict: mixed (memory supported; τ_D and plateau inconclusive; gte reverses τ_D). Game-state verdict: failed for the HH clause (slow, frozen and correlated damage). Period verdict: mixed.


## Scorecard (period-specific axes)
- C 1: day-1 overlap far below relabel; code excess against an exact null.
- D 1: P3 3/4 (informed by H07); P1 memory clause met; τ_D and plateau unpowered.
- E 1: the fork separates content within the first hour and code on the edit clock; code freezes at the 03-23 goal change.
- G 1: the forks' commit lineages (H07) match the rooms.

## Notes
- 2026-10-04: the 7 day-1 #best commits made on `rpg-game` before the move to `rpg-game-best` are part of the #best lineage (H07's rule). Statements made outside an agent's period room are dropped (Haiku 4.5's #best visit on 03-19/20 counts for #rest only); no agent fell below the 80% rule, so all 12 agents (3 + 9) are in.
- 2026-10-04: a scheme bug (commit index shadowing the function occurrence index in a join) was fixed before any function-level number was read.
