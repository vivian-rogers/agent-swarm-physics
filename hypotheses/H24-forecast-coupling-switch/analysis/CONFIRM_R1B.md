# H24 confirm re-freeze on round-1b inputs (batch D, 2026-10-04)
Script: `confirm_r1b.py`, target #14. `confirm.py` is unchanged. Written before any look at #14 data. **Not run.**
## What changed vs `confirm.py`
- **Goal field.** Old: H24's own ĝ, whose kickoff part has cos 0.88 to the shared vector in #21. New: the shared `goal_fields` ĝ.
  - The field is now removed along ĝ plus every goal-text and kickoff chunk (multi-direction). This follows the vector-spins pitfall: one-direction removal leaks field into "coupling".
- **Both embedding models.** Shared regime-whitened statement vectors for bge-small and gte-modernbert.
  - Each C passes only if it passes in both models, fails if it fails in both, and is otherwise "model-dependent".
  - Old: bge only.
- **N2 placebo weeks:** shared fields and multi-direction removal (round-1b `explore.CFG`).
- **Style sensitivity.** `style_resid_period` vectors are refit on the period's own statements, per kind. This is the `style_resid` rule for a held-out period, where the shared file holds the regime fallback.
- **Predictions:**
  - C0: unchanged.
  - C1-r1b / C2-r1b / C3-r1b: the C1–C3 rules, now required in both models.
    - Reason: round 1b's step verdict is model-robust, but its cause is model-dependent (no step under bge; under gte a +0.16 step that N2 also shows). The ramp is significant in one model only.
  - **New C4-r1b:** the pair-level reading DiD (round-1b G21 native) on #14.
    - Statements move toward the owner of a document just read. Rule: mean DiD > 0 and owner-permutation p < 0.05, in both models.
    - Inconclusive with < 10 usable events. Credence 0.35.
    - The style-residualized DiD is reported beside it.
- **Inputs that do not apply:** activity bins, outages and the DQ8 trim (not H24 inputs).
- **Leading-@ target / ledger:** not used. Reading events come from agent narration (a claim).
- **New guards:** `holdout_ledger.check()` (strict on `--confirm`) and a commit check.
## Holdout reuse collisions (ledger L144)
- **#14: allowed.** No prior run. Disclosure is needed for planned users H20, H25, H32 and H36 (content alignment).
## Dry run (#21, non-holdout; `data/processed/H24-forecast-coupling-switch/confirm_r1b_dryrun_G21/`)
- **Executes** in about 4 min, including the raw computer-use text pass and both sentence-transformer models.
- **Field check:** ĝ equals the round-1b G21 field in both models (cos 1.000; 6 chunks each).
- **Style refit:** equals the shared vectors (cos ≥ 0.9999998; chat and intent).
- **Results:**
  - C0 pass (7/8 switched).
  - **C1-r1b fail:**
    - bge: ΔA_res +0.02 vs N1/N2 q90 0.12/0.13.
    - gte: +0.16 vs N2 q90 0.18.
  - C2-r1b pass: A_pre 0.38 / 0.41 vs rotation q95 0.07 / 0.04.
  - C3-r1b pass: ρ 0.72 / 0.57.
  - **C4-r1b pass:** 102 events. DiD +0.036 (p 0.02) and +0.030 (p 0.035).
  - Style sensitivity: +0.023 (p 0.13) and +0.028 (p 0.08).
- These reproduce the card's round-1b numbers.
- **Not evidence:** #21 is the exploration period.
## Recommendation
**Adopt with changes.** #14 has N = 6, so C1 is weak evidence either way. C4-r1b depends on how many reading events the narration of a personality-test week yields; it may come out inconclusive. Vivian should decide whether C4-r1b is primary (the mechanism transfer) or secondary.
