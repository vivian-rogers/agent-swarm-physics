# H28 × G42: Run your own Youtube channel! (2026-05-18 → 2026-05-25)

**Verdict:** supported (P1 supported)
**Role:** exploratory (contrast)
**Period:** regime III · mode I · 16 agents on the roster · 5 non-holdout days.

## Why this period
Contrast (own channels; H11 no herding). ≈ 100 links.

## Prediction
*Written 2026-10-04, before running on this period.*

Card rules (P1–P10, Amendment 1) apply; tested only if ≥ 30 arrivals and ≥ 20 links to universe projects.

- **Here:** P9: λ below the shared-artifact median; P1 weak or failed.
- **Counts against:** κ̂ ≤ 0 or inside the link time-shift null; κ_lead ≈ κ; κ vanishing with the momentum control; an effect only in returns.

## Result
*Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H28-links-spread-herding/G42/round1.json`).* 143 arrivals (53 first), 101 links to 15 universe projects, 21 arrivals within 60 min of a visible link. Tested.

| Test | Observed | Rule | Verdict |
| --- | --- | --- | --- |
| P1 κ (any visible link, last 60 min) | +0.97 ± 0.32 (e^κ 2.64); p 0.00238; z_shift +2.0 (null +0.31 ± 0.33, n = 99) | κ > 0, z ≥ 2, p < 0.05 | supported |
| P2a lead placebo | κ_lead +0.46; κ − κ_lead +0.40 (one-sided p 0.162) | κ − κ_lead > 0, p < 0.05 | fail |
| P2b momentum control | κ +0.96 (p 0.00232); momentum +0.35 | ≥ 50% of κ, p < 0.05 | pass |
| P2c other-room placebo | κ_same +0.95; κ_other -0.87 ± 0.52 (2321 exposed rows, 5 arrivals) | κ_other < κ_same, CI ∋ 0 | pass |
| P3a naive agents | κ +1.01 ± 0.49 (p 0.04); first arrivals 53 | κ > 0 | pass |
| P3b pre-trend (O/E) | pre 1.58 (6 obs), post 1.39 (5 obs) | pre excess < ½ post excess | fail |
| P4 dose | d11 +0.62 (n_ev 8); d12 +0.69 (n_ev 3); d13 +1.79 (n_ev 8); dS2 +2.91 (n_ev 2); CV complex − simple -41.5 | 1-link HR > 1; S2 adds < 50% | pass |
| P5 λ (extra arrivals per exposure) | 0.014 [0.005, 0.029]; N_exp 904 | 0.01–0.15 | pass |
| P6 R_link | 0.09 [0.03, 0.18]; R_all (links + occupancy) -0.56 | < 0.5 | pass |
| P10 occupancy J | J -0.90 (pd FE -1.29); without links -0.81 | J > 0 both; drop < 50% | fail |
| P7 counterfactual peak occupancy | f=0.5 ×1.00; f=0 ×1.00; cap ×1.00; burst f=0 ×0.99 | f=0: 0.70–0.90 (≥ 0.5) | fail |
| P7 calibration (unfitted) | observed peak 7 vs sim [1, 3]; burst 7 vs [1, 3] | inside 90% | fail |
| P8 latency (median excess lag) | 28 min; excess 0–15 +11.4, 15–60 +12.9, 60–240 -9.6 | post-NE09 < pre | – |

## Scorecard (period-specific axes)
- **C:** link time-shift null z +2.0; held-out (quarter-blocked) Δ log-lik primary − occupancy-only -42.6.
- **D:** simulated pile-on calibration outside the 90% interval.
- **H:** lead not beaten; momentum survived; other-room placebo clean.

## Notes
- *Post hoc robustness (coordinator request, 2026-10-04):* on the deterministic shared labels (`project_states.parquet`, 30 min, window switches) κ = +1.46 ± 0.59 (p 0.0133; 23 switches), z_shift +1.5.
- *Post hoc short-lag check:* visible link in the last 15 min b = +0.02 ± 0.53 (z vs shift null -0.1); link arriving in the next 15 min b = +0.55 ± 0.38; lag − lead -0.53 (one-sided p 0.807). Action-only latency: median excess lag 28 min.
- Holdout days: none in this period's build (non-holdout days only).
