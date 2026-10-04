# H28 × G19: Create a popular daily puzzle game like Wordle (2025-11-03 → 2025-11-17)

**Verdict:** mixed (P1 weak)
**Verdict (1b):** supported (ledger visibility: κ +1.26 ± 0.26, z_shift +3.2, κ_lead +1.90)
**Role:** exploratory (herding)
**Period:** regime I · mode C · 8 agents on the roster · 10 non-holdout days · pre-NE09 visibility rule.

## Why this period
H11 herding (z_local +3.9) but the build repo dominated from the start (frozen consensus). Pre-NE09.

## Prediction
*Written 2026-10-04, before running on this period.*

Card rules (P1–P10, Amendment 1) apply; tested only if ≥ 30 arrivals and ≥ 20 links to universe projects.

- **Here:** P1 weak (most agents are already on the dominant repo, so few susceptible exposures); R_link < 0.2; slow kernel (P8).
- **Counts against:** κ̂ ≤ 0 or inside the link time-shift null; κ_lead ≈ κ; κ vanishing with the momentum control; an effect only in returns.

## Result
*Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H28-links-spread-herding/G19/round1.json`).* 256 arrivals (103 first), 369 links to 30 universe projects, 100 arrivals within 60 min of a visible link. Tested.

| Test | Observed | Rule | Verdict |
| --- | --- | --- | --- |
| P1 κ (any visible link, last 60 min) | +0.66 ± 0.32 (e^κ 1.93); p 0.0398; z_shift -0.8 (null +0.79 ± 0.17, n = 99) | κ > 0, z ≥ 2, p < 0.05 | weak |
| P2a lead placebo | κ_lead +1.96; κ − κ_lead -1.41 (one-sided p 0.999) | κ − κ_lead > 0, p < 0.05 | fail |
| P2b momentum control | κ +0.67 (p 0.0338); momentum +0.34 | ≥ 50% of κ, p < 0.05 | pass |
| P3a naive agents | κ +0.79 ± 0.71 (p 0.265); first arrivals 103 | κ > 0 | fail |
| P3b pre-trend (O/E) | pre 4.60 (39 obs), post 6.61 (33 obs) | pre excess < ½ post excess | fail |
| P4 dose | d11 +1.08 (n_ev 44); d12 -0.53 (n_ev 5); d13 +0.45 (n_ev 6); dS2 +0.59 (n_ev 45); CV complex − simple -13.8 | 1-link HR > 1; S2 adds < 50% | pass |
| P5 λ (extra arrivals per exposure) | 0.048 [0.008, 0.117]; N_exp 1004 | 0.01–0.15 | pass |
| P6 R_link | 0.19 [0.03, 0.46]; R_all (links + occupancy) 0.46 | < 0.5 | pass |
| P10 occupancy J | J +1.09 (pd FE -0.04); without links +1.45 | J > 0 both; drop < 50% | fail |
| P7 counterfactual peak occupancy | f=0.5 ×0.98; f=0 ×0.83; cap ×0.96; burst f=0 ×0.83 | f=0: 0.70–0.90 (≥ 0.5) | pass |
| P7 calibration (unfitted) | observed peak 8 vs sim [5, 7]; burst 8 vs [4, 7] | inside 90% | fail |
| P8 latency (median excess lag) | 2 min; excess 0–15 +171.5, 15–60 -61.2, 60–240 -204.8 | post-NE09 < pre | – |

## Scorecard (period-specific axes)
- **C:** link time-shift null z -0.8; held-out (quarter-blocked) Δ log-lik primary − occupancy-only +30.3.
- **D:** simulated pile-on calibration outside the 90% interval.
- **H:** lead not beaten; momentum survived.

## Notes
- *Post hoc robustness (coordinator request, 2026-10-04):* on the deterministic shared labels (`project_states.parquet`, 30 min, window switches) κ = +0.66 ± 0.25 (p 0.00862; 90 switches), z_shift -4.1.
- *Post hoc short-lag check:* visible link in the last 15 min b = +0.01 ± 0.21 (z vs shift null +2.2); link arriving in the next 15 min b = +1.99 ± 0.30; lag − lead -1.98 (one-sided p 1). Action-only latency: median excess lag 8 min.
- Holdout days: none in this period's build (non-holdout days only).
