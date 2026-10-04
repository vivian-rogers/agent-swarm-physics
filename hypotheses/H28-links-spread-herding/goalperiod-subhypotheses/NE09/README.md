# H28 × NE09: chat interleaved into computer-use context (2025-12-20)

**Verdict:** failed
**Verdict (1b):** failed (native: premise void, ledger delay 17 s vs 18 s; switches 6.5× baseline in the blind window before the link can be read vs 3.5× after)
**Role:** native (round 1b: NE09 redone on context-ledger visibility; round 1: exploratory spanning test; NE09 is not in the locked holdout)
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

## Round 1b native: NE09 on context-ledger visibility
*Prediction written 2026-10-04 16:40 UTC, before any round-1b statistic was computed on any period.* **Seen beforehand:** the round-1 results above; DQ1's validation (`infra/data-quality/context_ledger.md`, item 5): prompt-token jumps track the ledger's new chat items from 2025-04 on, so chat entered computer-use context throughout, and the 2025-12-20 CHANGELOG entry was a timezone hotfix, not the start of interleaving. No ledger visibility delay, blind-window count or ledger-based hazard had been computed for H28's periods.

**Design.** Exposures are now ledger receipts: link m reaches recipient i at t_vis = the `t_call` of i's receiving call (`context_ledger_items` ⋈ `call_windows`). For every (link, susceptible recipient) pair (recipient off X at posting, same day):
- **visibility delay** d = t_vis − t_post;
- **blind window** (t_post, t_vis]: any switch of i to X logged in it comes from a call assembled *before* the link was posted, so it cannot be a response to the link;
- **read window** (t_vis, t_vis + 15 min].
Rates of switches to X per minute in each window are compared with the same pairs under the link time-shift null (±30–120 min, t_vis recomputed from i's receiving calls; 39 draws): E_blind = observed/baseline in the blind windows, E_read the same in the read windows. Pooled over the herding periods (#18, #19, #24, #25, #26, #30, #31) with a pair-cluster bootstrap; split pre-NE09 (#18, #19) vs post (#24–#31).

**Predictions** (credences in brackets):
- **N9a (premise void).** The median visibility delay before NE09 is within a factor of 2 of the median after it [0.7]. Counts against: pre-NE09 delays ≥ 2× post (chat really was gated before NE09).
- **N9b (co-burst, not contagion).** Pooled over the herding periods, E_blind > 1 with bootstrap 90% CI above 1, and E_blind ≥ 0.5 × E_read: agents switch to X at elevated rates *before* they could have read the link [0.55]. Counts against: E_blind CI includes 1 while E_read > 1 (switches follow reading: contagion).
- **N9c (P8 restated).** The median excess lag measured from t_vis (not posting) is not shorter after NE09 than before [0.65].

**Verdict rule for H28 here:** *supported* (links act through reading) if N9b fails in the contagion direction (E_blind CI ∋ 1 and E_read CI > 1); *failed* if N9b holds; *mixed* otherwise. N9a decides whether NE09 can be used as an intervention at all.

### Result (round 1b, run 2026-10-04)
`analysis/r1b_natives.py ne09` → `data/processed/H28-links-spread-herding/r1b/ne09_blind.json` (39 link shifts per period; link-message cluster bootstrap, 2,000 draws).

| Period | Pairs | Median delay (s) | Blind switches / min of blind time | E_blind | E_read (0–15 min) |
| --- | --- | --- | --- | --- | --- |
| #18 (pre) | 1,478 | 18 | 47 / 1,390 | 118 | 6.3 |
| #19 (pre) | 1,062 | 16 | 16 / 2,183 | 4.7 | 3.1 |
| #24 | 275 | 15 | 3 / 251 | 9.9 | 6.2 |
| #25 | 1,248 | 21 | 7 / 1,143 | 10.3 | 3.9 |
| #26 | 845 | 21 | 21 / 1,047 | 44 | 10.0 |
| #30 | 757 | 16 | 15 / 534 | 3.4 | 2.9 |
| #31 | 2,579 | 19 | 5 / 6,200 | 0.6 | 2.2 |
| **Pooled, all** | | | | **6.5 [5.3, 7.7]** | **3.5 [3.3, 3.7]** |
| Pooled, pre-NE09 | | | | 16.6 [12.3, 22.7] | 4.5 [4.1, 4.8] |
| Pooled, post-NE09 | | | | 3.7 [2.8, 4.8] | 3.1 [3.0, 3.3] |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N9a premise void: pre/post median delay within ×2 | 17 s vs 18 s (ratio 0.92). Round 1's pre-NE09 rule had put it at 82–140 s | **pass**: NE09 did not change when links became visible |
| N9b switches already elevated in the blind window, E_blind CI > 1 and ≥ ½ E_read | E_blind 6.5 [5.3, 7.7] vs E_read 3.5: switches are *more* elevated in the ~20 s before the link could be read than in the 15 min after | **pass** |
| N9c median excess lag from t_vis not shorter after NE09 | pre 2.5 / 7.5 min, post 2.5–7.5 (median 2.5): shorter by one 5-min bin | fail (at bin resolution) |

**Reading.** NE09 is not an intervention on link visibility: chat reached computer-use calls throughout (DQ1), and the ledger delay is ~17 s on both sides. Round 1's P8 premise was wrong, which explains its "failure". The blind-window test answers the question NE09 was meant to answer: recipients switch to X at 6.5× the shifted-link baseline in the seconds between posting and reading, more than after reading (3.5×). The link and the switch share a cause (the same burst, announcement or prompt); reading the link adds little on top. Only #31 behaves like contagion (blind 0.6 vs read 2.2), and #31 is exactly where H11 and H53 see a field-free wave.

**Verdict (H28 here): failed** (links act through a shared burst, not through being read). Caveat: blind windows are short (median 17 s), so blind counts are small (114 switches in all) and #18 dominates the pre-NE09 pool.
