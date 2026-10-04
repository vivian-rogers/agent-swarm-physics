# H28 × G39: Build your own interactive world! (2026-04-27 → 2026-05-04)

**Verdict:** supported (P1 supported)
**Verdict (1b):** supported (ledger visibility: κ +1.11 ± 0.21, z_shift +3.5, κ_lead +0.14; work switches κ -0.23 ± 0.71, z +0.2, lead -0.99)
**Role:** exploratory (contrast)
**Period:** regime III · mode I · 15 agents on the roster · 5 non-holdout days.

## Why this period
Contrast (own-artifact week; H11 found spread by fields, no herding). ≈ 680 links (agents advertise their own worlds).

## Prediction
*Written 2026-10-04, before running on this period.*

Card rules (P1–P10, Amendment 1) apply; tested only if ≥ 30 arrivals and ≥ 20 links to universe projects.

- **Here:** P9: λ below the shared-artifact median; P1 may still pass (visits to others' worlds after a link) but R_link small.
- **Counts against:** κ̂ ≤ 0 or inside the link time-shift null; κ_lead ≈ κ; κ vanishing with the momentum control; an effect only in returns.

## Result
*Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H28-links-spread-herding/G39/round1.json`).* 355 arrivals (134 first), 684 links to 24 universe projects, 151 arrivals within 60 min of a visible link. Tested.

| Test | Observed | Rule | Verdict |
| --- | --- | --- | --- |
| P1 κ (any visible link, last 60 min) | +1.19 ± 0.20 (e^κ 3.27); p 5.85e-09; z_shift +3.9 (null +0.66 ± 0.13, n = 99) | κ > 0, z ≥ 2, p < 0.05 | supported |
| P2a lead placebo | κ_lead +0.12; κ − κ_lead +1.01 (one-sided p 0.00202) | κ − κ_lead > 0, p < 0.05 | pass |
| P2b momentum control | κ +1.19 (p 7.54e-09); momentum +0.07 | ≥ 50% of κ, p < 0.05 | pass |
| P2c other-room placebo | κ_same +0.89; κ_other -2.10 ± 0.81 (8723 exposed rows, 4 arrivals) | κ_other < κ_same, CI ∋ 0 | fail |
| P3a naive agents | κ +1.44 ± 0.30 (p 2.13e-06); first arrivals 134 | κ > 0 | pass |
| P3b pre-trend (O/E) | pre 0.86 (6 obs), post 1.88 (28 obs) | pre excess < ½ post excess | pass |
| P4 dose | d11 +1.01 (n_ev 46); d12 +1.59 (n_ev 40); d13 +1.20 (n_ev 54); dS2 +2.14 (n_ev 11); CV complex − simple +1.5 | 1-link HR > 1; S2 adds < 50% | fail |
| P5 λ (extra arrivals per exposure) | 0.019 [0.012, 0.029]; N_exp 5669 | 0.01–0.15 | pass |
| P6 R_link | 0.30 [0.19, 0.46]; R_all (links + occupancy) 0.04 | < 0.5 | pass |
| P10 occupancy J | J -0.53 (pd FE -1.19); without links -0.17 | J > 0 both; drop < 50% | fail |
| P7 counterfactual peak occupancy | f=0.5 ×0.94; f=0 ×0.77; cap ×0.92; burst f=0 ×0.79 | f=0: 0.70–0.90 (≥ 0.5) | pass |
| P7 calibration (unfitted) | observed peak 8 vs sim [4, 9]; burst 6 vs [3, 8] | inside 90% | pass |
| P8 latency (median excess lag) | 28 min; excess 0–15 +13.7, 15–60 -22.6, 60–240 -22.6 | post-NE09 < pre | – |

## Scorecard (period-specific axes)
- **C:** link time-shift null z +3.9; held-out (quarter-blocked) Δ log-lik primary − occupancy-only -14.7.
- **D:** simulated pile-on calibration inside the 90% interval.
- **H:** lead beaten; momentum survived; other-room placebo not clean.

## Notes
- *Post hoc robustness (coordinator request, 2026-10-04):* on the deterministic shared labels (`project_states.parquet`, 30 min, window switches) κ = -0.45 ± 0.91 (p 0.616; 27 switches), z_shift -0.0.
- *Post hoc short-lag check:* visible link in the last 15 min b = +0.37 ± 0.21 (z vs shift null +2.0); link arriving in the next 15 min b = +0.06 ± 0.18; lag − lead +0.31 (one-sided p 0.117). Action-only latency: median excess lag 22 min.
- Holdout days: none in this period's build (non-holdout days only).
