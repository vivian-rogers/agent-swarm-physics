# H38 confirm re-freeze (round 1b), 2026-10-04

`confirm_r1b.py` replaces `confirm.py` (untouched) for any holdout run. Written before any holdout access. Not run on the holdout.

## What changed
- **Inputs** (`H38_DATA_VERSION=fixed`, set before `h38lib` is imported):
  - activity: `activity_bins_fixed`;
  - stalls: the shared `outages_fixed/{outages,stall_minutes,reasons}` (all days kept, holdout flagged);
  - DQ8 null: O4 `trim*` variants, with rows outside the all-present window removed before block-shift surrogates.
- **Infra bursts** keep H38's platform-error classes (platform failures, so `turn_outcomes.failed` does not apply). Content, nudges and work are not used.
- **Predictions.** C1–C6 are unchanged. New, all scored on the trimmed decomposition, f_trim = 1 − E_trim/E_raw:
  - **C1t-r1b (regime III):** median f_trim ≥ 0.5, and at most half the regime-III targets keep z_trim > 2. Round 1b: 0.83 and 3/8.
  - **C2t-r1b (regime I):** median f_trim < 0.35. Round 1b: 0.11.
  - **C5t-r1b (talk):** median talk f_trim < 0.3. Round 1b: 0.03.
- **Guard.**
  - Adds a commit check and the ledger gate.
  - `--skip-blocked` drops ledger-blocked targets; use it only on Vivian's call.
  - C6 is dropped whenever any of #46–#49 is blocked: the NE21 weeks are those days, even though the NE21+NE23 tag passes `check()`.

## Why
- Ledger item 8: `confirm.py` lacks the trimmed variants.
- DQ8: the whole-day N1 null rejects 28–34% of independent swarms; the trimmed null rejects 2–4%.
- Round 1b: joint silences fall from 14.3% to 5.3% of minutes. Only 3/8 regime-III periods keep an excess after trimming.

## Holdout reuse (ledger L241–L255)
- `check()` **blocks**, as a same-family and same-modality prior run:
  - #45 (H02, Curie–Weiss βJ₀);
  - #46, #47, #49, #50 (H04, NE21+NE23, tagged curie_weiss_gain);
  - #34 (H05).
- **Open:** #1, #9, #14, #15, #22, #28, #29 and #32 (#32 is H05's, other family).
- Ledger item 5: H19 plans the same equal-time gain on 9 targets. H01, H12 and H26 plan the same family on #45–#47.

## Dry run (#39–#41 regime III, #10/#17/#18 regime I, #35 regime II, and stand-in NE21 weeks)
- Executes end to end.
- All criteria pass. Regime III: f_scaffold 0.71, f_edge 0.88, f_trim 1.03, no stand-in keeps z_trim > 2. Regime I: f_trim −0.03.
- C4: log OR −1.38. C6: edge excess 0.16 / 0.26 / 0.16 (8 h / 4 h / 8 h).
- On the fixed table C6 now passes; the original dry run on old bins failed it.

## Recommendation
**Adopt with changes.** As frozen, the regime-III half (C1, C1t-r1b, C3 and C6) cannot run without a ledger decision on #45–#50. Regime I/II (C2, C2t-r1b, C4, C5) can run now with `--skip-blocked`.
