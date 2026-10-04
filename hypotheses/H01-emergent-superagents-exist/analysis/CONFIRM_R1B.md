# H01 confirm re-freeze (round 1b), 2026-10-04

**Script:** `confirm_r1b.py` re-freezes `confirm_d32.py`, which tests D3.2 (NE15 split, #voted-out, NE12 placebo, transfer to #45–#47). `confirm_d32.py` is unchanged. `confirm_r2.py` (round 2, work ledger) is out of scope. Status: dry-run only, **not run on the holdout**.

## What changed
- **Inputs:**
  - Shared DQ5 statement vectors in two models (bge, gte), with round-1b per-regime whitening and the k = 40 ruler (fitted on non-holdout data). Round 1 used live bge only.
  - Chat restatements removed (each model's own `self_repeat` flag).
  - A style-residualized variant per model (`style_resid_period32`), descriptive only.
  - Shared goal table (fixes the #38 room swap) and context-ledger pair exposure (replaces `exposure`).
  - Activity bins, the DQ8 trim, the work ledger, failures and nudge targets are not inputs of this design.
- **Predictions:**
  - **C1-r1b** (NE15 cut-arm DiD < 0, CI excludes 0, permutation p < 0.05) and **C3-r1b** (TWFE z > 1.96) must now pass in both bge and gte.
  - **C1s-r1b** (new, descriptive): the style-residualized DiD is smaller than the whitened one.
  - **C6-r1b:** P9 (content mean-field βJ₀/n) dropped; P1 reported per model; P6 on ledger exposure.
  - C2, C4 and C5 unchanged; C4 must hold in both models.
- **Criteria:**
  - New overall label `model-dependent` (bge and gte disagree on C1 or C3); refutation needs both models.
  - `holdout_ledger.check()` now blocks the run on a same-family prior run. The original did not call it.

## Why
- **Instrument dependence:** in round 1b, P6's p < 0.01 held only with bge.
- **Style:** the #40 merge DiD fell from +0.17 (bge) / +0.10 (gte) to +0.06 / +0.01 after style removal. So part of the round-1 room effect is style convergence.
- **P9:** drives alone reproduce its value (H26). **Exposure:** the old `exposure` lag overstates visibility.

## Holdout reuse (ledger)
- **Prior runs, other modality** (allowed with disclosure): H05 on NE12, #32 and #34; H02 on #45; H04 on #45–#47 and NE21+NE23.
- **Same-family collision:** P9 (`curie_weiss_gain`) collided with the H02 and H04 runs. Dropping P9 removes it.
- **Competing planned content users:** #32/#34: H12, H16, H33, H36 (plus H10, H21); #45: 11 hypotheses. The first to run makes the rest second users.
- Disclose in the H01 and H05 cards and in `LOG.md`.

## Dry run (stand-ins: placebo #41 → #42, split 05-11, TWFE #39–#42, transfer #41–#42)
- Runs end to end; no holdout day touched (asserted); no pair separated at the placebo boundary.
- Split DiD: bge −0.240, gte −0.267. Style variants: −0.159 / −0.198.
- TWFE z: bge 1.97, gte 3.22. Style variants: 0.14 / 1.04.
- C6: P1 fails its size clause in both models (median ΔH −0.064 / −0.070). P6 is positive in both.
- Overall on the stand-ins: `confirmed`. Output: `data/processed/H01-emergent-superagents-exist/confirm_r1b_dryrun/confirm_r1b.json`.

## Recommendation
**Adopt with changes.** Vivian must accept the both-model rule. She must also decide whether a style-borne C3 counts against coupling: on the stand-ins the TWFE z falls to 0.1–1.0 once style is removed.
