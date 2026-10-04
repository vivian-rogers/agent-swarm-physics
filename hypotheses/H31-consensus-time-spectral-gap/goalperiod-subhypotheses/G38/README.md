# H31 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-27)

**Verdict:** supported
**Verdict (1b):** supported (unchanged)
**Role:** replication (exploratory) (E-P + E-C; two-room contrast (T6))
**Period:** regime III · mode C · 12 agents · #best, #rest · 17 non-holdout days (72.2 active h).

## Why this period
H11 project labels are dense enough for E-P (≥ 50% of room-windows have ≥ 3 labeled agents). Two rooms with the same goal and kickoff, so the field is common and the graphs differ (T6).

**Predictors** (whole block-period; computed before any outcome):

| Block | N_b | msgs/h | u (reads/h) | λ₂^w,sym (1/h) | λ₂^w,dir | u·λ₂^rw | γ_tr | τ_wave (min) | τ_Vsim (h) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #best | 4 | 27 | 12.3 | 1.60 | 2.08 | 12.1 | 0.33 | 10.4 | 26.083 |
| #rest | 8 | 36 | 22.0 | 17.20 | 31.45 | 22.1 | 10.18 | 8.5 | 0.047 |

## Prediction
*Written 2026-10-03, before running on this period.*

- **Card rules apply unchanged** (E-P, E-V, E-C definitions; tests T1–T7). Per-period verdicts are descriptive; the scaling test (P1, P5) is cross-period.
- **H31 (model D):** if this block's events are uncensored, their τ should sit on the cross-period line τ = c/λ₂^w,sym. Blocks with a larger λ₂^w,sym should be faster.
- **My prior (card):** the timing is set by task structure and announcements, so this period's τ will not track λ₂ beyond noise. E-P rises will be mostly abrupt (ρ ≤ 1 window), and E-C, if present, will be a convergence over days (τ_C 2–15 h).
- **T6 room contrast:** model D predicts consensus faster in the larger room (λ₂ ratio large/small = 10.8). Voter V predicts the smaller room (#best, N ≈ 4) faster by ≈ N ratio 2.0. Field F predicts no difference.
- **Period-specific:** 17-day charity fundraiser, two rooms. Long period, so τ can be long. H20 saw a kickoff relaxation over about 4 active days in content, so I expect an E-C convergence with τ_C of order 10 active h.
- **Counts against H31 here:** uncensored events whose τ is far off the calibrated line (outside the 80% LOPO interval), or a room contrast with the opposite sign to D.

## Result
| Block | E-P projects | consensus (frozen at start / instant / uncensored) | τ_P (h), uncensored | rise (windows) | kick-locked | M_λ forecast (h) | M0 forecast (h) | E-C kind | E-C τ (h) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #best | 2 | 2 (1 / 0 / 1) | 19.6 | 3 | 1/2 | 75.3 | 3.9 | divergence | 144.3 |
| #rest | 6 | 5 (1 / 0 / 4) | 1.0, 10.1, 4.5, 7.1 | 2, 4, 2, 3 | 1/5 | 7.0, 7.0, 7.0, 7.0 | 3.9, 3.9, 3.9, 3.9 | none | – |

- **E-P vs the H31 line:** M_λ (fitted on the other periods) beats the constant forecast for 3/5 uncensored events. Mean |log error| is 0.82 (M_λ) vs 0.94 (M0).
- **T6 room contrast:** τ(small room #best) / τ(large room #rest) = 4.62. D predicted 10.79 (sign agrees); V predicted 0.50 (sign disagrees).
- **E-C divergence:** content alignment starts high after the kickoff (A₀ = 0.60) and relaxes to A∞ = 0.23 with τ = 144.3 h. The field imposes the alignment and the dynamics dissolve it, the opposite of consensus formation.

Data: `data/processed/H31-consensus-time-spectral-gap/G38/`, `events_ep_w30.parquet`, `events_ec.parquet`.

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
| #best | 1.6 → 1.6 | 2 projects; 2 consensus (1 / 0 / 1); τ 19.6 | 2 projects; 2 consensus (1 / 0 / 1); τ 19.6 | not eligible |
| #rest | 17.2 → 17.2 | 6 projects; 5 consensus (1 / 0 / 4); τ 1.0, 10.1, 4.5, 7.1 | 6 projects; 5 consensus (1 / 0 / 4); τ 1.0, 10.1, 4.5, 7.1 | not eligible |
