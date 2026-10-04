# H28 × G26: Elect a village leader (2026-01-05 → 2026-01-12)

**Verdict:** mixed (P1 weak)
**Verdict (1b):** mixed (ledger visibility: κ +1.07 ± 0.42, z_shift +0.2, κ_lead +2.33)
**Role:** replication (exploratory (herding))
**Period:** regime I · mode C · 10 agents on the roster · 5 non-holdout days.

## Why this period
H11 herding (z_local +3.4); the week's coordination ran through chat votes, not repos; ≈ 120 links.

## Prediction
*Written 2026-10-04, before running on this period.*

Card rules (P1–P10, Amendment 1) apply; tested only if ≥ 30 arrivals and ≥ 20 links to universe projects.

- **Here:** P1 weak: links matter less when the coordinating object is a vote. R_link < 0.2.
- **Counts against:** κ̂ ≤ 0 or inside the link time-shift null; κ_lead ≈ κ; κ vanishing with the momentum control; an effect only in returns.

## Result
*Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H28-links-spread-herding/G26/round1.json`).* 220 arrivals (172 first), 124 links to 30 universe projects, 68 arrivals within 60 min of a visible link. Tested.

| Test | Observed | Rule | Verdict |
| --- | --- | --- | --- |
| P1 κ (any visible link, last 60 min) | +1.09 ± 0.43 (e^κ 2.99); p 0.0107; z_shift +0.4 (null +1.00 ± 0.22, n = 99) | κ > 0, z ≥ 2, p < 0.05 | weak |
| P2a lead placebo | κ_lead +2.33; κ − κ_lead -2.01 (one-sided p 1) | κ − κ_lead > 0, p < 0.05 | fail |
| P2b momentum control | κ +0.95 (p 0.0211); momentum +1.10 | ≥ 50% of κ, p < 0.05 | pass |
| P3a naive agents | κ +1.13 ± 0.54 (p 0.0372); first arrivals 172 | κ > 0 | pass |
| P3b pre-trend (O/E) | pre 3.64 (65 obs), post 5.95 (62 obs) | pre excess < ½ post excess | fail |
| P4 dose | d11 +1.36 (n_ev 39); d12 +0.81 (n_ev 5); d13 -15.51 (n_ev 0); dS2 +0.57 (n_ev 24); CV complex − simple +2.8 | 1-link HR > 1; S2 adds < 50% | fail |
| P5 λ (extra arrivals per exposure) | 0.053 [0.014, 0.140]; N_exp 858 | 0.01–0.15 | pass |
| P6 R_link | 0.21 [0.05, 0.55]; R_all (links + occupancy) 0.39 | < 0.5 | pass |
| P10 occupancy J | J +0.91 (pd FE +0.45); without links +1.42 | J > 0 both; drop < 50% | pass |
| P7 counterfactual peak occupancy | f=0.5 ×0.94; f=0 ×0.68; cap ×0.95; burst f=0 ×0.67 | f=0: 0.70–0.90 (≥ 0.5) | fail |
| P7 calibration (unfitted) | observed peak 8 vs sim [5, 10]; burst 8 vs [5, 10] | inside 90% | pass |
| P8 latency (median excess lag) | 2 min; excess 0–15 +181.8, 15–60 -84.7, 60–240 -169.6 | post-NE09 < pre | – |

## Scorecard (period-specific axes)
- **C:** link time-shift null z +0.4; held-out (quarter-blocked) Δ log-lik primary − occupancy-only -20.6.
- **D:** simulated pile-on calibration inside the 90% interval.
- **H:** lead not beaten; momentum survived.

## Notes
- *Post hoc robustness (coordinator request, 2026-10-04):* on the deterministic shared labels (`project_states.parquet`, 30 min, window switches) κ = +0.36 ± 1.13 (p 0.747; 26 switches), z_shift -4.8.
- *Post hoc short-lag check:* visible link in the last 15 min b = +0.69 ± 0.36 (z vs shift null +2.8); link arriving in the next 15 min b = +2.71 ± 0.21; lag − lead -2.02 (one-sided p 1). Action-only latency: median excess lag 2 min.
- Holdout days: none in this period's build (non-holdout days only).
