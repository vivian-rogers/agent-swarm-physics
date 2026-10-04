# H01 × NE30: same-family succession Gemini 3 Pro → Gemini 3.1 Pro (round 2, confirmatory)

**Verdict:** pending (confirmatory, not run)
**Role:** confirmatory (locked holdout)
**Period:** #34, 2026-03-05 → 03-13 (NE30 window 03-05 → 03-16, held out); swap on 03-09.

## Why this event
The cleanest member replacement in the village (same family, one-for-one) tests R7 (substrate independence): does the unit survive the swap
of a member, and does the successor take up the predecessor's place through the artifact rather than through memory?

## Prediction
*Frozen 2026-10-04 in `analysis/confirm_r2.py` (C1), after exploratory round 2 and before any holdout use.* Crews (strict writers of a shared project,
membership from #34's pre-swap days) that contained Gemini 3 Pro: (a) relative change of the crew's writes per bin on R_G over the 2 active days after
the swap + the predecessor's pre-swap share ≥ 0; (b) Gemini 3.1 Pro writes on a predecessor crew's project within its first 2 active days.
Both → supported; neither → failed; else mixed. n = 1 succession, so this is a strength-of-evidence test, not a rate.
Run together with C2 (allocation continuity across nights in every holdout unit), C3 (continuity after memory loss), C4 (NE24 artifact migration,
see `NE24/`) and C5 (R4d ranking).

## Result
Not run. Dry run on the non-holdout stand-in NE29 (`NE29/`): C1 mixed. Refuses without `--confirm --i-understand-this-uses-the-locked-holdout`.

## Notes
- Holdout reuse (policy in `hypotheses/holdout.md`): H15's `confirm_ne30.py` (unrun) also targets NE30 with per-agent write-turn deficits. This
  script's statistics are crew-level continuity of writes on shared projects: a different statistic, unexamined. Disclose in the H15 card and in
  LOG.md before running; commit the script first.
