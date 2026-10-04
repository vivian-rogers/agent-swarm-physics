# H13 confirm re-freeze on round-1b inputs (batch D, 2026-10-04)
Script: `confirm_r1b.py`. `confirm.py` is unchanged; its helpers and verdict rule are imported. Written before any holdout data was read. **Not run.** The held-out units and the dry-run stand-ins are as in `confirm.py`.
## What changed vs `confirm.py`
- **Content: both embedding models.** Old: round 1's own bge whitening. New: shared DQ5 statement vectors for bge-small and gte-modernbert (`build.py` round-1b path, no dedupe).
  - Every C is scored per model. A C passes or fails only when both models agree, else "model-dependent".
  - Overall is CONFIRMED or REFUTED only if both models give it.
- **Style rivals.** H13's own S-a (C2, unchanged) plus the shared `style_resid_period` (new C2p-r1b).
  - C2p-r1b uses C2's numeric rule. Round 1b retention was 0.07–0.09.
  - For #45–#50 the shared file holds the regime fallback, so the script refits on the period's own chat statements (the `style_resid` rule). The #51 tail keeps the non-holdout period fit.
- **Talk (C5 → C5-r1b).**
  - Old: `activity_bins`, whole day, with a cross-day surrogate.
  - New: `activity_bins_fixed`, each day trimmed to the all-present window (DQ8 `all_present_window` over agents with ≥ 4 flips). The baseline is now 30-min block-shift surrogates (20 per day).
  - C5's thresholds are unchanged.
  - Reason: cross-day surrogates on untrimmed activity reject 28–34% of independent swarms (STANDARDS §3).
- **C3 transfer.** It now uses the same model's round-1b exploration fields.
  - **Bug fixed:** `confirm.py` reassigns `explore.COUNTED` to the held-out units before `explore_fields()` reads it. The real run would raise a KeyError. Its dry run passed only because stand-in names exist in the exploration file.
- **C1, C4 and C6: unchanged.**
- **Inputs not used:** the context ledger. C6 ("rooms carry coupling") is still co-movement, so the convergence impostor stays open; ledger reads are a round-2 item.
- **New guards:** `holdout_ledger.check()` for content and talk on every target, and a commit check.
## Holdout reuse collisions (ledger L073–L084)
- **All targets allowed.** There is no same-family run. Every target needs disclosure.
- **#45:** H02 and H04 ran activity timing there. C5-r1b talk Δ is the same modality but a different statistic.
- **#46–#50:** H04's NE21+NE23 run.
- **Competing planned users:** H01, H12, H20, H23, H26, H29, H30, H31, H33, H36, H38, H39. On the #51 tail: H12, H15, H20, H22, H29, H30, H33, H34, H39.
- C5-r1b's activity statistic is the item most exposed to the policy-item-2 judgement.
## Dry run (8 non-holdout stand-in units; `data/processed/H13-family-fields/confirm_r1b_dryrun/`)
- **Executes** in about 3 min.
- **Style refit:** equals the shared vectors (statement cos ≥ 0.9999998; agent-day ≥ 0.9999998).
- **Trim:** keeps 82–96% of minutes in 6 units, 40% in #44 and 48% in 51e.
- **Results (bge / gte):**
  - C1 5/7: RE 0.12 [0.03, 0.21] / 0.10 [0.02, 0.19].
  - S-a RE 0.00 / −0.01. C2p-r1b RE 0.01 / −0.00.
  - C3 median cos 0.96 / 0.94 (p 0.01 / 0.02).
  - C5-r1b talk RE −0.005 [−0.04, 0.03] / −0.009.
  - Overall CONFIRMED in both models.
- **Original dry run:** INCONCLUSIVE (C3 failed on round-1 fields).
- **Not evidence:** the stand-ins are exploration units, so C3 overlaps exploration by construction.
## Recommendation
**Adopt with changes.** Vivian must rule whether C5-r1b's activity statistic may be the second activity-modality use of #45–#50. The fallback is to score C5-r1b on the #51 tail only, where nobody has run an activity test.
