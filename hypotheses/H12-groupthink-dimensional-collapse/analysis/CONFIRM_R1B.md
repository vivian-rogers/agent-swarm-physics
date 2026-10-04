# H12 confirm re-freeze (round 1b), 2026-10-04

**Script:** `confirm_r1b.py` re-freezes `confirm.py` (Amendment 2; unchanged). It imports `confirm.py`'s unit and day selection and its spin helper. Units, transitions and stand-ins are unchanged. Status: dry-run only, **not run on the holdout**.

## What changed
- **Inputs:** `activity_bins_fixed` with the DQ8 null (all-present-window trim, block-shift edge; plus a variant with H38's stall mask); statement vectors in both models (bge, gte; 64-d regime whitener); DQ5 `statement_flags` for restatements. Ledger visibility, the work ledger, failures and nudge targets are not inputs of this design.
- **Predictions:**
  - **C1-r1b:** activity mode above the trimmed edge in ≤ 1/2 of units. This replaces "k = 1 in ≥ 2/3".
  - **C1t-r1b** (new): talk mode above the trimmed edge in ≥ 2/3 of units.
  - **C2-r1b:** the VR/λ₁ threshold goes from 0.85 to 0.7, the card's pre-registered P2 value.
  - **C3** retired (descriptive only). **C4-r1b, C6-r1b:** both models. **C5-r1b:** both models and after removing restatements. **C7** unchanged (bge; gte descriptive). **C8-r1b:** DQ5 restatement share, both models.
- **Ledger gate (new):** without `--vivian-approved-activity-reuse`, C1, C1t and C2 run only on #28, #29 and the #51 tail.

## Why
- **Ledger item 8 / RE-A1:** C1–C3 and C5 were expected to fail as frozen. The round-1 market mode was the event-drop artifact. Under the calibrated null, activity modes survive in 7/24 units, talk in 21/24, content in 24/24 (both models).
- **C3:** the lull filter is biased (H25), and joint lulls nearly vanish on the fixed table.
- **C5:** fragile in round 1b (gte 11/16; restatements removed 9/15).
- **C8:** "loops" are restatement, not copying (DQ5).

## Holdout reuse (ledger)
- Activity/talk spectra are the Curie–Weiss family on targets with executed runs (#32/#34: H05; #45: H02; #46–#50: H04; holdout items 2–4), so they are blocked by default.
- Content statistics: no executed content run. Planned content users include H01, H16, H26, H33, H36 and others.
- Disclose in the H12, H02, H04 and H05 cards and in `LOG.md`.

## Dry run (stand-ins #38–#42, transitions #38→#42, free week #31; 50 surrogates)
- Runs end to end; no holdout day is read (asserted). Same all-pass pattern as the original dry run.
- **Activity:** above the trimmed edge in 1/5 units (C1-r1b pass). **Talk:** 4/5 (C1t pass). **C2:** 3/4.
- **Content:** C4 5/5 in both models. C5 holds in all four variants (4/4 or 3/3).
- **C6** median +0.50 / +0.51. **C7** bge 16.1 > 14.82 (gte 14.1). **C8** ρ −0.84 / −0.66.
- Output: `data/processed/H12-groupthink-dimensional-collapse/confirm_r1b_dryrun/confirm_results.json`.

## Recommendation
**Adopt with changes.** Vivian must approve the reversed C1 (scheduler mode), the new C1t and C2's 0.7 threshold, and decide on activity reuse of #32, #34 and #45–#50. Without that reuse, the activity and talk claims rest on 3 units.
