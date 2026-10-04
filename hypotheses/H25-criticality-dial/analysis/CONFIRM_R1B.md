# H25 confirm re-freeze (round 1b), 2026-10-04

**Script:** `confirm_r1b.py` re-freezes `confirm.py`, which is unchanged. It imports the frozen helpers of `confirm.py` and `explore.run_binary_variants` and runs with `H25_DATA_VERSION=fixed`. Status: dry-run only, **not run on the holdout**.

## What changed
- **Stage B inputs:** spins from `activity_bins_fixed` and the DQ8 `trim` variant (auto stall mask plus all-present window, before the null). The round-1 `auto` variant is reported beside it.
- **Stage A inputs:** the content dial in two models.
  - bge keeps the frozen pipeline (H12 dedupe rule), so measurement and thresholds match; a bge variant with DQ5 `self_repeat` dedupe is reported. gte uses shared vectors, the gte whitener and DQ5 `self_repeat_gte`.
  - Ledger visibility, the work ledger, failures and nudge targets are not inputs of this design.
- **Frozen file:** `r1b/results/frozen_confirm_r1b.json` (exploratory round 1b only; sha256 `63ec9a27…`, fixed in the script).
- **Predictions:**
  - CA1–CA4 are unchanged; the content point estimates are identical in round 1b.
  - **CA5-r1b** (new): the gte and bge period medians agree within ±0.15 in ≥ min(4, n) periods. Content counts as confirmed only if CA1–CA4 pass (bge) and CA5 holds.
  - **CB1-r1b:** the CB1 rule on the trim variant.
  - **CB2-r1b:** re-frozen exploratory share 0.069 (trim; round 1 used the buggy table).
  - **CB3-r1b** (new): talk's share of days above the trimmed null exceeds activity's by ≥ 0.10, and activity's share lies within ±0.20 of 0.24 (exploratory: activity 24%, talk 53%).
- **Gates:** Stage B also opens on H19's round-1b score file; `holdout_ledger.check()` is now called (the original did not); the commit check now covers `confirm_r1b.py` and `explore.py`.

## Why
- **Ledger item 8:** Stage B had no trimmed variant and used the buggy table.
- **Day edges:** round 1b showed most apparent activity feedback is day-edge synchrony. Only 24% of trimmed activity days exceed the null ceiling, against 54% untrimmed; talk keeps 53%.
- **Content:** must be reported in both models (DQ5). No gte exploratory baseline exists, so gte enters as an agreement clause.

## Holdout reuse (ledger)
- No executed run on #1, #9, #14, #15, #22 or #43; all checks return `allowed`.
- **Competing planned users:** H19 on all six (equal-time gains; Stage B stays gated on H19's run); H20 (#1, #14, #15, #22); H36 (all); H24, H32 (#14). #22 has nine planned users (H06, H10, H12, H19, H20, H32, H33, H34, H36).
- Disclose in the H25 and H19 cards and in `LOG.md`.

## Dry run (stand-ins: A #24, #27, #41; B #23, #42; numbers meaningless as confirmation)
- Runs end to end; the freeze is written and hashed; no holdout day is read (asserted). Without flags, the script refuses.
- **Stage A bge** reproduces the original dry run exactly: CA1 3/3, CA2 fail (share 0.00 vs 0.24), CA3 0.95, CA4 3/3. The DQ5 variant and gte give the same pass pattern.
- **CA5:** 3/3 periods agree (|Δ| ≤ 0.08).
- **Stage B trim:** CB1 1.00 (pass), CB2 0.00 (pass). CB3 fails: activity 0.00 vs talk 0.70 above the null, but activity sits 0.24 below its frozen 0.24.
- Output: `data/processed/H25-criticality-dial/r1b/confirm_r1b_dryrun/`.

## Recommendation
**Adopt with changes.** Vivian must decide whether CA5's agreement clause is enough for "both models", or whether to freeze gte thresholds from a gte exploratory run. That run is moderate compute and has not been done.
