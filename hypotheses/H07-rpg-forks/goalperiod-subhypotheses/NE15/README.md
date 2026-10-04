# H07 × NE15: the #best / #rest split and the two RPG lineages (2026-03-16 → last fork commit 2026-05-28)

**Verdict:** mixed
**Role:** exploratory
**Period:** spans #35 (regime II, mode C) → #36 (F perma-computer-use lands 03-24) → #37 (regime III, mode F) → #38–#44 (regime III), non-holdout days only (no fork commit falls on a held-out day). Two rooms: #best (GPT-5.4, Claude Opus 4.6, Gemini 3.1 Pro) and #rest (10 agents). 357 of 405 non-merge fork commits are in #35; #37 adds 29.

## Why this period
NE15 is the natural experiment that creates the system: one artifact (`rpg-game` at `abc7c37`, the state at T0 = 2026-03-16 16:20:05 UTC) copied into two isolated subpopulations. The test of inheritance and divergence spans the periods after the split: horizontal copy information between the forks, the independent-lineage bound, and leakage. Within-#35 statistics (vertical divergence, clocks, transformation) are in [`../G35/README.md`](../G35/README.md).

## Prediction
*Written 2026-10-03, before any repository history was fetched (main card, "Prediction"). As they apply across the split:*
- **P4.** Horizontal I_copy(best; rest), shuffle-corrected, falls monotonically day by day through #35, then changes by < 10% of its #35 drop over all later periods, because commits per active day fall ≥ 80% after 03-23.
- **P5.** ≤ 5 shared innovations, each traceable to a cross-room channel; ≤ 2 post-split commits on either main fork by the other room's agents; fewer shared innovations between #best and #rest than between the two #rest copies.
- **Model (independent lineages).** On ancestor keys, P(best = rest) = P(both unchanged); identical new values in both forks ≈ 0.

## Result
Figures: [`figures/fig_horizontal.pdf`](figures/fig_horizontal.pdf) (horizontal copy information per day; commits per day), [`figures/fig_vertical.pdf`](figures/fig_vertical.pdf) (vertical copy fraction vs. active hours, both forks). Data: `data/processed/H07-rpg-forks/` (`horizontal_day`, `curves_day`, `shared_innovations`, `leakage`, `leakage_summary.json`, `results.json` → `P4_horizontal`, `commits_per_active_day`).

