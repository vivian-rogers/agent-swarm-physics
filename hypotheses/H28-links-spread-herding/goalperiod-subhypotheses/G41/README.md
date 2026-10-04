# H28 × G41: Perform novel research! (2026-05-11 → 2026-05-18)

**Verdict:** mixed (P1 weak)
**Verdict (1b):** mixed (ledger visibility: κ +0.77 ± 0.24, z_shift -0.9, κ_lead +1.81; work switches κ +1.50 ± 0.35, z +2.3, lead +1.59)
**Role:** exploratory (candidate)
**Period:** regime III · mode I · 15 agents on the roster · 5 non-holdout days.

## Why this period
Named candidate; ≈ 11 #rest agents converged on one topic (H11 βJ_CW +4.3, local-shift z +4.2); two rooms with different topics.

## Prediction
*Written 2026-10-04, before running on this period.*

Card rules (P1–P10, Amendment 1) apply; tested only if ≥ 30 arrivals and ≥ 20 links to universe projects.

- **Here:** P1 supported (e^κ 2–4); room placebo κ_other ≈ 0; R_link 0.1–0.3.
- **Counts against:** κ̂ ≤ 0 or inside the link time-shift null; κ_lead ≈ κ; κ vanishing with the momentum control; an effect only in returns.

## Result
*Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H28-links-spread-herding/G41/round1.json`).* 312 arrivals (142 first), 443 links to 30 universe projects, 100 arrivals within 60 min of a visible link. Tested.

| Test | Observed | Rule | Verdict |
| --- | --- | --- | --- |
| P1 κ (any visible link, last 60 min) | +0.82 ± 0.23 (e^κ 2.27); p 0.000357; z_shift -0.9 (null +0.99 ± 0.19, n = 99) | κ > 0, z ≥ 2, p < 0.05 | weak |
| P2a lead placebo | κ_lead +1.80; κ − κ_lead -1.40 (one-sided p 1) | κ − κ_lead > 0, p < 0.05 | fail |
| P2b momentum control | κ +0.85 (p 0.000242); momentum +0.63 | ≥ 50% of κ, p < 0.05 | pass |
| P2c other-room placebo | κ_same +0.61; κ_other -2.02 ± 0.58 (5251 exposed rows, 3 arrivals) | κ_other < κ_same, CI ∋ 0 | fail |
| P3a naive agents | κ +1.66 ± 0.52 (p 0.00125); first arrivals 142 | κ > 0 | pass |
| P3b pre-trend (O/E) | pre 4.56 (37 obs), post 6.62 (25 obs) | pre excess < ½ post excess | fail |
| P4 dose | d11 +0.61 (n_ev 31); d12 +0.39 (n_ev 10); d13 +1.30 (n_ev 19); dS2 +1.28 (n_ev 40); CV complex − simple -3.9 | 1-link HR > 1; S2 adds < 50% | pass |
| P5 λ (extra arrivals per exposure) | 0.020 [0.009, 0.037]; N_exp 2740 | 0.01–0.15 | pass |
| P6 R_link | 0.18 [0.08, 0.33]; R_all (links + occupancy) 0.34 | < 0.5 | pass |
| P10 occupancy J | J +0.38 (pd FE -0.46); without links +0.75 | J > 0 both; drop < 50% | fail |
| P7 counterfactual peak occupancy | f=0.5 ×0.90; f=0 ×0.77; cap ×0.91; burst f=0 ×0.80 | f=0: 0.70–0.90 (≥ 0.5) | pass |
| P7 calibration (unfitted) | observed peak 10 vs sim [5, 12]; burst 10 vs [4, 9] | inside 90% | pass |
| P8 latency (median excess lag) | 8 min; excess 0–15 +93.3, 15–60 -56.0, 60–240 -65.0 | post-NE09 < pre | – |

## Scorecard (period-specific axes)
- **C:** link time-shift null z -0.9; held-out (quarter-blocked) Δ log-lik primary − occupancy-only -26.7.
- **D:** simulated pile-on calibration inside the 90% interval.
- **H:** lead not beaten; momentum survived; other-room placebo not clean.

## Notes
- *Post hoc robustness (coordinator request, 2026-10-04):* on the deterministic shared labels (`project_states.parquet`, 30 min, window switches) κ = +1.36 ± 0.44 (p 0.00215; 63 switches), z_shift +0.7.
- *Post hoc short-lag check:* visible link in the last 15 min b = +0.57 ± 0.23 (z vs shift null +2.0); link arriving in the next 15 min b = +1.30 ± 0.17; lag − lead -0.73 (one-sided p 0.992). Action-only latency: median excess lag 8 min.
- Holdout days: none in this period's build (non-holdout days only).
