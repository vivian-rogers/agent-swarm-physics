# H28 × G25: Create a digital museum of 2025 (2025-12-29 → 2026-01-05)

**Verdict:** mixed (P1 weak)
**Verdict (1b):** mixed (ledger visibility: κ +1.17 ± 0.43, z_shift +0.1, κ_lead +2.76)
**Role:** exploratory (herding)
**Period:** regime I · mode C · 10 agents on the roster · 5 non-holdout days.

## Why this period
H11 herding (z_local +3.0); exhibits in shared repos, ≈ 200 links.

## Prediction
*Written 2026-10-04, before running on this period.*

Card rules (P1–P10, Amendment 1) apply; tested only if ≥ 30 arrivals and ≥ 20 links to universe projects.

- **Here:** P1 supported, e^κ ≈ 2–4; R_link 0.1–0.3.
- **Counts against:** κ̂ ≤ 0 or inside the link time-shift null; κ_lead ≈ κ; κ vanishing with the momentum control; an effect only in returns.

## Result
*Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H28-links-spread-herding/G25/round1.json`).* 111 arrivals (78 first), 203 links to 20 universe projects, 53 arrivals within 60 min of a visible link. Tested.

| Test | Observed | Rule | Verdict |
| --- | --- | --- | --- |
| P1 κ (any visible link, last 60 min) | +1.15 ± 0.43 (e^κ 3.16); p 0.0075; z_shift -0.0 (null +1.16 ± 0.26, n = 99) | κ > 0, z ≥ 2, p < 0.05 | weak |
| P2a lead placebo | κ_lead +2.77; κ − κ_lead -2.07 (one-sided p 0.997) | κ − κ_lead > 0, p < 0.05 | fail |
| P2b momentum control | κ +1.15 (p 0.00677); momentum +0.33 | ≥ 50% of κ, p < 0.05 | pass |
| P3a naive agents | κ +1.12 ± 0.67 (p 0.0926); first arrivals 78 | κ > 0 | fail |
| P3b pre-trend (O/E) | pre 2.57 (29 obs), post 4.43 (26 obs) | pre excess < ½ post excess | pass |
| P4 dose | d11 +1.27 (n_ev 9); d12 +0.64 (n_ev 5); d13 +1.97 (n_ev 2); dS2 +1.86 (n_ev 37); CV complex − simple -8.3 | 1-link HR > 1; S2 adds < 50% | pass |
| P5 λ (extra arrivals per exposure) | 0.029 [0.010, 0.078]; N_exp 1249 | 0.01–0.15 | pass |
| P6 R_link | 0.33 [0.11, 0.88]; R_all (links + occupancy) 0.45 | < 0.5 | pass |
| P10 occupancy J | J +0.87 (pd FE -0.10); without links +1.44 | J > 0 both; drop < 50% | fail |
| P7 counterfactual peak occupancy | f=0.5 ×0.93; f=0 ×0.61; cap ×0.94; burst f=0 ×0.61 | f=0: 0.70–0.90 (≥ 0.5) | fail |
| P7 calibration (unfitted) | observed peak 9 vs sim [5, 10]; burst 9 vs [5, 10] | inside 90% | pass |
| P8 latency (median excess lag) | 8 min; excess 0–15 +129.2, 15–60 -0.4, 60–240 -171.0 | post-NE09 < pre | – |

## Scorecard (period-specific axes)
- **C:** link time-shift null z -0.0; held-out (quarter-blocked) Δ log-lik primary − occupancy-only -1.5.
- **D:** simulated pile-on calibration inside the 90% interval.
- **H:** lead not beaten; momentum survived.

## Notes
- *Post hoc robustness (coordinator request, 2026-10-04):* on the deterministic shared labels (`project_states.parquet`, 30 min, window switches) κ = +1.85 ± 0.38 (p 9.12e-07; 40 switches), z_shift -0.3.
- *Post hoc short-lag check:* visible link in the last 15 min b = +0.70 ± 0.36 (z vs shift null +3.0); link arriving in the next 15 min b = +1.81 ± 0.47; lag − lead -1.11 (one-sided p 0.964). Action-only latency: median excess lag 8 min.
- Holdout days: none in this period's build (non-holdout days only).
