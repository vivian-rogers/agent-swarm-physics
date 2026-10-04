# H08 confirm re-freeze (round 1b), 2026-10-04

**Script:** `confirm_r1b.py` re-freezes `confirm_holdout.py` (unchanged). It imports `confirm_holdout.py`'s unit lists, stand-ins and `evaluate()`, plus the round-1b ledger modules. Status: dry-run only, **not run on the holdout**.

## What changed
- **Inputs (holdout ledger item 10):** the round-1b ledger scheme (`build_turns_ledger`, `visibility_ledger`, `erasure_ledger`) replaces round 1's call-start rule, `exposure` membership and H15's consolidation catalog. The read-out call is the call that received the message. Erasures are ledger `reset_forced` / `reset_consol`. Responses: the @-mention (primary, pre-registered) and the DQ2 reply-parent author. `load_calls` hard-codes `~holdout`, so the script installs an identical loader with the filter switched by mode. activity_bins, the DQ8 trim, the work ledger, failures and nudge targets are no longer inputs once CF3 is retired.
- **Predictions:** CF1, CF2, CF4 and CF5 thresholds are unchanged. **CF1b-r1b** (new): D_auth > 0 (CI) in ≥ 7/8 regime-III units. **CF3 retired.** CF4's reply-author version is reported.
- **Ledger:** `holdout_ledger.check()` is now called. The original did not call it.

## Why
- **Ledger item 10:** the frozen script built round-1 inputs. The call-start rule mislabels 65–70% of "invisible" messages, and the old kernel used buggy bins and the future-kick isolation rule.
- **Round 1b:** D_addr regime III 7/8 and D_talk 5/8, so CF1's bands still fit. The reply author jumps in 17/17 periods. NE41 holds on replies (−21% ± 7%).
- **CF3:** round 1b reversed its basis. The nudge response starts at the receiving call (Φ(1,5) 1.76 vs predicted 0.52). The #51-tail kick cell is planned by H12, H19, H30 and H39.

## Holdout reuse (ledger)
- **Prior runs, all other modality** (allowed with disclosure): H02 (#45); H04 (#45–#50); H05 (#32, #34; only CF5's fetch logs touch those days).
- **Planned same-family (addressing) users:** H18 (#28, #29, #45–#50); H11 and H28 (#28, #45); H29, H34 and H39 (#51 tail).
- Disclose in the H08, H02, H04 and H05 cards and in `LOG.md`.

## Dry run (original stand-ins: #42, #44, last 10 days of #51; #30, #31; CC agent #30, #31, #33)
- Runs end to end; no stand-in day is held out (asserted).
- **CF1** pass: addr 3/3, talk 2/3, refractory 3/3. The original dry run had talk 3/3.
- **CF1b** 3/3. **CF2** 5/5, floor 5/5.
- **CF4** pass: β_F −0.027 ± 0.011; relative −0.21 ± 0.03; β_V −0.029. Reply author: β_F −0.023 ± 0.004.
- **CF5** pass.
- Stand-in D values agree with round-1b G44 and G51.
- Output: `data/processed/H08-context-is-the-coupling/confirm_r1b_dryrun/dryrun.json`.

## Recommendation
**Adopt.** Inputs are switched and thresholds kept. Vivian should approve retiring CF3, so that H08 cedes the nudge kernel to H04/H43, and the new CF1b-r1b.
