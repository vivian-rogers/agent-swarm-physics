# H28 × G37: Pick your own goal! (2026-03-30 → 2026-04-02)

**Verdict:** mixed (P1 weak)
**Verdict (1b):** supported (ledger visibility: κ +1.60 ± 0.33, z_shift +2.6, κ_lead +1.27; work switches κ +2.02 ± 0.43, z +1.6, lead +1.43)
**Role:** exploratory (candidate)
**Period:** regime III · mode F · 12 agents on the roster · 3 non-holdout days.

## Why this period
Named candidate; free 3-day period; two rooms (#best, #rest) so the other-room placebo applies; ≈ 90 links (low).

## Prediction
*Written 2026-10-04, before running on this period.*

Card rules (P1–P10, Amendment 1) apply; tested only if ≥ 30 arrivals and ≥ 20 links to universe projects.

- **Here:** P1 weak-to-supported; room placebo (P2c) underpowered (cross-room projects rarely overlap).
- **Counts against:** κ̂ ≤ 0 or inside the link time-shift null; κ_lead ≈ κ; κ vanishing with the momentum control; an effect only in returns.

## Result
*Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H28-links-spread-herding/G37/round1.json`).* 191 arrivals (99 first), 91 links to 23 universe projects, 33 arrivals within 60 min of a visible link. Tested.

| Test | Observed | Rule | Verdict |
| --- | --- | --- | --- |
| P1 κ (any visible link, last 60 min) | +1.54 ± 0.32 (e^κ 4.65); p 2.09e-06; z_shift +1.8 (null +1.18 ± 0.19, n = 99) | κ > 0, z ≥ 2, p < 0.05 | weak |
| P2a lead placebo | κ_lead +1.29; κ − κ_lead -0.30 (one-sided p 0.744) | κ − κ_lead > 0, p < 0.05 | fail |
| P2b momentum control | κ +1.54 (p 1.75e-06); momentum +0.03 | ≥ 50% of κ, p < 0.05 | pass |
| P2c other-room placebo | κ_same +1.44; κ_other -1.30 ± 0.58 (1425 exposed rows, 2 arrivals) | κ_other < κ_same, CI ∋ 0 | fail |
| P3a naive agents | κ +1.61 ± 0.37 (p 1.74e-05); first arrivals 99 | κ > 0 | pass |
| P3b pre-trend (O/E) | pre 2.26 (13 obs), post 4.18 (12 obs) | pre excess < ½ post excess | pass |
| P4 dose | d11 +1.49 (n_ev 16); d12 +1.05 (n_ev 2); d13 +1.08 (n_ev 2); dS2 +1.96 (n_ev 13); CV complex − simple -7.5 | 1-link HR > 1; S2 adds < 50% | pass |
| P5 λ (extra arrivals per exposure) | 0.068 [0.033, 0.129]; N_exp 382 | 0.01–0.15 | pass |
| P6 R_link | 0.14 [0.07, 0.26]; R_all (links + occupancy) 0.15 | < 0.5 | pass |
| P10 occupancy J | J +0.03 (pd FE -0.70); without links +0.40 | J > 0 both; drop < 50% | fail |
| P7 counterfactual peak occupancy | f=0.5 ×0.92; f=0 ×0.75; cap ×0.91; burst f=0 ×0.77 | f=0: 0.70–0.90 (≥ 0.5) | pass |
| P7 calibration (unfitted) | observed peak 7 vs sim [4, 9]; burst 5 vs [3, 8] | inside 90% | pass |
| P8 latency (median excess lag) | 62 min; excess 0–15 +8.5, 15–60 -11.6, 60–240 +1.1 | post-NE09 < pre | – |

## Scorecard (period-specific axes)
- **C:** link time-shift null z +1.8; held-out (quarter-blocked) Δ log-lik primary − occupancy-only +8.6.
- **D:** simulated pile-on calibration inside the 90% interval.
- **H:** lead not beaten; momentum survived; other-room placebo not clean.

## Notes
- *Post hoc robustness (coordinator request, 2026-10-04):* on the deterministic shared labels (`project_states.parquet`, 30 min, window switches) κ = +1.97 ± 0.49 (p 6.76e-05; 56 switches), z_shift +0.5.
- *Post hoc short-lag check:* visible link in the last 15 min b = +0.88 ± 0.35 (z vs shift null +1.0); link arriving in the next 15 min b = +0.77 ± 0.38; lag − lead +0.12 (one-sided p 0.401). Action-only latency: median excess lag 62 min.
- Holdout days: none in this period's build (non-holdout days only).
