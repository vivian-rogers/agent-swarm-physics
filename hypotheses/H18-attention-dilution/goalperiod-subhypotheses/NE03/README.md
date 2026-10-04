# H18 × NE03: chat fetch limit at a fixed roster and goal (#10a 2025-08-18/19 vs #10b 2025-08-20 → 08-22)

**Verdict:** failed
**Role:** native (round 1b, non-holdout; transition exception c)
**Period:** regime I · goal #10 "Complete as many games as you can" · N ≈ 7 · one room (#general) · 5 days (units 10a = 2 days, 10b = 3 days). NE03 (2025-08-20, CHANGELOG): "number of chat messages fetched into context limited"; the limit itself is not documented.

## Why this unit
DQ9's native test for H18: NE03 caps how much of the backlog can reach the model at a fixed roster, goal and room. Under the attention-budget reading, k is "what reaches the context"; a fetch cap truncates the oldest part of a large backlog. If the cap binds, messages far down the queue (high rank from the newest) should lose uptake after 08-20, while the newest messages keep theirs. Before the context ledger, regime-I periods before NE09 were excluded (the call-start rule was doubtful there); the ledger shows chat reached computer-use context throughout, so #10 is now usable.

## Prediction
*Written 2026-10-04 06:35 UTC, before any round-1b run on this unit (nothing computed on #10 by H18 before).*
Data: the round-1b ledger scheme (`scheme/build_ledger.py`; pending sets = ledger items received since the previous talk call; response = reply parent (primary) and mention (secondary)); units = (talk, agent sender) as on the card.
- **N3a (cap binds on old messages).** Per-pair uptake of senders whose newest pending message has rank > 10 (more than 10 messages newer than it) is ≤ ½ of its #10a value in #10b, while senders at rank ≤ 3 keep their #10a uptake within ±30%.
- **N3b (steeper dilution).** β̂ (M_pow, agent×day propensities) is larger in #10b than in #10a (difference > 0; CI reported).
- **Null:** no change across 08-20 (the cap is above typical backlogs at N ≈ 7, or chat mode re-fetches anyway).
- **Power caveat (stated before running):** 7 agents in one room on 4 h days; if either side has < 30 scored units at rank > 10, N3a is *underpowered* and the unit is *descriptive*.

**Verdict rule (fixed now):** supported if N3a holds (both clauses) and N3b has the predicted sign; failed if rank > 10 uptake in #10b is ≥ its #10a value; mixed otherwise; descriptive if underpowered.

## Result
*Run 2026-10-04 (`analysis/r1b_native.py`; `data/processed/H18-attention-dilution/r1b/native.json`, `r1b/G10/`). Units = (talk, agent sender); rank = the sender's newest pending message's position from the newest.*

| Response · side | uptake, rank ≤ 3 | uptake, rank > 10 | β̂ | k q90 |
| --- | --- | --- | --- | --- |
| reply · #10a | 0.035 (n 579) | 0.000 (n 53) | 1.11 | 20 |
| reply · #10b | 0.015 (n 1264) | 0.000 (n 98) | 1.03 | 17 |
| mention · #10a | 0.067 (n 579) | 0.019 (n 53) | 0.81 | 20 |
| mention · #10b | 0.035 (n 1264) | 0.000 (n 98) | 0.81 | 17 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N3a: rank > 10 uptake halves in #10b while rank ≤ 3 stays within ±30% | replies: no deep-queue reply on either side (0/53, 0/98), so nothing can fall; mentions: 1/53 → 0/98. Rank ≤ 3 uptake also halves (replies 0.035 → 0.015; mentions 0.067 → 0.035) | **fail** |
| N3b: β̂ larger in #10b | replies −0.08; mentions 0.00 | fail |

- **Reading:** after 08-20 uptake falls at every queue depth, not only at depth, which is not the signature of a fetch cap; something about the second half of the week (the goal's phase, or the newcomers of 08-18 settling into their own games) lowers engagement overall. Messages deeper than 10 in the queue were almost never taken up even before the limit.

**Verdict: failed** (by the pre-set rule: rank > 10 uptake in #10b is not below #10a; on replies the comparison is 0 vs 0).

## Notes
- 2026-10-04: folder created with the prediction (round 1b native layer, DQ9 cross-index).
