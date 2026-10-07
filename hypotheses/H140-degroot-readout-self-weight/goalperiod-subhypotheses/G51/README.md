# H140 × G51: private roles and timer wakes (#51 main body, units 51a–51l)

**Verdict:** pending
**Role:** exploratory (replication over 12 units + native N2)
**Period:** regime III · mode I/K (private roles) · up to 21 agents · #general (and #focus from 08-05) · non-reserved days 2026-07-06 → 2026-09-04. The tail (2026-09-07 → 09-21) is reserved and not used.

## Why this period
The most talk calls and the only period where batch size k is set by others while the reader sleeps (timer wakes: H18's design D2, H113's cleanest exponent a_U 0.31 [0.25, 0.37]). H130 measured γ_auto 0.0094 per call here, which fixes R-well's call-gap self-weight with no fit.

## Prediction
*Written 2026-10-07 ~10:50 UTC, before running on this period. Seen: H113's and H18's #51 numbers, H130's γ_auto, H72's idle self-share result; no s_self value and no self-weight.*
- **P1:** pooled ŵ₁ over 51a–51l ∈ [0.5, 1.5] with CI above 0. Credence 0.15.
- **N2 (native):** on timer-wake batches, |ŵ₁(wakes) − ŵ₁(talk)| < 0.3 and â(wakes) ∈ [0.15, 0.45]. Credence 0.35.
- **P3:** the call-gap term ŵ₂ = weight on (1 − 0.0094)^{Δn} is > 0 with CI, and adding it lowers ŵ₁ by ≥ 50%. Credence 0.55.
- Counts against: kill clause 1 (pooled ŵ₁ CI includes 0 with power ≥ 0.8) or clause 2 (â ≥ 0.7).

## Result
Not run.

## Scorecard (period-specific axes)
C, D, E, H: not run (all 0).

## Notes
- H113 found the dilution exponent b lower on #51 wakes than on #51 talk calls (0.69 / 0.71 vs 0.86 / 0.90, bge / gte), so â is higher on wakes. N2's band (up to 0.45) allows for that.
