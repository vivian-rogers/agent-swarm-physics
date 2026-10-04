# H31 × G21: Forecast the abilities and effects of AI (2025-12-01 → 2025-12-08)

**Verdict:** failed
**Verdict (1b):** supported (was failed; label renumbering)
**Role:** replication (exploratory) (E-P + E-C)
**Period:** regime I · mode I · 8 agents · #general · 5 non-holdout days (20.0 active h).

## Why this period
H11 project labels are dense enough for E-P (≥ 50% of room-windows have ≥ 3 labeled agents).

**Predictors** (whole block-period; computed before any outcome):

| Block | N_b | msgs/h | u (reads/h) | λ₂^w,sym (1/h) | λ₂^w,dir | u·λ₂^rw | γ_tr | τ_wave (min) | τ_Vsim (h) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #general | 8 | 122 | 50.9 | 52.85 | 54.45 | 51.9 | 8.75 | 0.5 | 0.108 |

## Prediction
*Written 2026-10-03, before running on this period.*

- **Card rules apply unchanged** (E-P, E-V, E-C definitions; tests T1–T7). Per-period verdicts are descriptive; the scaling test (P1, P5) is cross-period.
- **H31 (model D):** if this block's events are uncensored, their τ should sit on the cross-period line τ = c/λ₂^w,sym. Blocks with a larger λ₂^w,sym should be faster.
- **My prior (card):** the timing is set by task structure and announcements, so this period's τ will not track λ₂ beyond noise. E-P rises will be mostly abrupt (ρ ≤ 1 window), and E-C, if present, will be a convergence over days (τ_C 2–15 h).
- **Period-specific:** Forecast week. H24 found content aligned from the first hour and ramping over the week, so I expect an E-C convergence with a long τ_C (≥ 5 h) that the graph does not explain.
- **Counts against H31 here:** uncensored events whose τ is far off the calibrated line (outside the 80% LOPO interval), or a room contrast with the opposite sign to D.

## Result
| Block | E-P projects | consensus (frozen at start / instant / uncensored) | τ_P (h), uncensored | rise (windows) | kick-locked | M_λ forecast (h) | M0 forecast (h) | E-C kind | E-C τ (h) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #general | 8 | 3 (0 / 1 / 2) | 2.0, 3.0 | 3, 7 | 0/3 | 2.0, 2.0 | 4.2, 4.2 | divergence | 0.7 |

- **E-P vs the H31 line:** M_λ (fitted on the other periods) beats the constant forecast for 1/2 uncensored events. Mean |log error| is 0.20 (M_λ) vs 0.55 (M0).
- **E-C divergence:** content alignment starts high after the kickoff (A₀ = 0.85) and relaxes to A∞ = 0.43 with τ = 0.7 h. The field imposes the alignment and the dynamics dissolve it, the opposite of consensus formation.

Data: `data/processed/H31-consensus-time-spectral-gap/G21/`, `events_ep_w30.parquet`, `events_ec.parquet`.

## Scorecard (period-specific axes)
- **C (period level):** the per-event leave-one-period-out comparison of M_λ (or M_tr) vs the constant is listed above.
- **G:** no external ground truth for consensus timing in this period.

## Notes
- 2026-10-03: folder and prediction written before the real-data run on this period.
- 2026-10-03: results filled from `analysis/explore.py` (round 1).

## Round 1b (improved data, 2026-10-04)
*Replication (templated) with context-ledger visibility and the shared deterministic labels (`scheme/build.py --visibility ledger --labels shared`, `analysis/explore.py` with `H31_DATA=…/r1b`). Card predictions R1b-1 and R1b-2 were written before the run.* Verdict rule as in round 1 (M_λ fitted on the other periods vs the constant, per gradual event). Changed from round 1 (failed): label renumbering under the deterministic tie-break moves which events are gradual.

| Block | λ₂^w,sym (1/h) round 1 → 1b | E-P attention, round 1 (frozen / instant / gradual) | E-P attention, round 1b | E-P work (round 1b) |
| --- | --- | --- | --- | --- |
| #general | 52.9 → 53.2 | 8 projects; 3 consensus (0 / 1 / 2); τ 2.0, 3.0 | 8 projects; 4 consensus (0 / 1 / 3); τ 2.0, 1.0, 0.5 | n/a (ledger sparse before #30) |
