# H01 × NE15 (+ #voted-out, NE12 placebo): the real channel cuts, confirmatory

**Verdict:** pending
**Role:** confirmatory (locked holdout)
**Period:** 2026-02-09 → 03-20 (#30–#35; #32 and #34 held out), regime I/II, one whitening basis (regime II, fitted on non-holdout data) across the window. Transfer window 2026-06-01 → 06-19 (#45–#47, held out, regime III).

## Why this event
NE12 (02-25) changed visibility rules but separated no pair (H05), so it is a placebo. The channel was actually cut when #voted-out was populated (03-05/06, inside held-out #34) and at the #best/#rest split (NE15, 03-16, whose pre-split window #34 is held out). These are the strongest available interventions for D3.2 (coupling) vs D3.2′ (field).

## Prediction
*Written 2026-10-03 after exploratory round 1, before any holdout outcome was computed. Machine-readable in `../analysis/confirm_d32.py` (`PREDICTIONS`), which stores a hash of the main card's prediction section with its results.*
- **C1 (primary).** NE15 cut arm vs stay pairs: DiD of the rarefied residual cosine < 0, pair-clustered 95% CI excluding 0 and assignment-permutation one-sided p < 0.05 (expected −0.05 to −0.20).
- **C2.** Stay pairs: descriptive (a goal change shifts every pair).
- **C3 (primary).** Pooled TWFE over 02-09 → 03-20: β(co-location) > 0, z > 1.96.
- **C4 (placebo).** No pair separated across 02-25 (asserted); all-pair residual cosine does not drop at 02-25 (day-block bootstrap CI).
- **C5.** The cut arm's residual moves toward the rotation-null (field-only) level after the split.
- **C6 (transfer).** Held-out two-room days #45–#47: the P1 rule; P6 RE slope > 0 (direction); P9 βJ₀/n ≥ 0.5 expected again.
- **Overall.** Confirmed if C1 and C3 pass and C4 holds; refuted if C1 and C3 both have the wrong sign, or both CIs contain 0 with |effect| < 0.05; otherwise inconclusive.

## Result
Not run. `--dry-run` on non-holdout stand-ins (placebo #41 → #42; split 05-11, #40 → #41; TWFE window #39–#42; transfer #41–#42) runs end to end and asserts no holdout day is touched. Stand-in numbers (exploratory, not confirmation): no separated pair at the placebo boundary; split cut-arm DiD −0.24 (95% CI −0.32 to −0.17, permutation p = 0.006); TWFE β = +0.054 (z = 1.81). Output: `data/processed/H01-emergent-superagents-exist/confirm_dryrun/confirm_d32.json`.

## Scorecard (period-specific axes)
- **E**, **I**: to be scored after sign-off and the run.

## Notes
- 2026-10-03: run with `UV_OFFLINE=1 HF_HUB_OFFLINE=1 uv run --with sentence-transformers python analysis/confirm_d32.py --confirm --i-understand-this-uses-the-locked-holdout` only after sign-off; the script refuses without both flags. Power is low (~40 cut pairs, 5 post days).
