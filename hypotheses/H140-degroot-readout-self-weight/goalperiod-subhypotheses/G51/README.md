# H140 × G51: private roles and timer wakes (#51 main body, units 51a–51l)

**Verdict:** mixed
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
Data: `data/processed/H140-degroot-readout-self-weight/G51/`, results `results/units_G51.json`. Run 2026-10-07 (exploration data; reserved days never enter the scheme). Estimator: Amendment A1 spec (primary) and the registered spec; agent-day cluster bootstrap, 300 draws.

Replication over the 12 non-reserved units (51a–51l; 8,801 scored rows):

| Prediction | Observed (bge; gte) | Verdict |
| --- | --- | --- |
| P1 pooled ŵ₁ ∈ [0.5, 1.5], CI > 0 | DL pool 0.025 [−0.09, 0.14]; −0.018 [−0.13, 0.10]. No unit has a CI above 0. Registered spec 0.10 [0.01, 0.19] (inside the range a field produces in synthetic worlds, 0.2–0.35) | **failed** |
| P3 ŵ₂ > 0 and ≥ 50% drop in ŵ₁ (registered) | ŵ₂ 0.34 [−0.61, 1.29]; ŵ₁ 0.113 → 0.101 when the Δn term is added (−11%) | failed |
| P2 â (identified units, 8 of 12) | 0.23 [0.12, 0.34]; 0.21 [0.13, 0.28] | supported (card-level P2) |
| P4 | γ̂_F 0.003 [−0.006, 0.011] vs γ̂₁ 0.068 [0.053, 0.083]; contrast 0.053 [0.038, 0.069] | supported |
| **N2 (native, timer wakes)** \|Δŵ₁\| < 0.3 and â(wakes) ∈ [0.15, 0.45] | wakes ŵ₁ 0.04 [−0.34, 0.42] vs talk 0.02 (Δ 0.02); gte 0.06 vs −0.02 (Δ 0.07). â(wakes) 0.19 [0.07, 0.32]; 0.15 [0.05, 0.25] (1,710 wake rows) | supported (weak: ŵ₁ on wakes is ≈ 0 with a wide CI, so "same as talk calls" means "both ≈ 0") |

- 51g (2,753 rows, the largest unit): ŵ₁ 0.00 [−0.19, 0.18]. In s_self deciles (means 0.26 → 0.95) the per-decile self-weight is flat: −0.48, −0.51, −0.54, −0.57, −0.53, −0.44, −0.55, −0.50, −0.50, −0.51 (level set by the nuisance terms).
- N1 surrogate batches: γ̂₁ under cross-day surrogates is ≈ 0 (medians −0.007 to +0.007); the real γ̂₁ exceeds every surrogate draw in all 9 units with other-day batches (51b, 51k and 51l are one-day units).

## Scorecard (period-specific axes)
C 1, D 0, E 1 (wakes: k set by others gives the same ŵ₁ ≈ 0 and â ≈ 0.2), H 1.

## Notes
- H113 found the dilution exponent b lower on #51 wakes than on #51 talk calls (0.69 / 0.71 vs 0.86 / 0.90, bge / gte), so â is higher on wakes. N2's band (up to 0.45) allows for that.
