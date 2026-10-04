# H07 × G34: Develop a turn-based RPG together while voting out Easter Egg saboteurs! (2026-03-05 → 2026-03-16)

**Verdict:** pending
**Verdict (1b):** pending (confirmatory, not run)
**Role:** confirmatory (locked holdout)
**Period:** regime II · mode M (teams / hidden saboteurs) · 12 agents (+1 −1: Gemini 3.1 Pro joins, Gemini 3 Pro leaves, NE30) · rooms #general and #voted-out · 7 active days × 4 h. Inside: kickoff message in prompt (03-10), consolidate tool (03-11), pause tool (03-13). Also covered by the NE30 holdout window.

## Why this period
#34 is the ancestor's own lineage: all twelve agents built `rpg-game` from scratch, and its state at T0 (`abc7c37`) is the common ancestor of the forks. It is the only place to test whether what H07 found after the split is a property of the artifact and the swarm, not of #35:
- persistent hot spots;
- the file-touch clock.

Exploratory H07 code reads only the T0 tree, never #34 commits, authors or messages.

## Prediction
*Written 2026-10-03, after exploratory round 1 (#35 onward) and before any #34 commit, author, message or file list was read. Same text as the main card, "Confirmatory predictions".*
- **C1 (persistent hot spots).** Per-file touch counts on `rpg-game/main` during #34 (non-merge commits; files present in A) predict which ancestor files were changed in **both** forks by the end of #35:
  - AUC ≥ 0.65;
  - the top quartile of #34 touches (tie-averaged ranks) has ≥ 2× the both-changed rate of the bottom half;
  - the co-change excess (2.4× for all files in exploration) falls to ≤ 1.5 when the independence expectation is computed within #34-touch quartiles.

  *Falsifier:* AUC < 0.55 or stratified excess ≥ 2.
- **C2 (touch clock transfers).** In the second half of #34, the src-file copy fraction relative to the snapshot at the end of 2026-03-10 PT, against cumulative touches to those reference files, has a single-exponential rate within a factor of 1.5 of the #35 value from the same function (pooled #best + #rest = 0.00194 per touch; #best 0.00211, #rest 0.00176). *Falsifier:* ratio outside [0.5, 2].

## Result
Not run. Script: [`../analysis/confirm_h34.py`](../../analysis/confirm_h34.py). Run it once with `--i-am-confirming`; it writes `data/processed/H07-rpg-forks/confirm_h34.json`. The default mode is a dry run on #35 stand-ins, which exercised the code path on 2026-10-03 and touched no #34 data. Its stand-in numbers are not evidence.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| E interventional | — | C2 is the pre-split → post-split prediction (rate fitted on one side of NE15, tested on the other). |
| I transfer | — | C1 and C2 are the transfer tests. |

## Notes
- The bare partial clone `data/raw/repos/rpg-game.git` holds the #34 commit metadata and trees needed. No blob contents from #34 are fetched or needed.
- Saboteur Easter eggs (the mode-M mechanic) would make a further confirmatory feature: are eggs purged faster in the forks than other inherited code? Identifying eggs needs #34 chat (held out), so it is left for the confirmation round.
