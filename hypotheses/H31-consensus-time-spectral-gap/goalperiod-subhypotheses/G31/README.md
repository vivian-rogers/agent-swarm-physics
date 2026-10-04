# H31 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-23)

**Verdict:** failed
**Role:** exploratory (card candidate; E-P + E-C)
**Period:** regime I · mode F · 12 agents · #general · 5 non-holdout days (20.0 active h).

## Why this period
Named by HH115 and H11 as a consensus period. H11 project labels are dense enough for E-P (≥ 50% of room-windows have ≥ 3 labeled agents).

**Predictors** (whole block-period; computed before any outcome):

| Block | N_b | msgs/h | u (reads/h) | λ₂^w,sym (1/h) | λ₂^w,dir | u·λ₂^rw | γ_tr | τ_wave (min) | τ_Vsim (h) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #general | 11 | 139 | 57.9 | 86.41 | 76.77 | 59.0 | 7.00 | 0.4 | 0.067 |

## Prediction
*Written 2026-10-03, before running on this period.*

- **Card rules apply unchanged** (E-P, E-V, E-C definitions; tests T1–T7). Per-period verdicts are descriptive; the scaling test (P1, P5) is cross-period.
- **H31 (model D):** if this block's events are uncensored, their τ should sit on the cross-period line τ = c/λ₂^w,sym. Blocks with a larger λ₂^w,sym should be faster.
- **My prior (card):** the timing is set by task structure and announcements, so this period's τ will not track λ₂ beyond noise. E-P rises will be mostly abrupt (ρ ≤ 1 window), and E-C, if present, will be a convergence over days (τ_C 2–15 h).
- **Period-specific:** Free week with herding waves onto successive shared repos (H11). I expect several uncensored E-P events with abrupt rises (ρ ≤ 1 window) and τ_P ≤ 2 h: model H's signature, not D's gradual 1/λ₂ approach.
- **Counts against H31 here:** uncensored events whose τ is far off the calibrated line (outside the 80% LOPO interval), or a room contrast with the opposite sign to D.

## Result
| Block | E-P projects | consensus (frozen at start / instant / uncensored) | τ_P (h), uncensored | rise (windows) | kick-locked | M_λ forecast (h) | M0 forecast (h) | E-C kind | E-C τ (h) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #general | 8 | 5 (0 / 0 / 5) | 1.0, 1.0, 3.5, 3.0, 13.5 | None, 1, 2, 3, 2 | 1/5 | 1.1, 1.1, 1.1, 1.1, 1.1 | 4.4, 4.4, 4.4, 4.4, 4.4 | none | – |

- **E-P vs the H31 line:** M_λ (fitted on the other periods) beats the constant forecast for 2/5 uncensored events. Mean |log error| is 0.97 (M_λ) vs 0.94 (M0).

Data: `data/processed/H31-consensus-time-spectral-gap/G31/`, `events_ep_w30.parquet`, `events_ec.parquet`.

## Scorecard (period-specific axes)
- **C (period level):** the per-event leave-one-period-out comparison of M_λ (or M_tr) vs the constant is listed above.
- **G:** no external ground truth for consensus timing in this period.

## Notes
- 2026-10-03: folder and prediction written before the real-data run on this period.
- 2026-10-03: results filled from `analysis/explore.py` (round 1).
