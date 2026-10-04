# H19 confirm re-freeze (round 1b), 2026-10-04

**Script:** `confirm_r1b.py` re-freezes `confirm.py`, which is unchanged. The new script imports `confirm.py`'s `predict_one`. It runs with `H19_DATA=r1b H19_E1=trim`. Status: dry-run only, **not run on the holdout**.

## What changed
- **Inputs:**
  - H19's own g_eq comes from `activity_bins_fixed`, DQ8-trimmed: the all-present window, with explained joint silences from `outages_fixed` removed (`geq_r1b`).
  - H02/H03 round-1b estimates; H04 `K_week` and H05 two-block gains dropped (buggy table, not re-run).
  - Controls unchanged. k_llm counts deliveries by `exposure` room membership (not its buggy `lag_s`), and fit and prediction use the same definition. A ledger-based k_llm would need a refit (left open).
  - Embeddings, the work ledger, failures, nudge targets and ledger visibility are not inputs of this design.
- **Models and predictions:**
  - **C1-r1b (primary):** all six methods regressed on k_llm. This model is new, fitted only on exploratory round-1b estimates, and hash-locked: `r1b/results_trim/frozen_kllm_model_r1b.json`, sha256 `22c64e28…`.
  - **C2-r1b (secondary):** the old channel model (talk on k_llm, activity on x_att), refitted on round-1b data.
  - **C3 (secondary):** the P1 model (x_att), refitted on round-1b data.
  - Pass rule unchanged (≥ 70% coverage of 90% PIs, RMSE below the regime-only rival). The old buggy-table `results/frozen_channel_model.json` is no longer used.
- **Eligible periods:** #1, #9, #14, #15, #22, #28, #29, #43, #51 tail. Dropped: #45 (H04 ran Hawkes there); #32, #34 (H05's executed run: Curie–Weiss family / same modality).
- **Guards:** `--confirm` refuses if any frozen-model hash changes; `holdout_ledger.check()` is now called (the original did not).

## Why
- **Ledger item 9:** the round-1 frozen model was fitted on `activity_bins`, which dropped about half of all events.
- **Day edges:** the activity gain's rise with x_att was the operator's day edges. Its slope goes from +0.18 to −0.03 after trimming, so the round-1 channel model is withdrawn.
- **k_llm:** on trimmed gains it is the one control with a positive, significant slope for 6/6 methods. This is still post hoc (chosen in round 1 from 16 controls), which is why it needs the holdout.
- **Ledger items 2 and 4:** these block #45 and #32/#34.

## Holdout reuse (ledger)
- No prior run on the nine eligible targets; all checks return `allowed`.
- Planned same-family competitors (first runner consumes): H38's equal-time gain on the same 9 periods (item 5); H25 Curie–Weiss on #1, #9, #14, #15, #22, #43; H12 on #28, #29, #51 tail; H03 Hawkes on #9–#43; kick-response users (H36, H30, H39).
- Disclose in the H19 and H38 cards and in `LOG.md`.

## Dry run (stand-ins #24, #41; these were fitted, so the numbers are meaningless)
- The code path runs end to end: freeze, then hash check, then sealed predictions (12), then scoring of 4 own-gain cells.
- C1-r1b PASS (coverage 1.0, RMSE 0.064 vs rival 0.072); talk-only FAIL; C2-r1b FAIL; C3 FAIL. Without flags, the script refuses.
- Output: `data/processed/H19-loop-gain-collapse/r1b/confirm_r1b_dryrun/`.

## Recommendation
**Adopt with changes.** Vivian must approve the post-hoc k_llm model as the primary. She must also accept the re-scoped period list. The frozen JSONs live in gitignored `data/`: keep them (or commit their hashes, which are already in the script) before any rebuild of `r1b/results_trim`.
