# H08 × NE03: chat fetch limit, read-out at a fixed roster and goal (#10a 2025-08-18/19 vs #10b 2025-08-20 → 08-22)

**Verdict:** descriptive
**Role:** native (round 1b, non-holdout; transition exception c)
**Period:** regime I · goal #10 · N ≈ 7 · #general · 5 days (10a = 2 days, 10b = 3 days). NE03 (2025-08-20): the number of chat messages fetched into context was limited; the limit is undocumented.

## Why this unit
DQ9's native test for H08 (context capacity cut in regime I). If the coupling is what enters the model call, a message that the ledger assigns to a receiving call but that the fetch limit drops from the prompt should get **no** read-out jump. The cap removes the oldest part of a burst, so the read-out discontinuity should vanish for messages deep in their batch after 08-20 and stay for the newest ones.

## Prediction
*Written 2026-10-04 06:42 UTC, before any round-1b run on this unit (H08 round 1 did not use #10).*
C9 rebuilt on the ledger (`analysis/visibility_ledger.py`): (message, recipient) pairs from `context_ledger_items`; o = 1 is the receiving call; pseudo-message null as on the card. Split by the message's rank in its receiving batch (1 = newest).
- **N03a:** the addressing jump at read-out, D_addr = G(1) − G(0) (all recipients; mention-based, plus the content-similarity version), for messages at rank > 10 in their batch is ≤ ½ its #10a value in #10b.
- **N03b:** for rank ≤ 3 it changes by less than ±30% (or both CIs overlap).
- **Null:** the cap does not bind at N ≈ 7 (bursts rarely exceed it), so nothing changes.
- **Power caveat (stated before running):** if either side has < 200 rank > 10 pairs, N03a is underpowered and the unit is descriptive.

**Verdict rule (fixed now):** supported if N03a and N03b hold; failed if the rank > 10 jump in #10b is ≥ its #10a value with overlapping CIs; mixed otherwise; descriptive if underpowered.

## Result
*Run 2026-10-04 (`analysis/visibility_ledger.py`, G10 block). Data: `data/processed/H08-context-is-the-coupling/r1b/G10/c9.json` (`ne03`). All units (o = 0 in flight or not); D = G(1) − G(0) in percentage points (cosine ×100), day bootstrap within side.*

| Side · batch rank | pairs | D_addr (mention) | D reply author | D content cosine |
| --- | --- | --- | --- | --- |
| 10a rank le3 | 1780 | +0.60 [-0.38, +1.08] | +0.44 [-0.22, +0.78] | -1.28 [-1.70, -0.63] |
| 10a rank gt10 | 621 | -3.79 [-3.85, +0.00] | -3.08 [-3.12, +0.00] | +0.09 [-5.80, +0.11] |
| 10a all | 2867 | -0.48 [-0.69, -0.05] | -0.42 [-0.52, -0.19] | -1.59 [-1.87, -0.49] |
| 10b rank le3 | 4093 | +0.11 [-0.27, +0.36] | +0.49 [+0.23, +0.89] | +0.02 [-0.83, +0.57] |
| 10b rank gt10 | 80 | — | — | — |
| 10b all | 4568 | +0.10 [-0.12, +0.31] | +0.53 [+0.37, +0.80] | +0.09 [-0.66, +0.70] |

- **N03a:** underpowered: only 80 rank > 10 pairs in #10b (< 200; pre-set floor), against 621 in #10a. Batches deeper than 10 messages almost vanish after 08-20 at the same roster and goal, which is what a fetch cap would do to the visible backlog, but the ledger counts every message posted, so this reflects fewer large bursts per receiving call, not truncation.
- **N03b:** rank ≤ 3: D_addr +0.60 → +0.11 (both CIs include 0); reply author +0.44 → +0.49.
- In #10 as a whole the read-out jump is weak in every response (regime I, N ≈ 7); the content jump is negative in #10a (recency).

**Verdict: descriptive** (underpowered by the pre-set rule).

## Notes
- 2026-10-04: folder created with the prediction (round 1b native layer, DQ9 cross-index).
