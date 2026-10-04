# H07 × G36: Interact with other AI agents outside the Village! (2026-03-23 → 2026-03-30)

**Verdict:** supported
**Role:** exploratory
**Period:** regime II → III (F perma-computer-use lands 03-24) · mode C · 13 agents · rooms #best / #rest (split continues) · 5 active days × 4 h. Split inside: the regime boundary on 03-24 (no fork content changed on either side of it).

## Why this period
The first period after #35, with a goal unrelated to the game: the test of P4's "freeze" (horizontal copy information stops changing once commit activity collapses).

## Prediction
*Written 2026-10-03, before any repository history was fetched (main card, P4):* after the goal change on 03-23, commits per active day fall ≥ 80%, and horizontal copy information changes by < 10% of its #35 drop.

## Result
| Test | Observed | Verdict |
| --- | --- | --- |
| activity collapse | 3 fork commits in 5 active days (0.6/day vs. 71.4 in #35; −99%) | supported |
| horizontal freeze | I_copy(best; rest) − shuffle null unchanged (0.000 bits) for every feature type. The 03-23 README edits touched a file that already differed between the forks | supported |

All three #36 fork commits are README "for autonomous agents" cross-links, made by #rest agents in the spirit of the #36 goal:
- GPT-5.2 on #rest's repo;
- Haiku 4.5 and Sonnet 4.5 on **#best's** repo (cross-fork commits, no game content).

Other cross-room contact: room visits by Claude Code (03-23) and DeepSeek-V3.2 (03-26/27) to #best, and 12 explicit references by #rest agents to `rpg-game-best`, mostly on 03-23. None changed game content. Data: `data/processed/H07-rpg-forks/horizontal_day.parquet`, `leakage.parquet`.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| D unfitted predictions | 2 | Freeze and activity collapse as predicted, before the data were seen. |

## Notes
- 2026-10-03: the F boundary (03-24) leaves no trace in the forks because nothing game-related was committed after 03-23.
- Shuffle-null estimates carry Monte Carlo noise of about 0.002 bits between runs (100 draws; key order follows Python's per-process hash seed), so differences below about 0.01 bits are not meaningful.
