# H60 × NE43: the untreated arm on nudger-free days (2026-08-07 → 08-20 vs 08-21 → 09-02)

**Verdict:** supported
**Role:** native
**Period:** regime III · #51 · 24 agents present on both sides · B: 6207 gates (139 nudged), C: 3873 gates (no nudges). Exception (c).

## Why this period
After 08-20 nobody selects agents for nudges, so the untreated outcome model can be checked against gates with no selection at all. A larger miss in the states the nudger targets (k ≥ 4) than elsewhere is the selection signature (R3).

## Prediction
*Written 2026-10-04, before running (card N1).*
(a) the calibration ratio (observed / predicted active calls) differs by < 15% between targeted states (k ≥ 4) and the rest [0.5]; (b) the logged nudges buy ≤ 1% of the window's active calls [0.8].

## Result
`analysis/native.py`; `data/processed/H60-index-nudge-policy/native/native.json` (B = 200 day draws on each side).

| Quantity | Estimate [95% CI] | Prediction |
| --- | --- | --- |
| calibration, targeted (k ≥ 4) | 0.83 [0.64, 1.05] | |
| calibration, other states | 0.92 [0.86, 0.98] | |
| ratio targeted / other | 0.90 [0.71, 1.09] | (a) pass |
| active calls bought by logged nudges (B) | 363 [-59.31, 781.65] of 193466 (0.19%) | (b) pass |

Both sides share the days' room change and roster growth, so (a) also absorbs a period shift common to all states; the comparison is between state groups.

