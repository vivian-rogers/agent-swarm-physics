# H41 confirm re-freeze (round 1b), 2026-10-04

`confirm_r1b.py` replaces `confirm.py` (untouched) for any holdout run. Written before any holdout use. Not run on the holdout.

## What changed
- **Inputs: no change was needed.** H41 already ran on the context ledger, DQ2 and statement flags. Activity bins, embeddings, work, failures and nudges are not inputs.
- **Two pipeline fixes:**
  1. **Room index (new bug, found here).** `scheme/h41core.load_skeleton` keeps `rooms_timeline` rows with `te >= t_min − 1 day`. Open segments (`t_end` null) fail that test and are dropped, so `RoomIndex.at` returns an agent's previous room.
     - Share of stale lookups, for agents in the table, on non-holdout windows: #51 07-06..07-24 **61%**, #51 08-24..09-05 **70%**, #38 5%, #42 0%.
     - The typical error is #general read as an old onboarding room or #focus.
     - Fix: the script re-sets `sk.rooms` with open segments kept, before any statistic. This changes room0, the cross-room labels (C2, C3) and isolation.
  2. **C4 isolation (ledger item 16).** The old check flagged 671 "isolated" adoptions in the T4 stand-in, only 3 of them acausal. It was evaluated at use time only, on the stale index, against `sk.agents` only.
     - **C4-r1b** uses the card's definition: only non-#general rooms, with no other roster agent (Claude Code excluded) in any of them during [t0, t_use], and never in the item's first room.
- **Unchanged:** C1, C2, C3, C5, C6 and the overall rule. The seal is new (`sealed_r1b_<mode>.json`).
- **Guard.** Adds a commit check and the ledger gate. H41 has no ledger entries; it is checked as message content / cascade.

## Why
- Ledger item 16 requires the C4 fix.
- The room bug was found while diagnosing it. It voids the room labels wherever segments are still open, which in practice means #51.

## Holdout reuse
- No same-family run on the targets. H04 ran activity timing on #45–#50.
- Planned users: #51 tail (H14, H18, H20, H22, H29, H30, H34, H39); #47 (H29, H30, H35, H36, H38, H39); #28 (H10, H32, H34, H36).
- H41 is not yet in `infra/data-quality/holdout_ledger.json`. Add it before any run.

## Dry run (#51 08-24..09-04, #42, #30, #51 07-06..07-23)
- Executes end to end. All criteria pass: C1, C2, C3, C4-r1b and C6. The original dry run had C1 and C4 failing.
- **T1 stand-in J_mh:** 12.9 [7.4, 25.7], against 0.60 [0.11, 1.03] with stale rooms. The card's "T1 may fail" warning was this bug. T1 cross-room robust acausal share: 0.46.
- **T4:** 0 isolated adoptions, both under the new rule and under the old rule with fixed rooms, so C4 passes vacuously. The test has no power on this stand-in.
- T2 and T3 are unchanged (no open segments).

## Recommendation
**Adopt with changes.**
- Round-1 #51 results (G51 native: #focus bridging and cadence; J_mh) and #38's room labels used the stale index. Re-run them before trusting the round-1 G51 verdict.
- Add H41 to the ledger.
- Fix `load_skeleton` itself; it is outside this task's edit scope.
