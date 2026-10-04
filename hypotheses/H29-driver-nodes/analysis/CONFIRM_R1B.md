# H29 confirm re-freeze (round 1b), 2026-10-04

`confirm_r1b.py` replaces `confirm.py` (untouched) for any holdout run. Written before any holdout data was read. Not run on the holdout.

## What changed
- **Visibility.** DQ1 ledger units (`build_unit_ledger`, `H29_DATA=r1b`). Every invisible row is now strictly invisible (`C_MAX_S = ∞`). The old rule was H18's call-start rule.
- **Content.** Both embedding models: bge (primary) and gte, each whitened in its own basis.
- **Predictions.**
  - **C1-r1b:** the named jump passes C1's rule under both models.
  - **C2-r1b:** the CI clause (upper CI < 0.05) now applies to the #51 tail only, under both models. In G47/G45 only the point estimate must be < 0.03.
  - **C3-r1b:** κ_pre < 0 in the tail. The clause "> 30% of invisible rows from call windows > 30 s" is dropped.
  - **C7-r1b (new):** the reply-graph network (DQ2) predicts held-out 2-h spread better than volume. Its gte value is reported.
  - C1b, C4, C5 and C6 are unchanged.
- **Guard.** Same preconditions as before (commit check, LOG.md and card disclosure lines), plus `holdout_ledger.check()`.

## Why
- Ledger item 12 / RE-V2: re-freeze on ledger visibility.
- DQ5 two-model rule.
- C2: under the ledger the strictly invisible control rows shrink (G41 867 → 566), so CIs widen in two-room weeks. Round 1b already calls those weeks underpowered.
- C2 disclosure: the G38 stand-in dry run (upper CI 0.063) prompted this check. The stand-in is non-holdout.
- C3: the old clause measured the H18 rule's bias, which the ledger removes. The negative κ is co-response.
- C7: round 1b's reply network gave pooled ρ 0.23 [0.05, 0.39] under bge.

## Holdout reuse
- **G47:** H04 ran activity timing there (another modality). Planned users of the same family: H12, H13, H26, H33, H36.
- **#51 tail:** no run. Planned users: H08, H18, H34, H39 (same family) and 10 others (same modality).
- **G45 (optional):** H02 and H04 runs; H23 plans message content.
- Disclose in `LOG.md` and in the H04, H02 and H23 cards (the script checks for this).

## Dry run (r1b/G38 for G47, r1b/G51d for the tail; both models)
- Executes end to end.
- **Address gating holds.** Tail named jump 0.056 bge / 0.068 gte, both CIs > 0. Unnamed jump 0.012 / 0.007.
- C1-r1b, C2-r1b, C3-r1b, C4 (bge) and C7-r1b pass.
- C1b fails (G38 named jump < 0, as in round 1).
- C5 fails (ρ 0.25).
- **C6 fails:** ratio 2.82; the original dry run gave 1.56.
- C4 under gte fails (V2_D 0.37 on G38).

## Recommendation
**Adopt with changes.** Vivian should accept C2-r1b, or keep the strict C2, knowing that two-room weeks are likely to fail its CI clause. C6 rests on the content-pull network, which round 1b found unreliable; consider demoting it to a report.
