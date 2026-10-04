# H31 × G13: Design, run and write up a human subjects experiment (2025-09-08 → 2025-09-22)

**Verdict:** descriptive
**Role:** exploratory (E-C only)
**Period:** regime I · mode C · 6 agents · #general · 10 non-holdout days (29.9 active h).

## Why this period
H11 labels are too sparse for E-P, so only content (E-C) is tested.

**Predictors** (whole block-period; computed before any outcome):

| Block | N_b | msgs/h | u (reads/h) | λ₂^w,sym (1/h) | λ₂^w,dir | u·λ₂^rw | γ_tr | τ_wave (min) | τ_Vsim (h) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #general | 6 | 153 | 66.7 | 120.98 | 152.01 | 74.0 | 22.45 | 0.4 | 0.014 |

## Prediction
*Written 2026-10-03, before running on this period.*

- **Card rules apply unchanged** (E-P, E-V, E-C definitions; tests T1–T7). Per-period verdicts are descriptive; the scaling test (P1, P5) is cross-period.
- **H31 (model D):** if this block's events are uncensored, their τ should sit on the cross-period line τ = c/λ₂^w,sym. Blocks with a larger λ₂^w,sym should be faster.
- **My prior (card):** the timing is set by task structure and announcements, so this period's τ will not track λ₂ beyond noise. E-P rises will be mostly abrupt (ρ ≤ 1 window), and E-C, if present, will be a convergence over days (τ_C 2–15 h).
- **Counts against H31 here:** uncensored events whose τ is far off the calibrated line (outside the 80% LOPO interval), or a room contrast with the opposite sign to D.

## Result
| Block | E-P projects | consensus (frozen at start / instant / uncensored) | τ_P (h), uncensored | rise (windows) | kick-locked | M_λ forecast (h) | M0 forecast (h) | E-C kind | E-C τ (h) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #general | n/a | 0 (0 / 0 / 0) | – | – | – | – | – | none | – |

Data: `data/processed/H31-consensus-time-spectral-gap/G13/`, `events_ep_w30.parquet`, `events_ec.parquet`.

## Scorecard (period-specific axes)
- **C (period level):** the per-event leave-one-period-out comparison of M_λ (or M_tr) vs the constant is listed above.
- **G:** no external ground truth for consensus timing in this period.

## Notes
- 2026-10-03: folder and prediction written before the real-data run on this period.
- 2026-10-03: results filled from `analysis/explore.py` (round 1).
