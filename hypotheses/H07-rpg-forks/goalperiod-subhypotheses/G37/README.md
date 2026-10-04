# H07 × G37: Pick your own goal! (2026-03-30 → 2026-04-02)

**Verdict:** mixed
**Role:** exploratory
**Period:** regime III · mode F (free choice) · 13 agents · rooms #best / #rest (split continues) · 3 active days × 4 h. Split inside: none.

## Why this period
A free-choice period in which one #best agent chose to return to the game. It tests whether the post-#35 freeze (P4) survives when the swarm is no longer told to work on the RPG.

## Prediction
*Written 2026-10-03, before any repository history was fetched (main card, P4):* commits per active day stay ≥ 80% below #35, and horizontal copy information changes by < 10% of its #35 drop (over all later periods combined).

## Result
| Test | Observed | Verdict |
| --- | --- | --- |
| activity collapse | 29 fork commits in 3 active days (9.7/day vs. 71.4 in #35; −86%) | supported |
| horizontal freeze, code and names | change in I_copy − null over #37: files −0.09 bits (2% of the #35 drop), names −0.07 (3%) | supported |
| horizontal freeze, numbers / functions | numbers −0.35 bits (most of the 24% post-#35 change), functions −0.18 | failed |

**One agent, one fork.** All 27 #best commits are by Gemini 3.1 Pro (03-31 and 04-01), working through issues #16–#24 on `rpg-game-best`: UI fixes, light-mode CSS, a bounty-board bug, two new main quests, and a map expanded from 3×3 to 10×10.
- Inherited content barely moved: vertical copy of numeric parameters 0.904 → 0.902, names 0.896 → 0.896.
- #best grew: new numeric keys 392 → 770, new entities 17 → 29, new names 108 → 120.
- Inherited code did change: src files 0.579 → 0.542, function bodies 0.914 → 0.895.

So the horizontal drop in numbers is growth on one side (the union-key statistic counts it), while the drop in functions is mutation of inherited code.

On the #rest side, 2 commits (GPT-5.2 relationship greetings; Opus 4.5 removing a stray submodule). A #rest agent (Sonnet 4.6) also fixed a quest-acceptance crash on the *original* `rpg-game` (03-31). Data: `curves_commit.parquet`, `horizontal_day.parquet`, `commits.parquet`.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| D unfitted predictions | 1 | Activity collapse held; the freeze held for files and names, not for numbers (growth) or functions (mutation). |

## Notes
- 2026-10-03: the union-key horizontal statistic mixes one fork's growth with mutation of shared keys. Read it alongside the ancestor-key identity, which moved ≤ 3% of its #35 change for numbers, names and files in all later periods (5% for src files), and 19% for functions.
