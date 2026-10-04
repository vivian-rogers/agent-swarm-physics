# H18 confirm re-freeze (round 1b), 2026-10-04

**Script:** `confirm_r1b.py` re-freezes `confirm_holdout.py`, which is unchanged. The new script imports `confirm_holdout.py`'s evaluator (C1–C6 rules) and `scheme/build_ledger.py`. Targets and stand-ins are unchanged. Status: dry-run only, **not run on the holdout**.

## What changed
- **Inputs (holdout ledger item 10):** the round-1b ledger scheme replaces round 1's call-start rule. Talk turns are ledger talk calls (`call_windows`). Pending set: k = `k_since_talk`, the ledger items received since the previous talk call. D2 timer wakes are ledger calls with `gap_kind = pause`. The response stays the pre-registered @-mention. The DQ2 reply-parent response is reported as a descriptive variant. It builds in a one-parent budget, so it cannot test dilution. C5's post side is the round-1b G35 build. activity_bins, embeddings, failures, the work ledger and nudge targets are not inputs of this design.
- **Mechanism:** `build_ledger.py` hard-codes `~holdout` filters. So the script builds a temporary view of the shared folder in which only the target days of `call_windows`, `context_ledger_turns` and `reply_pairs` carry `holdout = False`. The dry run uses the same view; it changes nothing on stand-in days (asserted). The view is deleted after the build.
- **Predictions:** C1–C6 are unchanged.
- **Ledger:** `holdout_ledger.check()` is now called. The original did not call it.

## Why
- **Visibility:** the call-start rule mislabels 65–70% of "invisible" messages (infra Known issues, DQ1).
- **Bands still hold:** on the ledger, every period exponent moved by ≤ 0.1 (pooled 0.63 → 0.66; regime I 0.61; regime III 0.68; #51 0.61; #51 D2 0.45). So every frozen band still sits where it was set, and no prediction needed changing.

## Holdout reuse (ledger)
- **Prior runs, other modality** (allowed with disclosure): H02 (#45); H04 (#45–#50); H05 (#34).
- **Planned same-family (addressing) users:** H08 (#28, #29, #45–#50, #51 tail), H11 and H28 (#28, #45), H29, H34 and H39 (#51 tail).
- Disclose in the H18, H02, H04 and H05 cards and in `LOG.md`.

## Dry run (same stand-ins as the original; B ≤ 20)
- Runs end to end; no stand-in day is held out (asserted).
- Same pass pattern as the original dry run: **C1** pass: β 0.63 [0.59, 0.70], sat. **C2** pass: 5/5 CIs exclude 0; no M_const winner. **C3** pass: ρ −0.49; CV(B̂) 0.29 < CV(p̄) 0.45. **C4** pass: 0.65, 0.52. **C5** fail: the stand-in pair #39 → G35 is not a split, so this is meaningless. **C6** pass: 0.63 [0.45, 0.73].
- Reply variant: β 0.74–1.00, recency wins everywhere, as in round 1b.
- Output: `data/processed/H18-attention-dilution/confirm_r1b_dryrun/results.json`.

## Recommendation
**Adopt.** Only the inputs change, and the predictions survive round 1b unchanged. Vivian should accept the shared-folder view as the mechanism for admitting held-out rows into the frozen builder.
