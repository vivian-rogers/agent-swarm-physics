# H28 × G30: Adopt a park and get it cleaned! (2026-02-09 → 2026-02-16)

**Verdict:** supported (P1 supported)
**Role:** exploratory (herding)
**Period:** regime I · mode C · 11 agents on the roster · 5 non-holdout days.

## Why this period
H11 herding (z_local +3.5); one shared repo plus satellites; nudger starts 2026-02-10.

## Prediction
*Written 2026-10-04, before running on this period.*

Card rules (P1–P10, Amendment 1) apply; tested only if ≥ 30 arrivals and ≥ 20 links to universe projects.

- **Here:** P1 supported; the nudger is controlled by `auto30` (it does not post links).
- **Counts against:** κ̂ ≤ 0 or inside the link time-shift null; κ_lead ≈ κ; κ vanishing with the momentum control; an effect only in returns.

## Result
*Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H28-links-spread-herding/G30/round1.json`).* 263 arrivals (71 first), 313 links to 14 universe projects, 105 arrivals within 60 min of a visible link. Tested.

| Test | Observed | Rule | Verdict |
| --- | --- | --- | --- |
| P1 κ (any visible link, last 60 min) | +0.98 ± 0.23 (e^κ 2.68); p 1.29e-05; z_shift +3.7 (null +0.18 ± 0.22, n = 99) | κ > 0, z ≥ 2, p < 0.05 | supported |
| P2a lead placebo | κ_lead +1.14; κ − κ_lead -0.27 (one-sided p 0.767) | κ − κ_lead > 0, p < 0.05 | fail |
| P2b momentum control | κ +0.99 (p 9.29e-06); momentum +0.29 | ≥ 50% of κ, p < 0.05 | pass |
| P3a naive agents | κ +1.51 ± 0.80 (p 0.0577); first arrivals 71 | κ > 0 | fail |
| P3b pre-trend (O/E) | pre 1.48 (17 obs), post 4.73 (25 obs) | pre excess < ½ post excess | pass |
| P4 dose | d11 +0.51 (n_ev 15); d12 +0.85 (n_ev 11); d13 +0.77 (n_ev 3); dS2 +1.46 (n_ev 76); CV complex − simple -8.5 | 1-link HR > 1; S2 adds < 50% | pass |
| P5 λ (extra arrivals per exposure) | 0.086 [0.041, 0.150]; N_exp 766 | 0.01–0.15 | pass |
| P6 R_link | 0.25 [0.12, 0.44]; R_all (links + occupancy) 0.19 | < 0.5 | pass |
| P10 occupancy J | J -0.09 (pd FE -0.43); without links +0.20 | J > 0 both; drop < 50% | fail |
| P7 counterfactual peak occupancy | f=0.5 ×1.00; f=0 ×0.90; cap ×0.98; burst f=0 ×0.86 | f=0: 0.70–0.90 (≥ 0.5) | pass |
| P7 calibration (unfitted) | observed peak 11 vs sim [10, 11]; burst 11 vs [8, 11] | inside 90% | pass |
| P8 latency (median excess lag) | 2 min; excess 0–15 +189.6, 15–60 -156.2, 60–240 -185.7 | post-NE09 < pre | – |

## Scorecard (period-specific axes)
- **C:** link time-shift null z +3.7; held-out (quarter-blocked) Δ log-lik primary − occupancy-only +13.1.
- **D:** simulated pile-on calibration inside the 90% interval.
- **H:** lead not beaten; momentum survived.

## Notes
- *Post hoc robustness (coordinator request, 2026-10-04):* on the deterministic shared labels (`project_states.parquet`, 30 min, window switches) κ = +1.23 ± 0.46 (p 0.00798; 144 switches), z_shift +0.6.
- *Post hoc short-lag check:* visible link in the last 15 min b = +0.79 ± 0.19 (z vs shift null +6.0); link arriving in the next 15 min b = +1.24 ± 0.23; lag − lead -0.45 (one-sided p 0.927). Action-only latency: median excess lag 8 min.
- Holdout days: none in this period's build (non-holdout days only).
