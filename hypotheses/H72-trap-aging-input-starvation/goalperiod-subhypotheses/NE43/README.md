# H72 × NE43: the nudger stops inside #51 (2026-08-07 → 08-20 vs 08-21 → 09-02)

**Verdict:** descriptive
**Role:** native
**Prediction outcome (dated, written against H72):** mixed. The verdict line scores H72's claim: the stop did not lengthen the directed clock, so it does not manipulate starvation and cannot test H72 (descriptive).
**Period:** regime III · #51 (G51) · B = 08-07 → 08-20 (nudges on, bookends gone), C = 08-21 → 09-02 (no nudges). Exception (c): the transition is the object.

## Why this period
The nudger is the only source of directed input that switches off at a known date. If trap aging were input starvation, losing the nudges would lengthen the starvation clock and lower escape at fixed trap age.

## Prediction
*Written 2026-10-04, before running (card, N1).*
(a) median s_dir up ≥ 20% after the stop [0.7]; (b) β_a and β_s differ by < 0.3 with CIs including 0 [0.6]; (c) a C indicator in the pooled model has a CI including 0 [0.55].

## Result
`analysis/native.py`; numbers in `data/processed/H72-trap-aging-input-starvation/native/native.json` (B = 200 day-block draws per side).

| Quantity | B (nudges on) | C (nudger off) | C − B [95% CI] | Prediction |
| --- | --- | --- | --- | --- |
| gates | 6907 | 4688 | | |
| median s_dir (min) | 30.2 | 29.4 | ×0.97 | (a) fail |
| β_a | -0.30 [-0.37, -0.15] | -0.45 [-0.50, -0.33] | -0.16 [-0.33, -0.01] | (b) |
| β_s | -0.09 [-0.28, +0.02] | +0.13 [-0.10, +0.46] | +0.22 [-0.05, +0.63] | (b) fail |
| C indicator (pooled, agent FE) | | | -0.18 [-0.40, +0.02] | (c) pass |

