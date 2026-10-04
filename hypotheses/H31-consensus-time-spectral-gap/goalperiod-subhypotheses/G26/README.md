# H31 × G26: Elect a village leader. They choose this week’s goal! (2026-01-05 → 2026-01-12)

**Verdict:** failed
**Role:** exploratory (card candidate; E-P + E-C)
**Period:** regime I · mode C · 10 agents · #general · 5 non-holdout days (15.8 active h).

## Why this period
Named by HH115 and H11 as a consensus period. H11 project labels are dense enough for E-P (≥ 50% of room-windows have ≥ 3 labeled agents).

**Predictors** (whole block-period; computed before any outcome):

| Block | N_b | msgs/h | u (reads/h) | λ₂^w,sym (1/h) | λ₂^w,dir | u·λ₂^rw | γ_tr | τ_wave (min) | τ_Vsim (h) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #general | 10 | 133 | 53.0 | 89.10 | 131.56 | 54.8 | 14.81 | 1.0 | 0.044 |

## Prediction
*Written 2026-10-03, before running on this period.*

- **Card rules apply unchanged** (E-P, E-V, E-C definitions; tests T1–T7). Per-period verdicts are descriptive; the scaling test (P1, P5) is cross-period.
- **H31 (model D):** if this block's events are uncensored, their τ should sit on the cross-period line τ = c/λ₂^w,sym. Blocks with a larger λ₂^w,sym should be faster.
- **My prior (card):** the timing is set by task structure and announcements, so this period's τ will not track λ₂ beyond noise. E-P rises will be mostly abrupt (ρ ≤ 1 window), and E-C, if present, will be a convergence over days (τ_C 2–15 h).
- **Period-specific:** Election week. E-P project events should be gradual or absent (H11: project labels gradual). **E-V:** the runoff consensus should come within ≤ 1 h of the first runoff message (P10), faster than the E-P-calibrated M_λ forecast. That would make it a decision field, not diffusion.
- **Counts against H31 here:** uncensored events whose τ is far off the calibrated line (outside the 80% LOPO interval), or a room contrast with the opposite sign to D.

## Result
| Block | E-P projects | consensus (frozen at start / instant / uncensored) | τ_P (h), uncensored | rise (windows) | kick-locked | M_λ forecast (h) | M0 forecast (h) | E-C kind | E-C τ (h) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| #general | 8 | 7 (1 / 6 / 0) | – | – | 2/7 | – | – | none | – |
- **E-V (runoff):** onset at 0.0 active h. The winner's declared share reached ≥ 0.5 (≥ 3 declared) after τ_V = 12.55 h. The M_λ forecast was 1.22 h (80%: 0.19–5.36). Before the runoff, the top candidate's declared share was 1.00 (n = 1).
- **E-V post hoc:** the pre-registered onset (first runoff-word message) fired at the period start, as H11's onset rule did. The winner's share rose from 0.22 to ≥ 0.5 within 0.76 h (last window below 0.25 → first ≥ 0.5): an abrupt decision step.
- No uncensored E-P event: 1 frozen at the period start (kick-locked by construction) and 6 *instant* (criterion met in the onset window mid-period: a one-window herding wave). By the card's rule both are left-censored, so there is no τ to test.

Data: `data/processed/H31-consensus-time-spectral-gap/G26/`, `events_ep_w30.parquet`, `events_ec.parquet`.

## Scorecard (period-specific axes)
- **C (period level):** the per-event leave-one-period-out comparison of M_λ (or M_tr) vs the constant is listed above.
- **G:** the #26 runoff winner matches the dataset's summary (DeepSeek-V3.2).

## Notes
- 2026-10-03: folder and prediction written before the real-data run on this period.
- 2026-10-03: results filled from `analysis/explore.py` (round 1).
