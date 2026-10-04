# H31 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 2026-03-23)

**Verdict:** descriptive
**Verdict (1b):** descriptive (unchanged)
**Role:** exploratory (E-P + E-C; two-room contrast (T6))
**Period:** regime II · mode C · 13 agents · #best, #rest · 5 non-holdout days (19.9 active h).

## Why this period
H11 project labels are dense enough for E-P (≥ 50% of room-windows have ≥ 3 labeled agents). Two rooms with the same goal and kickoff, so the field is common and the graphs differ (T6).

**Predictors** (whole block-period; computed before any outcome):

| Block | N_b | msgs/h | u (reads/h) | λ₂^w,sym (1/h) | λ₂^w,dir | u·λ₂^rw | γ_tr | τ_wave (min) | τ_Vsim (h) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #best | 3 | 27 | 14.6 | 25.00 | 27.19 | 20.0 | 15.75 | 0.3 | 0.032 |
| #rest | 9 | 70 | 44.4 | 42.21 | 67.95 | 45.4 | 24.48 | 0.3 | 0.037 |

## Prediction
*Written 2026-10-03, before running on this period.*

- **Card rules apply unchanged** (E-P, E-V, E-C definitions; tests T1–T7). Per-period verdicts are descriptive; the scaling test (P1, P5) is cross-period.
- **H31 (model D):** if this block's events are uncensored, their τ should sit on the cross-period line τ = c/λ₂^w,sym. Blocks with a larger λ₂^w,sym should be faster.
- **My prior (card):** the timing is set by task structure and announcements, so this period's τ will not track λ₂ beyond noise. E-P rises will be mostly abrupt (ρ ≤ 1 window), and E-C, if present, will be a convergence over days (τ_C 2–15 h).
- **T6 room contrast:** model D predicts consensus faster in the larger room (λ₂ ratio large/small = 1.7). Voter V predicts the smaller room (#best, N ≈ 3) faster by ≈ N ratio 3.0. Field F predicts no difference.
- **Counts against H31 here:** uncensored events whose τ is far off the calibrated line (outside the 80% LOPO interval), or a room contrast with the opposite sign to D.

## Result
| Block | E-P projects | consensus (frozen at start / instant / uncensored) | τ_P (h), uncensored | rise (windows) | kick-locked | M_λ forecast (h) | M0 forecast (h) | E-C kind | E-C τ (h) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #best | 1 | 1 (1 / 0 / 0) | – | – | 1/1 | – | – | none | – |
| #rest | 1 | 1 (1 / 0 / 0) | – | – | 1/1 | – | – | none | – |
- No uncensored E-P event: 2 frozen at the period start (kick-locked by construction) and 0 *instant* (criterion met in the onset window mid-period: a one-window herding wave). By the card's rule both are left-censored, so there is no τ to test.

Data: `data/processed/H31-consensus-time-spectral-gap/G35/`, `events_ep_w30.parquet`, `events_ec.parquet`.

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
| #best | 25.0 → 24.9 | 1 projects; 1 consensus (1 / 0 / 0); τ – | 1 projects; 1 consensus (1 / 0 / 0); τ – | 1 projects; 1 consensus (0 / 1 / 0); τ – |
| #rest | 42.2 → 42.1 | 1 projects; 1 consensus (1 / 0 / 0); τ – | 1 projects; 1 consensus (1 / 0 / 0); τ – | 1 projects; 1 consensus (1 / 0 / 0); τ – |
