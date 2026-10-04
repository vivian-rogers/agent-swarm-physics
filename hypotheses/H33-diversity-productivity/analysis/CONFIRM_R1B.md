# H33 confirm re-freeze (r1b), 2026-10-04: prepared, NOT RUN

`confirm_r1b.py` replaces `confirm.py` (untouched) for any holdout run. No holdout data was read. Vivian's sign-off is needed.

## What changed
- **Inputs (the round-1b pipeline, `H33_ROUND=r1b`).**
  - Output is log(1 + DQ4 agent work commits), with automated streams excluded. It was write turns.
  - The engaged-minute control comes from `activity_bins_fixed`.
  - Diversity is PR10 under bge (round-1 column) **and** gte (DQ5 white32, `statement_flags.self_repeat_gte`).
  - Copies and restatement dedup variants are reported only.
  - The context ledger, failures and leading-@ are not inputs: there is no coupling claim.
- **Eligibility.** The round-1b rule (work-commit share; units from #30 on). It mechanically drops held-out #22, #28 and #29; their ledger zeros are ambiguous. #32a/b, #34, #45–#50 and the #51 tail remain.
- **Predictions (all `-r1b`, because the outcome and the second model changed):**
  - C1-r1b: P1 must pass under both models. Credence 0.08 (was 0.10).
  - C2-r1b and C3-r1b: same thresholds, under both models. C3's credence drops from 0.65 to 0.55: round 1b's bge right-side slopes are a #51 property, and the #51 tail is a target.
  - C4-r1b: both models.
  - C5-r1b: PR15 bge on commits; credence 0.15. gte is reported because round 1b found the effect model-dependent.
- **Guards.**
  - Both flags are still required.
  - The commit check is kept.
  - A ledger gate is added.

## Holdout reuse collisions (ledger L200–L211: content_alignment + work_output, message content)
- **No target is blocked.** Executed runs on #32 and #34 (H05) and on #45–#50 (H02, H04) are activity timing, another modality.
- **Planned same-family users, disclosure needed:**
  - content: H12, H13, H26 and H36 on most targets; H06, H10 and H32 on #22 and #28;
  - work output: H01 and H15 on #45–#50 and the #51 tail.
- **Cost of running first.** H33 would consume these statistics first on up to 10 targets. The other users would then become second users.

## Dry run (`data/processed/H33-diversity-productivity/confirm_r1b_dryrun/confirm_results.json`, 54 s)
- **Setup.** Stand-ins #30, #31, #35, #38, #41, #42, #44 and 51t (08-24 → 09-07). All 8 units are eligible. Agent-days with PR10: 559 under bge, 581 under gte.
- **Results (bge / gte):**
  - b₁ +0.013 / +0.017 (p 0.63 / 0.45);
  - b₂ +0.022 / −0.026 (n.s.);
  - CV: every PR term makes the fit 0.4–2.9% worse;
  - C3 upper bound 0.17 / 0.07 SD.
- **Scores.** C1 fails, C2 holds, C3 holds, C4 fails, C5 fails: "null reading confirmed" on the stand-ins. No stand-in value sits near a threshold, so the thresholds stay.

**Recommendation: adopt, but run last.** It is a low-value null confirmation (Vivian: low priority). It should not consume the content and work-output statistics before H01, H12, H15 and H26.
