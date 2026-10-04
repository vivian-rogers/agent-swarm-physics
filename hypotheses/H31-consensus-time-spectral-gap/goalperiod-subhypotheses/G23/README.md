# H31 × G23: Compete against each other in an online chess tournament (2025-12-15 → 2025-12-22)

**Verdict:** descriptive
**Verdict (1b):** descriptive (unchanged)
**Role:** replication (exploratory) (E-C only)
**Period:** regime I · mode K · 10 agents · #general · 5 non-holdout days (20.0 active h).

## Why this period
H11 labels are too sparse for E-P, so only content (E-C) is tested.

**Predictors** (whole block-period; computed before any outcome):

| Block | N_b | msgs/h | u (reads/h) | λ₂^w,sym (1/h) | λ₂^w,dir | u·λ₂^rw | γ_tr | τ_wave (min) | τ_Vsim (h) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #general | 10 | 89 | 51.9 | 58.08 | 87.94 | 53.6 | 22.47 | 0.3 | 0.039 |

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

Data: `data/processed/H31-consensus-time-spectral-gap/G23/`, `events_ep_w30.parquet`, `events_ec.parquet`.

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
| #general | 58.1 → 58.0 | not eligible | not eligible | n/a (ledger sparse before #30) |
