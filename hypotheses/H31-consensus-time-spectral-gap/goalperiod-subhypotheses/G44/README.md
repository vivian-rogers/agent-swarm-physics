# H31 × G44: Finetune your leader! (2026-05-26 → 2026-06-01)

**Verdict:** failed
**Verdict (1b):** failed (unchanged)
**Role:** exploratory (E-P + E-C; two-room contrast (T6))
**Period:** regime III · mode C · 16 agents · #best, #rest · 4 non-holdout days (16.2 active h).

## Why this period
H11 project labels are dense enough for E-P (≥ 50% of room-windows have ≥ 3 labeled agents). Two rooms with the same goal and kickoff, so the field is common and the graphs differ (T6).

**Predictors** (whole block-period; computed before any outcome):

| Block | N_b | msgs/h | u (reads/h) | λ₂^w,sym (1/h) | λ₂^w,dir | u·λ₂^rw | γ_tr | τ_wave (min) | τ_Vsim (h) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #best | 4 | 24 | 13.4 | 12.08 | 11.37 | 14.2 | 2.28 | 2.9 | 2.072 |
| #rest | 12 | 84 | 43.4 | 35.63 | 47.66 | 43.4 | 1.25 | 0.5 | 0.048 |

## Prediction
*Written 2026-10-03, before running on this period.*

- **Card rules apply unchanged** (E-P, E-V, E-C definitions; tests T1–T7). Per-period verdicts are descriptive; the scaling test (P1, P5) is cross-period.
- **H31 (model D):** if this block's events are uncensored, their τ should sit on the cross-period line τ = c/λ₂^w,sym. Blocks with a larger λ₂^w,sym should be faster.
- **My prior (card):** the timing is set by task structure and announcements, so this period's τ will not track λ₂ beyond noise. E-P rises will be mostly abrupt (ρ ≤ 1 window), and E-C, if present, will be a convergence over days (τ_C 2–15 h).
- **T6 room contrast:** model D predicts consensus faster in the larger room (λ₂ ratio large/small = 3.0). Voter V predicts the smaller room (#best, N ≈ 4) faster by ≈ N ratio 2.7. Field F predicts no difference.
- **Counts against H31 here:** uncensored events whose τ is far off the calibrated line (outside the 80% LOPO interval), or a room contrast with the opposite sign to D.

## Result
| Block | E-P projects | consensus (frozen at start / instant / uncensored) | τ_P (h), uncensored | rise (windows) | kick-locked | M_λ forecast (h) | M0 forecast (h) | E-C kind | E-C τ (h) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #best | 4 | 1 (0 / 0 / 1) | 0.5 | 2 | 1/1 | 9.7 | 4.4 | none | – |
| #rest | 4 | 1 (0 / 0 / 1) | 4.6 | 4 | 0/1 | 3.3 | 4.4 | none | – |

- **E-P vs the H31 line:** M_λ (fitted on the other periods) beats the constant forecast for 0/2 uncensored events. Mean |log error| is 1.65 (M_λ) vs 1.10 (M0).
- **T6 room contrast:** τ(small room #best) / τ(large room #rest) = 0.11. D predicted 2.95 (sign disagrees); V predicted 0.38 (sign agrees).

Data: `data/processed/H31-consensus-time-spectral-gap/G44/`, `events_ep_w30.parquet`, `events_ec.parquet`.

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
| #best | 12.1 → 12.1 | 4 projects; 1 consensus (0 / 0 / 1); τ 0.5 | 4 projects; 1 consensus (0 / 0 / 1); τ 0.5 | 4 projects; 1 consensus (0 / 0 / 1); τ 1.0 |
| #rest | 35.6 → 35.6 | 4 projects; 1 consensus (0 / 0 / 1); τ 4.6 | 4 projects; 1 consensus (0 / 0 / 1); τ 4.6 | 4 projects; 0 consensus (0 / 0 / 0); τ – |
