# H32 × NE42: #best and #rest merged into #universe-coordination for #40, split back for #41 (2026-04-27 → 2026-05-15)

**Verdict:** failed (merged pairs show no content transfer in #40; sign p = 0.39)
**Role:** exploratory
**Period:** regime III · spans #39 (mode I, two rooms), #40 (mode C, merged room), #41 (mode I, two rooms). Goal-confounded: each week has its own goal.

## Why this period
An A–B–A switch of exposure for the pairs that sat in different rooms in #39 and #41: the cleanest exposure manipulation in the non-holdout data (natural-experiments.md, NE42).

## Prediction
*Written 2026-10-03, before running on these periods.*
- **P9:** for ordered pairs (i, j) in different rooms in both #39 and #41 and both present in #40, ΔG_ij ≈ 0 in #39 and #41 and > 0 in #40. Test: pair-level sign test of ΔG(#40) − mean(ΔG(#39), ΔG(#41)) > 0, p < 0.10. [0.55]
- **Control:** pairs in the same room throughout show no systematic #40 increase beyond what the goal change gives everyone (difference-in-differences: split pairs' increase > same-room pairs' increase). [0.45]
- **Counts against:** split pairs' #40 ΔG not above their #39/#41 values, or #39/#41 cross-room ΔG clearly > 0 (transfer without exposure, i.e. common drive or cross-room channels such as shared repos).

## Result
*Run 2026-10-03 (round 1). Data: `data/processed/H32-information-current-leaders/ne42.json` (primary), `ne42_A2.json` (post hoc A2). Pair values: ΔG (% of held-out residual variance), seen-source gain in #40; unseen-source gain in #39/#41 for split pairs (they never saw each other there), seen-source gain for same-room pairs.*

| Test | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P9 split pairs: ΔG(#40) − mean ΔG(#39, #41) > 0 | mean +0.0116%, median +0.0233%; 27/51 pairs positive; #40 mean -0.0063% vs #39/#41 mean -0.0183% | sign test p = 0.39 | **failed** |
| Control: same-room pairs | mean +0.0383%; 33/70 positive | sign test p = 0.72 | – |
| DiD (split − same-room) | -0.0266% (90% CI -0.1727, +0.1122) | 0 | not > 0 |
| A2 post hoc (folds with ≥ 20 training messages) | split pairs +0.0103% (28/51 positive, p = 0.29) | – | same conclusion |

Reading: the pairs that could not see each other in #39 and #41 show no content transfer when they share #universe-coordination in #40 (their #40 mean is ≈ 0). #40 as a whole shows no transfer under the primary pipeline (T = −0.18%, driven by two unstable low-volume pairs; A2: −0.03%, p = 0.51). Merging a room did not switch on measurable pairwise content transfer. The week is goal-confounded (each week has its own goal). An untested possibility is that coordination in #40 ran through shared artifacts (repositories, documents) that this chat-content observable does not see.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| E interventional | 0 | predicted exposure switch-on of pair transfer absent |

## Notes
- 2026-10-03: prediction written before any H32 statistic on #39–#41.
- 2026-10-03: round 1 run; verdict by the card's rule.
