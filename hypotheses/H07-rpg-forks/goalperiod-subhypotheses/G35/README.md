# H07 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 2026-03-23)

**Verdict:** mixed
**Verdict (1b):** mixed (replication unchanged); native lead-designer failed
**Role:** native (was: exploratory; native (round 1b: lead designers))
**Period:** regime II · mode C · 13 agents · rooms #best (GPT-5.4, Claude Opus 4.6, Gemini 3.1 Pro) and #rest (10 agents, including the Claude Code agent) · 5 active days × 4 h. Split inside: none. The period opens with the split itself (NE15, 03-16; see [`../NE15/README.md`](../NE15/README.md)).

## Why this period
#35 is where the forks evolved: 357 of the 405 post-split non-merge fork commits. Goal-periods ranking: model 08 first ("two isolated subpopulations evolving forks from a common ancestor"). Both rooms had the same goal, so differences between the forks are team effects, not goal effects.

## Prediction
*Written 2026-10-03, before any repository history was fetched (main card, "Prediction": P1, P2, P3, P6, P7, P8 are end-of-#35 statements).* "End of #35" = the last first-parent snapshot before 2026-03-23 11:17 UTC.

## Result
Figure: [`figures/fig_clocks.pdf`](figures/fig_clocks.pdf) (src-file copy fraction vs. three clocks). The vertical curves are in [`../NE15/figures/fig_vertical.pdf`](../NE15/figures/fig_vertical.pdf). Data: `data/processed/H07-rpg-forks/` (`curves_commit`, `curves_day`, `clock_fits`, `commits`, `results.json` → `P1_steps`).

**Material.** Ancestor A (`abc7c37`): 465 files (190 src JS, 231 tests), 1,836 function bodies, 4,212 numeric parameters, 883 keyed content names (773 distinct), 543 entities, 3,919 identifiers. In #35:
- #best: 165 commits (161 non-merge, 490 file-touches). 59 by Opus 4.6, 52 GPT-5.4, 49 Gemini 3.1 Pro, plus 1 by Haiku 4.5 during its visit. Includes 7 commits the #best agents first made on the original `rpg-game` on day 1.
- #rest: 219 commits (196 non-merge, 325 touches) by 10 agents.

**Vertical copy fraction at the end of #35** (κ ≈ c except for numbers):

| Feature (n ancestor keys) | #best | #rest |
| --- | --- | --- |
| all files (465) | 0.686 | 0.811 |
| src JS files (190) | 0.579 | 0.663 |
| test files (231) | 0.732 | 0.918 |
| function bodies (1,836) | 0.914 | 0.946 |
| numeric parameters (4,212) | 0.904 (κ 0.900) | 0.997 (κ 0.997) |
| content names, keyed (883) | 0.896 | 0.999 |
| entity id → name (543) | 0.941 | 0.998 |
| identifiers, set survival (3,919) | 0.998 (+250 new) | 0.997 (+163 new) |
| content names, set survival (773) | 0.951 (+66 new) | 1.000 (+40 new) |

| # | Prediction | Observed | Null | Verdict |
| --- | --- | --- | --- | --- |
| P1 | gradual: c_files ∈ [0.2, 0.9]; identifiers ≥ 0.8; names ≥ 0.85; numbers ≥ 0.7; no commit > 50% of file divergence | c_files 0.686 / 0.811; identifiers 0.998 / 0.997; names 0.951 / 1.000 (keyed 0.896 / 0.999); numbers 0.904 / 0.997; largest single first-parent step 5% (#best) / 10% (#rest, a merge) of file divergence | c = 1 (no divergence) or a one-commit reset | supported |
| P2 | names ≥ identifiers ≥ numbers > files in both forks (rival: numbers most conserved) | #rest 1.000 ≥ 0.997 ≈ 0.997 > 0.811 (holds, with ties). #best: names 0.951 (keyed 0.896) < identifiers 0.998; numbers 0.900; files 0.686. Rival not supported: numbers are not above identifiers in either fork | — | failed in #best |
| P3a | per-commit μ of the two forks within 2×, closer than per active hour | μ ratio #best/#rest. Per commit: files 1.98, src 1.72, functions 2.11. Per hour: 1.71, 1.49, 1.83. Per file-touch: 1.15, 1.02, 1.21. Numbers and names: 26–294× under every clock | active-hour clock | failed (commit clock); the touch clock collapses code-level divergence (post hoc) |
| P3b | frozen core ≥ 30% of files; two-class beats one exponential | 63.7% of ancestor files untouched in both forks. BIC prefers two-class for #rest (commit and touch clocks) and #best (touch clock); not for #best per commit; never per hour. Curves are nearly linear over 5 days | single exponential | mixed |
| P6 | #rest ≥ 1.5× #best's commits and diverges further | 196 vs. 161 non-merge commits (1.22×; 219 vs. 165 with merges). #best touched more files (490 vs. 325) and diverged further on every feature. Per agent: ≈54 vs. ≈20 commits | — | failed |
| P7 | I_transform ≤ 0.1 × I_copy (numbers a possible exception) | Plain shuffle: excess ≤ 0 everywhere. Conditional null: #best numbers 0.045 bits (z ≈ 19) vs. I_copy 5.10; entities 0.004 bits; all others 0. Not identifiable for unique-valued features (files, functions, names) | shuffle and conditional nulls | supported (significant but small numeric rebalance in #best) |
| P8 | ≥ 90% of commits by own team; common history ends within 2 h of T0 | 98.5% (#best), 99.6% (#rest). The common history ends at A, the last commit of the last pre-split session: ≈ 0.5 active h before T0, or 68 h of wall-clock across a weekend (the prediction did not name the clock) | — | supported (active time) |

**Gradual code, punctuated content.**
- File and function divergence accrues in small steps: the largest single step is 5–17% of the end-of-#35 divergence.
- In #best, 59–77% of the name, number and entity divergence comes from two Gemini 3.1 Pro events, and 85–97% from the top three commits:
  - a merged branch `fix-crafted-items` (03-19), which also restructured `items.js`;
  - "Renamed generic items to thematic Aethermere names" (03-20).
- What changed in #best's content:
  - enemies renamed: Wolf → Timberfang, Orc → Bloodtusk Raider, Dragon → Elder Wyrm, Slime → Aetherial Ooze;
  - locations retitled ("Village Square" → "Millbrook Crossing");
  - rebalancing: XP thresholds all lowered by 50, ability mpCost cut (6 → 4 in six abilities), arena stat multipliers shifted.
- 67% of #best's changed numbers follow an (x → y) mapping shared with another key. This is the systematic part the conditional null detects.
- #rest changed almost no content (≈13 numeric parameters, 5 of them in place; 1 name). Its edits were mostly src bug fixes (34% of src files changed vs. 42% in #best). It modified fewer existing test files than #best (8% vs. 27%) but added more new ones (16 vs. 11).

**Mutation rate: a team policy for content, a touch clock for code.** Per file-touch, both forks lose ancestral src files at the same rate (μ ≈ 0.00135 vs. 0.00133). For content, the rates differ by one to two orders of magnitude under every clock. Whether a team rewrites the game's names and numbers looks like a choice: #best read "make it fun" as re-theming and rebalancing. It is not a per-edit hazard.

**Leakage inside #35.** One room visit (Haiku 4.5 in #best, 03-19 20:46 → 03-20 17:14), with 1 game-code commit to #best. Joint #general talk only after #best's last #35 commit. No cross-room searches. Shared innovations: 3, all convergent (details in [`../NE15/README.md`](../NE15/README.md)).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 1 | Copy information above the shuffle null for every feature; no day-blocked held-out prediction. |
| D unfitted predictions | 1 | P1, P7, P8 held; P2 (in #best), P3a and P6 failed. |
| G ground truth | 1 | Authorship follows rooms (98.5% / 99.6%). |

## Notes
- 2026-10-03: keyed content features break on restructuring. #best's 03-19 `items.js` change moved keys, so keyed names (0.896) understate survival relative to the key-free set measure (0.951).
- 2026-10-03: the conditional null for I_transform was added after seeing negative plain-shuffle values under strong copying (both reported).

## Round 1b native: content nucleation by the day's lead designer (DQ6)
**Role (round 1b):** native. *Prediction written 2026-10-04, before computing anything with the DQ6 lead designers.* Seen: the DQ6 rows (lead designer per room for 03-16, 03-17, 03-18; #best: GPT-5.4, Opus 4.6, Gemini 3.1 Pro in that order) and round 1's finding that two Gemini 3.1 Pro commits carry 59–77% of #best's content divergence; I have not looked up those commits' dates.

**Design.** For each main fork, the keyed content changes (content names and data numbers whose value at the end of #35 differs from the ancestor), attributed to the first-parent commit that last changed each key (round 1's attribution). Lead-designer share L = share of attributed content changes made by the room's lead designer on the commit's PT day (03-16/17/18 only; other days excluded), against the lead designer's share of that room's non-merge commits on the same days (C).
- **N35-L1.** In #best, L ≥ 0.5 and L > C. Credence 0.45 (the alternative is a trait: the same agent nucleates whatever its role that day).
- **N35-L2.** Across both forks and the three days, the agent who makes the largest single content commit of a room-day is the lead designer in ≥ 4 of the 6 room-days that have a content commit. Credence 0.35.
- **Reading.** L1 and L2 held → nucleation follows the designated role (a field); failed with the same agent dominating across days → a trait (H07-R1).

### Result (round 1b, run 2026-10-04)
Data: `data/processed/H07-rpg-forks/r1b/results_r1b.json` (`lead`). Content = inherited name and data-number keys changed at each first-parent step (net), 03-16 → 03-18 PT.

| Test | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| N35-L1 (#best: L ≥ 0.5 and L > C) | L = 0.00 of 87 content keys; the day-1 burst (66 keys) is by Gemini 3.1 Pro while GPT-5.4 was lead | lead designers' commit share C = 0.22 | **failed** |
| N35-L2 (top content commit of a room-day by its lead, ≥ 4/6) | 0/5 room-days with content (#best 0/3, #rest 0/2) | — | **failed** |
| Trait reading (post hoc summary) | Over all of #35, Gemini 3.1 Pro carries 426 of 497 #best content keys (86%), on lead and non-lead days alike; #rest changed 15 keys in total | — | descriptive |

**Reading.** Content nucleation in #best follows one agent (Gemini 3.1 Pro) whatever the designated role that day, which supports H07-R1 (nucleators are a trait) over a role field. n = 1 nucleator in one fork.

**Replication on corrected inputs.** Shared `copy_info` reproduces every end-of-#35 value exactly (max |Δ| = 0). All 405 post-split non-merge fork commits are in the DQ4 ledger, 0 automated, author agreement 405/405; 7 are flagged non-canonical only because the canonical copy of #best's day-1 commits is `rpg-game`. P6 on agent work: #best 51.3 vs #rest 19.6 commits per capita (was 53.7 vs 19.6): still failed. P8 on DQ6 rooms: #best 164/165, #rest 219/219 in #35 (all post-split: 98.5% / 99.2%): supported.
