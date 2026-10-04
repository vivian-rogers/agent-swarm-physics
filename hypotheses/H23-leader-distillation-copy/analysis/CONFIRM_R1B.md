# H23 confirm re-freeze (round 1b), 2026-10-04

**Script:** `confirm_r1b.py` re-freezes `confirm_g45.py`, which is unchanged, as are `h23lib.py`, `h23run.py` and `build_messages.py`. The new script imports them and swaps inputs from outside, as `r1b.py` did. Target: #45 (leader = agent 30). Dry run on G44 (agent 28). Status: dry-run only, **not run on the holdout**.

## What changed
- **Inputs:** Copy information comes from `infra/shared/copy_info` (identical numbers), not from H07's folder. DQ6 checkpoint labels are used for agent 28 (0 relabelled). **C0-r1b, the item-14 amendment:** agent-30 messages before 2026-06-01 17:15:40 UTC (wrong model string) are not leader messages. They stay in the table as context. `APPLY_ITEM14 = True` is set and needs Vivian's approval. **Contexts use receiving-call visibility.** The 3 context messages are the latest posted before the producing call's `t_call` (`call_windows`, joined to the call as in DQ2). Before, they were the 3 messages before the message itself. z_ctx, prev_act and the lexical context-copy clause are rebuilt this way (the copy clause re-implemented, since `h23run` does room order internally). activity_bins, the work ledger, failures and nudge targets are not inputs of this design.
- **Predictions:** C1, C2 and C3 are unchanged. **C4-r1b:** same thresholds, on ledger-visible contexts. **C5-r1b:** leader > Kimi (p < 0.10) is required in both bge and gte. The gte corpus targets are embedded once, offline, and cached in `G44/r1b/`. R1 is rejected only if C1's Kimi clause and C5-r1b both hold.
- **Guards:** All of `confirm_g45.py`'s preconditions: committed and unmodified files, H02 and LOG disclosure lines. This script must also be committed. `holdout_ledger.check()`.

## Why
- **C5:** round 1b showed its only pro-distillation hint (bge p 0.08) vanishes in gte (p 0.43).
- **Contexts:** Standards §2 (a message acts at the receiving call); round-1 contexts include in-flight messages.
- **Item 14:** DQ6 shows about 11 minutes under a wrong model string.

## Holdout reuse (ledger)
- **#45 prior runs, other modality** (allowed): H02 (activity couplings), H04 (kernels).
- **Planned same-family users:** content: H12, H13, H16, H33, H36; lineage: H11, H15, H28.
- Whoever runs first on #45 content makes the others second users.
- Disclose in the H23 and H02 cards and in `LOG.md`; the script checks for these lines.

## Dry run (G44, v7-aug-64, 16 leader messages)
- Runs end to end. Contexts were matched to a ledger call for 385/454 period messages; the rest are humans or unmatched calls.
- Same as the original dry run, except C4 and C5: **C1** fail (Kimi clause p 0.27; Kimi has only 6 messages); **C2** pass; **C3** pass; **C4-r1b** pass (JSD to contexts 0.132, was 0.145; context-copy p 0.77 ledger vs 0.77 room order); **C5-r1b** fail (bge p 0.08 passes; gte p 0.43 fails).
- Output: `data/processed/H23-leader-distillation-copy/G44/dryrun_confirm_r1b/`.

## Recommendation
**Adopt with changes.** Vivian must approve the item-14 exclusion. A commit is then needed: the card has changed since `confirm_g45.py`'s check.
