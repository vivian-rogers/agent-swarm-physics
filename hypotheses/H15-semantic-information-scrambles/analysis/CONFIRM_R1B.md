# H15 confirm re-freeze (round 1b), 2026-10-04

**Script:** `confirm_r1b.py` re-freezes `confirm_ne30.py`, which is unchanged. The new script imports the frozen helpers from `confirm_ne30.py` and sets `H15_ROUND=r1b` before any H15 import. Status: dry-run only, **not run on the holdout**.

## What changed
- **Inputs (via the round-1b switch):**
  - V_eng comes from `activity_bins_fixed`.
  - V_rel = 1 − the real-failure fraction (`turn_outcomes.failed`, `error_class`), replacing stderr.
  - V_out = DQ4 agent work commits per hour.
  - Context erasures come from the ledger (`reset_forced` vs `reset_consol`, per-call timing). The outcome is work commits per call.
  - Embeddings, leading-@ targets and the DQ8 trim are not inputs of this design.
- **V\*:** re-chosen by the pre-registered D2.6 rule on the corrected candidates. Regime I/II use V_eng; regime III uses V_rel.
- **Predictions:**
  - **C1-r1b** (NE30 successor): z > −2 on V_eng and V_rel (refutation-only). The rule is unchanged; the definitions changed.
  - **C2-r1b** (NE33 batch): z > −2 on V_rel (the new V\*) and on V_eng. Round 1 tested V_eng only.
  - **C3-r1b** (forced-erasure dip): on ledger work commits per call. DL meta ≤ −0.25 with CI < 0, and per-unit CI < 0 in ≥ 2/3 of units with ≥ 200 forced resets. Thresholds unchanged.
  - C4 and C5 unchanged.
  - **C3e** (new, descriptive): failure rate after a forced reset.
- **Ledger:** `holdout_ledger.check()` is now called for every target and blocks a same-family prior run. The original did not call it.

## Why
- **Buggy viability measures:** round 1 used `actions.error` (stderr) for V_rel, write turns for V_out and the buggy `activity_bins` for V_eng. Under the corrected candidates, D2.6 picks a different V\* in both regimes (round-1b synthesis, decision 2).
- **Erasure dip:** it replicated on independent timing and output data: −0.39 [−0.42, −0.35] in work commits per call, 7/9 periods. This makes the work-commit version the natural confirmatory statistic.

## Holdout reuse (ledger)
- **Same-modality prior run:** H05 used activity timing on #34 days 03-05..03-13, which overlap NE30.
  - C1 measures one successor's V_eng deficit, not pair coupling: a different statistic, but the same modality.
  - The ledger marks it "blocked unless the statistic is shown to differ". Vivian must accept that argument.
- **Other-modality prior runs** (allowed with disclosure): H02 (#45), H04 (#45–#50, NE21+NE23).
- **Competing planned users:** H01 (`confirm_r2.py`: work output and lineage on #43–#50 and the #51 tail; crew continuity on NE30); H33 (work output); H11, H23, H28 (lineage on #45).
- Disclose in the H15, H05 and H01 cards and in `LOG.md`.

## Dry run (stand-ins: GPT-5.4 in #35 for NE30; the GPT-5.6 triplet for NE33; non-holdout regime-III units)
- Runs end to end; no holdout day is read (asserted).
- C1: V_eng +0.01 (z 0.02), V_rel +0.09 (z 0.15). C2: V_rel −0.24 (z −0.65), V_eng +0.02 (z 0.07).
- C3: −0.386 [−0.42, −0.35]; per-unit CI < 0 in 7/9 units (not #36b, #37); passes.
- C4: +0.30 (z 1.71, k = 2). C5: +0.0067 (lo +0.0012). C3e: +0.27 (k = 9). Overall on the stand-ins: CONFIRMED. Output: `data/processed/H15-semantic-information-scrambles/r1b/confirm_r1b_dryrun.json`.

## Recommendation
**Adopt.** The rules are unchanged except for V\* and the outcome definitions. The NE30 activity-modality collision with H05 needs Vivian's explicit sign-off.