| Test | Observed | Null / expectation | Verdict |
| --- | --- | --- | --- |
| P4a monotone decline in #35 | I_copy − shuffle null falls every day 03-16 → 03-20 for all 8 feature types. Files: 8.84 bits at T0 → 7.99, 7.15, 6.82, 5.36, 4.75 | no divergence: constant at T0 value | supported |
| P4b freeze after #35 (< 10% of the #35 drop) | files 4.5%, src files 5.6%, tests 1.8%, names 3.2%; functions 15%, entities 15%, numbers 24% | — | mixed (content features fail) |
| P4c activity collapse (≥ 80%) | non-merge commits per active day: 71.4 (#35) → 0.6 (#36), 9.7 (#37), 0.4 (#38–#44) | — | supported |
| Independent lineages | P(best = rest) on ancestor keys = P(both unchanged) exactly from 03-18 on (0 inherited files changed to identical content in both; 1 on 03-16/17, later overwritten) | identity bounded by P(both unchanged) | supported |
| Hot spots | 66 inherited files changed in both forks vs. 27.6 expected if the forks chose files independently (2.4×); P(both unchanged) 0.637 vs. product 0.556 | independence of which files change | homogeneous-hazard model rejected |
| P5a count of shared innovations | 3 events: 2 identical new files + 1 cluster of 4 abilities (5 keyed names, 3 new name strings); 13 generic identifiers aside | ≤ 5 | supported as events (borderline counted as items) |
| P5b traceable to a channel | none of the 3 is preceded by a room visit, cross-fork fetch, search or chat link | — | not supported: convergent repair (below) |
| P5c cross-fork commits ≤ 2 per fork | #best received 3 (1 game code, 2 README); #rest 1 (README) | ≤ 2 | narrowly not supported |
| P5d #best–#rest vs. rest–rest-week | rest-week never evolved (one README commit) | — | not testable |

**Reading the P4b failure.** The post-#35 drop in content features comes from #37, when Gemini 3.1 Pro alone made 27 #best commits ([`../G37/README.md`](../G37/README.md)). Vertical copy of inherited numbers barely moved (0.904 → 0.902), but #best added 378 new numeric keys (a 3×3 → 10×10 map, new quests). The horizontal measure runs over the union of both forks' keys, so it falls when one fork *grows*. On ancestor keys alone, P(best = rest) changed after #35 by 2% of its #35 change for numbers, 0% for names and entities, 3% for files and 5% for src files. The exception is functions (19%): the #37 fixes rewrote inherited function bodies. So the freeze holds for inherited content except code bodies.

**Shared innovations: convergent repair, not leakage.** All three are minimal fixes of defects present in the ancestor:
1. `src/battle-summary.js`: the one-line fallback `enemy?.displayName ?? enemy?.name`. #rest (Gemini 2.5 Pro) committed it at 18:08 UTC on 03-16, inside an achievements-spam fix; #best (GPT-5.4) at 18:16, "Use enemy displayName in battle won summary".
2. `src/tavern-dice.js`: `Math.floor(rngValue * 6) + 1` replacing `(rngValue % 6) + 1`, twice. #best (Gemini 3.1 Pro) on 03-16 19:41; #rest (Opus 4.5, Claude Code) on 03-17 18:25.
3. Abilities `execute`, `divine-shield`, `taunt`, `prophecy`: referenced by the ancestor's `class-specializations.js` but missing from `abilities.js`. Both forks defined them on 03-20: #rest (Sonnet 4.6, 17:01, "Add all 16 missing specialization abilities") and #best (Opus 4.6, 17:41, "level-up choices … new abilities"). Names and default parameters are identical, both derived from the shared ancestor reference.

**Leakage ledger (T0 → 2026-05-01).** Full list in `leakage.parquet`.
- **Room.** During #35 there was one visit: Haiku 4.5 (#rest) in #best from 03-19 20:46 to 03-20 17:14. It fetched `rpg-game-best`, committed a character-name validation fix, and pushed. #best agents spoke in #general only from 03-20 20:38 to 21:00, after their last #35 commit (20:13). The 03-19 evening #general session was #rest-only (76 messages). Later: Claude Code in #best on 03-23, DeepSeek-V3.2 on 03-26/27, Sonnet 4.6 moved on 04-02, and room reshuffles from 04-17 on (none touching the RPG).
- **Commits across forks (5).**
  - Haiku 4.5 → best on 03-20: game code.
  - Haiku 4.5 and Sonnet 4.5 → best on 03-23 (#36): README "for autonomous agents" cross-links.
  - GPT-5.4 → rest and rest-week on 04-03 (#38): fundraiser README notes.
- **Explicit artifact references** (url / git output / scheme-less ref) to the other team's fork:
  - #rest → #best: 8 in #35 (Haiku's visit plus two site views at 20:53–21:00 on 03-20), 12 later.
  - #best → #rest: 0 in #35, 5 later.
  - On day 1, both teams also used the shared original repo `rpg-game`. #best pushed its first 7 commits there (17:12–18:34 UTC) before moving to `rpg-game-best`. #rest's history never absorbed them.
- **Search.** 633 history searches; 4 mention the RPG; 5 query the other room (03-23 → 04-27, about outreach and room logistics, none about the game).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 1 | Copy information far above the shuffle null; the independent-lineage identity holds exactly. No held-out prediction. |
| D unfitted predictions | 1 | P4a and the independent-lineage identity held; P4b failed for content; P5's mechanism failed. |
| E interventional | 1 | The split produced gradual, monotone divergence of the predicted sign. The rate was not predicted from pre-split data (needs #34, see [`../G34/README.md`](../G34/README.md)). |
| G ground truth | 1 | Commits follow room membership (98.5% / 99.6% own-team); lineage divergence starts at the known split. |

## Notes
- 2026-10-03: the horizontal statistic on union keys mixes mutation of shared keys with growth of one fork. Report it next to the ancestor-key identity (which isolates mutation).
- Leakage counts are lower bounds. Identical-content matching cannot see a feature re-implemented after viewing the other fork. The Claude Code agent's fetches are not in `computer_use_turns`.
- 2026-10-03: team labels are fixed at the split. The 04-27 reshuffle moved Opus 4.6 and GPT-5.4 into #rest (and GPT-5.5 into #best), so after 04-27 labels and rooms differ. Only 2 fork commits fall after 04-27 (05-13 GPT-5.4 README on #rest, by then a #rest member; 05-28 Gemini 2.5 Pro). The leakage ledger stops at 05-01.
