# H28 × G24: Do random acts of kindness! (2025-12-22 → 2025-12-29)

**Verdict:** supported (P1 supported)
**Verdict (1b):** supported (ledger visibility: κ +2.90 ± 0.63, z_shift +5.1, κ_lead +1.71)
**Role:** exploratory (herding)
**Period:** regime I · mode C · 10 agents on the roster · 5 non-holdout days.

## Why this period
H11 herding (z_local +2.4); small link volume (45 links to universe projects), post-NE09 (first period after it).

## Prediction
*Written 2026-10-04, before running on this period.*

Card rules (P1–P10, Amendment 1) apply; tested only if ≥ 30 arrivals and ≥ 20 links to universe projects.

- **Here:** Low power: P1 weak at best; λ imprecise.
- **Counts against:** κ̂ ≤ 0 or inside the link time-shift null; κ_lead ≈ κ; κ vanishing with the momentum control; an effect only in returns.

## Result
*Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H28-links-spread-herding/G24/round1.json`).* 68 arrivals (55 first), 45 links to 12 universe projects, 32 arrivals within 60 min of a visible link. Tested.

| Test | Observed | Rule | Verdict |
| --- | --- | --- | --- |
| P1 κ (any visible link, last 60 min) | +2.90 ± 0.63 (e^κ 18.12); p 3.76e-06; z_shift +5.1 (null +0.31 ± 0.50, n = 99) | κ > 0, z ≥ 2, p < 0.05 | supported |
| P2a lead placebo | κ_lead +1.71; κ − κ_lead +1.16 (one-sided p 0.0623) | κ − κ_lead > 0, p < 0.05 | fail |
| P2b momentum control | κ +2.83 (p 7.25e-06); momentum +0.53 | ≥ 50% of κ, p < 0.05 | pass |
| P3a naive agents | κ +2.44 ± 0.84 (p 0.00352); first arrivals 55 | κ > 0 | pass |
| P3b pre-trend (O/E) | pre 1.10 (22 obs), post 2.55 (25 obs) | pre excess < ½ post excess | pass |
| P4 dose | d11 +2.74 (n_ev 10); d12 +3.58 (n_ev 3); d13 +4.62 (n_ev 1); dS2 +3.55 (n_ev 18); CV complex − simple -0.0 | 1-link HR > 1; S2 adds < 50% | pass |
| P5 λ (extra arrivals per exposure) | 0.110 [0.035, 0.315]; N_exp 275 | 0.01–0.15 | pass |
| P6 R_link | 0.44 [0.14, 1.27]; R_all (links + occupancy) 0.35 | < 0.5 | pass |
| P10 occupancy J | J -0.73 (pd FE -0.82); without links +0.70 | J > 0 both; drop < 50% | fail |
| P7 counterfactual peak occupancy | f=0.5 ×0.94; f=0 ×0.48; cap ×1.05; burst f=0 ×0.48 | f=0: 0.70–0.90 (≥ 0.5) | fail |
| P7 calibration (unfitted) | observed peak 8 vs sim [1, 9]; burst 8 vs [2, 9] | inside 90% | pass |
| P8 latency (median excess lag) | 8 min; excess 0–15 +54.9, 15–60 -10.0, 60–240 -46.3 | post-NE09 < pre | – |

## Scorecard (period-specific axes)
- **C:** link time-shift null z +5.1; held-out (quarter-blocked) Δ log-lik primary − occupancy-only +14.0.
- **D:** simulated pile-on calibration inside the 90% interval.
- **H:** lead not beaten; momentum survived.

## Notes
- *Post hoc robustness (coordinator request, 2026-10-04):* on the deterministic shared labels (`project_states.parquet`, 30 min, window switches) κ = +0.85 ± 0.71 (p 0.228; 30 switches), z_shift -0.4.
- *Post hoc short-lag check:* visible link in the last 15 min b = +2.70 ± 0.84 (z vs shift null +7.9); link arriving in the next 15 min b = +1.73 ± 0.40; lag − lead +0.97 (one-sided p 0.169). Action-only latency: median excess lag 8 min.
- Holdout days: none in this period's build (non-holdout days only).
