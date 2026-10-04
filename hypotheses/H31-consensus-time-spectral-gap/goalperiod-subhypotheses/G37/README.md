# H31 × G37: Pick your own goal! (2026-03-30 → 2026-04-02)

**Verdict:** failed
**Verdict (1b):** failed (unchanged)
**Role:** exploratory (E-P + E-C; two-room contrast (T6))
**Period:** regime III · mode F · 13 agents · #best, #rest · 3 non-holdout days (20.7 active h).

## Why this period
H11 project labels are dense enough for E-P (≥ 50% of room-windows have ≥ 3 labeled agents). Two rooms with the same goal and kickoff, so the field is common and the graphs differ (T6).

**Predictors** (whole block-period; computed before any outcome):

| Block | N_b | msgs/h | u (reads/h) | λ₂^w,sym (1/h) | λ₂^w,dir | u·λ₂^rw | γ_tr | τ_wave (min) | τ_Vsim (h) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #best | 3 | 12 | 5.4 | 1.79 | 2.22 | 5.7 | 0.00 | 93.0 | 4.546 |
| #rest | 9 | 22 | 11.0 | 11.00 | 18.14 | 11.0 | 2.47 | 93.2 | 3.210 |

## Prediction
*Written 2026-10-03, before running on this period.*

- **Card rules apply unchanged** (E-P, E-V, E-C definitions; tests T1–T7). Per-period verdicts are descriptive; the scaling test (P1, P5) is cross-period.
- **H31 (model D):** if this block's events are uncensored, their τ should sit on the cross-period line τ = c/λ₂^w,sym. Blocks with a larger λ₂^w,sym should be faster.
- **My prior (card):** the timing is set by task structure and announcements, so this period's τ will not track λ₂ beyond noise. E-P rises will be mostly abrupt (ρ ≤ 1 window), and E-C, if present, will be a convergence over days (τ_C 2–15 h).
- **T6 room contrast:** model D predicts consensus faster in the larger room (λ₂ ratio large/small = 6.1). Voter V predicts the smaller room (#best, N ≈ 3) faster by ≈ N ratio 3.0. Field F predicts no difference.
- **Counts against H31 here:** uncensored events whose τ is far off the calibrated line (outside the 80% LOPO interval), or a room contrast with the opposite sign to D.

## Result
| Block | E-P projects | consensus (frozen at start / instant / uncensored) | τ_P (h), uncensored | rise (windows) | kick-locked | M_λ forecast (h) | M0 forecast (h) | E-C kind | E-C τ (h) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #best | 3 | 1 (0 / 0 / 1) | 10.1 | 22 | 0/1 | 67.6 | 3.7 | none | – |
| #rest | 8 | 4 (0 / 0 / 4) | 18.1, 2.0, 3.5, 20.1 | 3, 3, 6, 2 | 0/4 | 11.0, 11.0, 11.0, 11.0 | 3.7, 3.7, 3.7, 3.7 | none | – |

- **E-P vs the H31 line:** M_λ (fitted on the other periods) beats the constant forecast for 2/5 uncensored events. Mean |log error| is 1.17 (M_λ) vs 0.99 (M0).
- **T6 room contrast:** τ(small room #best) / τ(large room #rest) = 1.42. D predicted 6.13 (sign agrees); V predicted 0.33 (sign disagrees).

Data: `data/processed/H31-consensus-time-spectral-gap/G37/`, `events_ep_w30.parquet`, `events_ec.parquet`.

## Scorecard (period-specific axes)
- **C (period level):** the per-event leave-one-period-out comparison of M_λ (or M_tr) vs the constant is listed above.
- **G:** no external ground truth for consensus timing in this period.

## Notes
- 2026-10-03: folder and prediction written before the real-data run on this period.
- 2026-10-03: results filled from `analysis/explore.py` (round 1).

## Round 1b (improved data, 2026-10-04)
*Replication (templated) with context-ledger visibility and the shared deterministic labels (`scheme/build.py --visibility ledger --labels shared`, `analysis/explore.py` with `H31_DATA=…/r1b`). Card predictions R1b-1 and R1b-2 were written before the run.* Verdict rule as in round 1 (M_λ fitted on the other periods vs the constant, per gradual event).

| Block | λ₂^w,sym (1/h) round 1 → 1b | E-P attention, round 1 (frozen / instant / gradual) | E-P attention, round 1b | E-P work (round 1b) |
| --- | --- | --- | --- | --- |
| #best | 1.8 → 1.8 | 3 projects; 1 consensus (0 / 0 / 1); τ 10.1 | 3 projects; 1 consensus (0 / 0 / 1); τ 10.1 | not eligible |
| #rest | 11.0 → 11.0 | 8 projects; 4 consensus (0 / 0 / 4); τ 18.1, 2.0, 3.5, 20.1 | 8 projects; 3 consensus (0 / 0 / 3); τ 18.1, 2.0, 3.5 | not eligible |
