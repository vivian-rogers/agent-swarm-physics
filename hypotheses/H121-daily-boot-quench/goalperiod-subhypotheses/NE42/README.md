# H121 × NE42: room merge and split at a fixed roster (#39 → #40 → #41; 2026-04-27 → 05-15)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** regime III · units 39, 40, 41 (5 days each) · N = 15 · #best/#rest merged into one room for #40, split back for #41.

## Why this period
H67's read-out gain falls to zero in the merged week and returns: g_lag 0.144 [0.066, 0.223] → 0.003 [−0.110, 0.117] → 0.189 [0.093, 0.286]. At fixed roster and scaffold this is a dose change of the coupling, with τ₀ expected to stay put.

## Prediction
*Written 2026-10-04 22:08 UTC, before running on this period.*
- **Mean field (H121's model):** τ_boot/τ₀ = 1/(1 − g): 1.17 → 1.00 → 1.23. So τ_boot/τ₀ in #40 is lower than in both #39 and #41, by ≈ 15–20%.
- **Credence 0.3** that the observed ordering matches (τ_boot/τ₀ in #40 below both neighbours). The expected effect (≈ 0.15 in ln τ) is likely below the resolution of three 5-day units, so a non-matching order is weak evidence; the synthetic CI width decides whether this native is "descriptive".
- Counts against: τ_boot/τ₀ in #40 above both neighbours with CIs excluding the neighbours' point estimates.

## Result
*Registered estimator.* τ_boot/τ₀ = 0.67 [0.20, 18.7] (#39), 1.14 [0.82, 2000] (#40), 3.46 [1.95, 1580] (#41). Mean field predicted 1.17 → 1.00 → 1.23. The merged week (#40) is not the lowest. Its CI overlaps both neighbours, so the "counts against" clause (#40 above both, with the CI excluding them) is not met: **mixed**.

*Post hoc (labelled)*: the ratio estimator gives τ_fast = 0.77 [0, 2.8], 2.12 [0.95, 5.5] and 3.07 [1.04, 7.0] calls. The order does not match either. The predicted effect (about 15% in τ) is far below the resolution of three 5-day units.

Data: `data/processed/H121-daily-boot-quench/results/natives.json`, `posthoc.json`.

## Scorecard (period-specific axes)
E (dose response across a natural experiment).

## Notes
- The goal also changes each week (#39, #40, #41), so a boot change that tracks the goal rather than g_lag is a confound.
