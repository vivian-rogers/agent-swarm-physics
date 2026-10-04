# H28 × NE09: chat interleaved into computer-use context (2025-12-20)

**Verdict:** failed
**Role:** exploratory (spanning test; NE09 is not in the locked holdout)
**Design:** before/after comparison across goal periods. Before: #18, #19 (and #20, not built: no herding in H11 beyond the local shift, so not in the H28 period set). After: #24, #25, #26, #30, #31. All regime I, #general only. Confounded with goal and roster changes; at best descriptive evidence for axis E.

## Why this natural experiment
NE09 changed when a link posted in chat reaches an agent working in a computer session: before it, chat entered the model's context only at session boundaries (`events_core` turns); after it, at the next computer-use call (median turn gap 10–13 s). If links cause switches, the delay between a link being posted and the induced arrival should shrink at NE09. If link-arrival co-timing is common drive (both respond to the same prompt), NE09 should not change it.

## Prediction
*Written 2026-10-04, before running on any period.*
- **P8:** the median excess lag from link posting to the induced arrival (excess over the link time-shift baseline, 0–240 min, susceptible recipients) is shorter after NE09 than before: median over post periods < median over pre periods, and the share of excess arrivals in the first 15 min is larger after.
- **Counts against:** pre-NE09 latency ≤ post-NE09 latency, or no excess at all before NE09 (then the visibility rule, not the links, is in question).

## Result
*Run 2026-10-04 (`analysis/explore.py` → `latency` in each `G<NN>/round1.json`; assembled in `data/processed/H28-links-spread-herding/cross_period_round1.json`, key P8). Figure: [`../../figures/latency_ne09.pdf`](../../figures/latency_ne09.pdf).*

| Statistic | Pre-NE09 (#18, #19) | Post-NE09 (#24, #25, #26, #30, #31) | Prediction | Verdict |
| --- | --- | --- | --- | --- |
| Median excess lag (per-period medians) | 2.5, 2.5 min | 7.5, 7.5, 2.5, 2.5, 7.5 min | post < pre | **failed** |
| Share of positive excess in the first 15 min | 0.95 | 0.90 | post > pre | **failed** |
| Excess arrivals in the first 5 min, per 1000 exposed recipients | 154 | 86 | — | pre larger |
| Action-only switches (post hoc), median excess lag | 2.5 (#18), 7.5 (#19) min | 2.5–7.5 min | — | same picture |

The link-switch co-timing is **at least as fast before NE09**, when chat should not have reached a computer-use call until the session ended. It is not carried by chat replies: the same holds for switches made through computer-use actions only (post hoc).

So the tight co-timing is not mediated by agents reading the link during computer use. Two candidate readings:
- **Common cause:** links and switches are parts of the same coordination burst, posted by agents who are already working on X.
- **Hidden channel:** chat reached regime-I calls through logged-out turns (the visibility doubt H18 raised).

Either way, NE09 gives no interventional support for "links cause switches". Caveat: the pre/post periods also differ in goal, roster and N, so this is a confounded before/after comparison.

## Notes
- The pre-NE09 visibility rule (next `events_core` turn) is used for the hazard model in #18 and #19; the latency statistic is measured from *posting* time, so it does not depend on the visibility rule.
