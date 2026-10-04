# H25 × NE43: the operator's drive is withdrawn in two steps inside #51 (bookends stop 2026-08-05, nudges stop 2026-08-21)

**Verdict:** supported
**Role:** native (round 1b, non-holdout; transition exception c)
**Period:** #51 head, non-holdout days (2026-07-06 → 2026-09-04): A = before 08-05 (bookends + nudges), B = 08-05 → 08-20 (nudges only), C = 08-21 → 09-04 (no operator drive). Regime III; roster 21 → 32; one room plus #focus from 08-05.

## Why this period
The dial claims to measure feedback among agents after the drives (fields) are removed: 30-min block means take out every field slower than 30 min. NE43 removes two exogenous drives at fixed goal, room and hours (DQ9): the daily pause/resume bookends (a field at the day edges) and the nudger (a field aimed at idle agents). If the dial reads coupling, not drive, neither step should move it. If the activity dial is partly drive leakage (nudges arrive at minute scale, faster than the blocks), it should fall when the nudger stops.

## Prediction
*Written 2026-10-04 06:34 UTC, before computing any round-1b dial on these days. Seen before: round-1 G51 period values on the old table (activity 0.17, talk 0.06–0.09 fixed/random effects, content 0.82); no day-level values by window, no fixed-table values.*
Design: daily dials on `activity_bins_fixed` (activity and talk: `auto` stall mask, the round-1 primary; and `trim`, the DQ8 all-present-window variant), random-effects means per window; step z = Δ / SE(Δ) as in P7; placebo = every other within-#51 day boundary with ≥ 2 days each side, same statistic (|z| distribution).
- **N3a (no drive leakage at the bookend stop).** Activity and talk: |z(A → B)| below the 95th percentile of the within-#51 placebo |z|.
- **N3b (no drive leakage at the nudger stop).** Activity and talk: |z(B → C)| below the placebo 95th percentile.
- **Rival (drive leakage).** The activity dial falls at the nudger stop (z(B → C) < 0 beyond the placebo q95), because nudges wake idle agents together at minute scale.
- Credence: N3a 0.75, N3b 0.65.
- **Verdict rule:** supported if N3a and N3b hold for both channels; failed if either step exceeds the placebo q95 in the activity channel in the rival's direction; mixed otherwise. Content steps are reported (descriptive).
- Confounds stated in advance: #focus opens on 08-05; joins at NE33 (09-03) fall in C; weekly roster growth raises g mechanically at fixed per-pair correlation (PH1), so ρ̄ steps are reported alongside g.

## Result
*Run 2026-10-04 06:42 UTC (`analysis/r1b_native.py`; `data/processed/H25-criticality-dial/r1b/native/ne43_steps.parquet`). Windows: A 22 days, B 12, C 11. Placebo: 36 other within-#51 boundaries (33 for `trim`).*

| Dial | A → B (bookends stop): Δ (z) | B → C (nudger stops): Δ (z) | placebo q95 of \|z\| | Δ per-pair ρ̄ (A→B, B→C) |
| --- | --- | --- | --- | --- |
| activity, stalls masked (primary) | −0.046 (−0.78) | +0.030 (+0.43) | 1.04 | −0.001, +0.001 |
| talk, stalls masked (primary) | −0.042 (−1.47) | +0.008 (+0.24) | 1.57 | −0.003, +0.002 |
| activity, DQ8 trim | +0.038 (+1.01) | +0.002 (+0.05) | 1.48 | +0.000, +0.000 |
| talk, DQ8 trim | −0.034 (−1.12) | +0.003 (+0.09) | 1.13 | −0.002, −0.000 |
| content F2 (descriptive) | −0.038 (−1.07) | +0.024 (+0.55) | 1.55 | −0.014, −0.004 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N3a no step at the bookend stop (activity, talk) | \|z\| 0.78, 1.47 < q95 1.04, 1.57 | ✓ |
| N3b no step at the nudger stop (activity, talk) | \|z\| 0.43, 0.24 | ✓ |
| Rival: activity dial falls at the nudger stop | +0.030 | ✗ (rival rejected) |

**Verdict: supported.** Withdrawing either exogenous drive leaves the dial where it was, on both the round-1 design and the DQ8-trimmed one, as a measure of feedback rather than drive should. The talk step at the bookend stop (z −1.47) is the largest but stays inside the placebo band.

## Scorecard (period-specific axes)
- **E (interventional):** two drive withdrawals at fixed goal, room and hours; the dial does not move beyond within-#51 placebo boundaries. Evidence that block detrending removes these fields (a null result the model predicts).
- **C (adequacy):** the field-only rival for activity (nudges as minute-scale drive) is rejected at this resolution.

## Notes
- 2026-10-04: folder created with the prediction before the run (round 1b; DQ9 native test for H25).
