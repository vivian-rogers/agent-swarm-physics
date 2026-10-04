# H31 × G19: Create a popular daily puzzle game like Wordle (2025-11-03 → 2025-11-17)

**Verdict:** supported
**Verdict (1b):** descriptive (was supported; label renumbering)
**Role:** exploratory (card candidate; E-P + E-C)
**Period:** regime I · mode C · 7 agents · #general · 10 non-holdout days (40.0 active h).

## Why this period
Named by HH115 and H11 as a consensus period. H11 project labels are dense enough for E-P (≥ 50% of room-windows have ≥ 3 labeled agents).

**Predictors** (whole block-period; computed before any outcome):

| Block | N_b | msgs/h | u (reads/h) | λ₂^w,sym (1/h) | λ₂^w,dir | u·λ₂^rw | γ_tr | τ_wave (min) | τ_Vsim (h) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #general | 7 | 134 | 54.1 | 12.30 | 13.81 | 54.8 | 0.41 | 0.5 | 0.026 |

## Prediction
*Written 2026-10-03, before running on this period.*

- **Card rules apply unchanged** (E-P, E-V, E-C definitions; tests T1–T7). Per-period verdicts are descriptive; the scaling test (P1, P5) is cross-period.
- **H31 (model D):** if this block's events are uncensored, their τ should sit on the cross-period line τ = c/λ₂^w,sym. Blocks with a larger λ₂^w,sym should be faster.
- **My prior (card):** the timing is set by task structure and announcements, so this period's τ will not track λ₂ beyond noise. E-P rises will be mostly abrupt (ρ ≤ 1 window), and E-C, if present, will be a convergence over days (τ_C 2–15 h).
- **Period-specific:** H11 found the build repo at ≈ 0.6 share from the start (frozen consensus). I expect the dominant E-P event to be **frozen** (left-censored, excluded from the τ fit), with at most minor uncensored events.
- **Counts against H31 here:** uncensored events whose τ is far off the calibrated line (outside the 80% LOPO interval), or a room contrast with the opposite sign to D.

## Result
| Block | E-P projects | consensus (frozen at start / instant / uncensored) | τ_P (h), uncensored | rise (windows) | kick-locked | M_λ forecast (h) | M0 forecast (h) | E-C kind | E-C τ (h) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #general | 4 | 3 (1 / 1 / 1) | 18.5 | 2 | 1/3 | 8.6 | 3.9 | divergence | 23.1 |

- **E-P vs the H31 line:** M_λ (fitted on the other periods) beats the constant forecast for 1/1 uncensored events. Mean |log error| is 0.76 (M_λ) vs 1.55 (M0).
- **E-C divergence:** content alignment starts high after the kickoff (A₀ = 0.60) and relaxes to A∞ = 0.28 with τ = 23.1 h. The field imposes the alignment and the dynamics dissolve it, the opposite of consensus formation.

Data: `data/processed/H31-consensus-time-spectral-gap/G19/`, `events_ep_w30.parquet`, `events_ec.parquet`.

## Scorecard (period-specific axes)
- **C (period level):** the per-event leave-one-period-out comparison of M_λ (or M_tr) vs the constant is listed above.
- **G:** no external ground truth for consensus timing in this period.

## Notes
- 2026-10-03: folder and prediction written before the real-data run on this period.
- 2026-10-03: results filled from `analysis/explore.py` (round 1).

## Round 1b (improved data, 2026-10-04)
*Replication (templated) with context-ledger visibility and the shared deterministic labels (`scheme/build.py --visibility ledger --labels shared`, `analysis/explore.py` with `H31_DATA=…/r1b`). Card predictions R1b-1 and R1b-2 were written before the run.* Verdict rule as in round 1 (M_λ fitted on the other periods vs the constant, per gradual event). Changed from round 1 (supported): label renumbering under the deterministic tie-break moves which events are gradual.

| Block | λ₂^w,sym (1/h) round 1 → 1b | E-P attention, round 1 (frozen / instant / gradual) | E-P attention, round 1b | E-P work (round 1b) |
| --- | --- | --- | --- | --- |
| #general | 12.3 → 12.3 | 4 projects; 3 consensus (1 / 1 / 1); τ 18.5 | 4 projects; 2 consensus (1 / 1 / 0); τ – | n/a (ledger sparse before #30) |
