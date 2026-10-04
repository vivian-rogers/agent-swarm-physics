# H28 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 2026-05-11)

**Verdict:** supported (P1 supported)
**Role:** exploratory (contrast)
**Period:** regime III · mode C · 15 agents on the roster · 5 non-holdout days.

## Why this period
Contrast (own worlds plus a fixed hub; H11 no herding, z_N2 ≈ 0). One coordination room.

## Prediction
*Written 2026-10-04, before running on this period.*

Card rules (P1–P10, Amendment 1) apply; tested only if ≥ 30 arrivals and ≥ 20 links to universe projects.

- **Here:** P9: λ below the shared-artifact median.
- **Counts against:** κ̂ ≤ 0 or inside the link time-shift null; κ_lead ≈ κ; κ vanishing with the momentum control; an effect only in returns.

## Result
*Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H28-links-spread-herding/G40/round1.json`).* 248 arrivals (128 first), 358 links to 26 universe projects, 70 arrivals within 60 min of a visible link. Tested.

| Test | Observed | Rule | Verdict |
| --- | --- | --- | --- |
| P1 κ (any visible link, last 60 min) | +0.74 ± 0.31 (e^κ 2.10); p 0.0175; z_shift +6.0 (null -0.76 ± 0.25, n = 99) | κ > 0, z ≥ 2, p < 0.05 | supported |
| P2a lead placebo | κ_lead +0.11; κ − κ_lead +0.62 (one-sided p 0.124) | κ − κ_lead > 0, p < 0.05 | fail |
| P2b momentum control | κ +0.81 (p 0.00529); momentum +0.75 | ≥ 50% of κ, p < 0.05 | pass |
| P2c other-room placebo | κ_same +0.55; κ_other -1.53 ± 0.83 (1203 exposed rows, 4 arrivals) | κ_other < κ_same, CI ∋ 0 | pass |
| P3a naive agents | κ +1.11 ± 0.30 (p 0.000258); first arrivals 128 | κ > 0 | pass |
| P3b pre-trend (O/E) | pre 1.09 (30 obs), post 2.39 (34 obs) | pre excess < ½ post excess | pass |
| P4 dose | d11 +0.86 (n_ev 22); d12 +0.84 (n_ev 11); d13 +0.09 (n_ev 11); dS2 +1.06 (n_ev 26); CV complex − simple +4.8 | 1-link HR > 1; S2 adds < 50% | fail |
| P5 λ (extra arrivals per exposure) | 0.012 [0.004, 0.028]; N_exp 3041 | 0.01–0.15 | pass |
| P6 R_link | 0.15 [0.05, 0.34]; R_all (links + occupancy) 0.12 | < 0.5 | pass |
| P10 occupancy J | J -0.05 (pd FE -0.07); without links +0.17 | J > 0 both; drop < 50% | fail |
| P7 counterfactual peak occupancy | f=0.5 ×0.97; f=0 ×0.82; cap ×0.99; burst f=0 ×0.82 | f=0: 0.70–0.90 (≥ 0.5) | pass |
| P7 calibration (unfitted) | observed peak 14 vs sim [6, 13]; burst 13 vs [5, 13] | inside 90% | fail |
| P8 latency (median excess lag) | 8 min; excess 0–15 +143.5, 15–60 -22.9, 60–240 -7.7 | post-NE09 < pre | – |

## Scorecard (period-specific axes)
- **C:** link time-shift null z +6.0; held-out (quarter-blocked) Δ log-lik primary − occupancy-only -55.1.
- **D:** simulated pile-on calibration outside the 90% interval.
- **H:** lead not beaten; momentum survived; other-room placebo clean.

## Notes
- *Post hoc robustness (coordinator request, 2026-10-04):* on the deterministic shared labels (`project_states.parquet`, 30 min, window switches) κ = -0.79 ± 0.45 (p 0.0816; 29 switches), z_shift -0.0.
- *Post hoc short-lag check:* visible link in the last 15 min b = +1.64 ± 0.29 (z vs shift null +10.5); link arriving in the next 15 min b = +0.54 ± 0.27; lag − lead +1.10 (one-sided p 0.00825). Action-only latency: median excess lag 8 min.
- Holdout days: none in this period's build (non-holdout days only).
