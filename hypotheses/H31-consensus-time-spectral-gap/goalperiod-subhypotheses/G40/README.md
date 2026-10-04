# H31 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 2026-05-11)

**Verdict:** descriptive
**Verdict (1b):** descriptive (unchanged)
**Role:** exploratory (card candidate; E-P + E-C)
**Period:** regime III · mode C · 15 agents · #universe-coordination · 5 non-holdout days (20.3 active h).

## Why this period
Named by HH115 and H11 as a consensus period. H11 project labels are dense enough for E-P (≥ 50% of room-windows have ≥ 3 labeled agents).

**Predictors** (whole block-period; computed before any outcome):

| Block | N_b | msgs/h | u (reads/h) | λ₂^w,sym (1/h) | λ₂^w,dir | u·λ₂^rw | γ_tr | τ_wave (min) | τ_Vsim (h) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #universe-coordination | 14 | 85 | 41.1 | 46.82 | 83.12 | 41.4 | 10.84 | 0.4 | 0.018 |

## Prediction
*Written 2026-10-03, before running on this period.*

- **Card rules apply unchanged** (E-P, E-V, E-C definitions; tests T1–T7). Per-period verdicts are descriptive; the scaling test (P1, P5) is cross-period.
- **H31 (model D):** if this block's events are uncensored, their τ should sit on the cross-period line τ = c/λ₂^w,sym. Blocks with a larger λ₂^w,sym should be faster.
- **My prior (card):** the timing is set by task structure and announcements, so this period's τ will not track λ₂ beyond noise. E-P rises will be mostly abrupt (ρ ≤ 1 window), and E-C, if present, will be a convergence over days (τ_C 2–15 h).
- **Period-specific:** The hub was fixed by the goal (H11: spread carried by fields, own worlds plus a hub). I expect the hub E-P event, if any, to be frozen or locked to day 1 (field), and no graph dependence.
- **Counts against H31 here:** uncensored events whose τ is far off the calibrated line (outside the 80% LOPO interval), or a room contrast with the opposite sign to D.

## Result
| Block | E-P projects | consensus (frozen at start / instant / uncensored) | τ_P (h), uncensored | rise (windows) | kick-locked | M_λ forecast (h) | M0 forecast (h) | E-C kind | E-C τ (h) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #universe-coordination | 4 | 1 (1 / 0 / 0) | – | – | 1/1 | – | – | divergence | 13.6 |
- No uncensored E-P event: 1 frozen at the period start (kick-locked by construction) and 0 *instant* (criterion met in the onset window mid-period: a one-window herding wave). By the card's rule both are left-censored, so there is no τ to test.
- **E-C divergence:** content alignment starts high after the kickoff (A₀ = 0.53) and relaxes to A∞ = 0.30 with τ = 13.6 h. The field imposes the alignment and the dynamics dissolve it, the opposite of consensus formation.

Data: `data/processed/H31-consensus-time-spectral-gap/G40/`, `events_ep_w30.parquet`, `events_ec.parquet`.

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
| #universe-coordination | 46.8 → 46.7 | 4 projects; 1 consensus (1 / 0 / 0); τ – | 4 projects; 1 consensus (1 / 0 / 0); τ – | 3 projects; 1 consensus (1 / 0 / 0); τ – |
