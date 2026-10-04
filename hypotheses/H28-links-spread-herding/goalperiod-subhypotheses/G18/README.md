# H28 × G18: Reduce global poverty as much as you can (2025-10-20 → 2025-11-03)

**Verdict:** failed (P1 failed)
**Role:** exploratory (candidate)
**Period:** regime I · mode C · 8 agents on the roster · 10 non-holdout days · pre-NE09 visibility rule.

## Why this period
Named candidate. H11: herding (βJ_CW +5.0, local-shift z +4.1) with a last-day convergence of the whole swarm onto one repo. **Pre-NE09**: chat reached computer-use calls only at session boundaries, so visibility is the next `events_core` turn.

## Prediction
*Written 2026-10-04, before running on this period.*

Card rules (P1–P10, Amendment 1) apply; tested only if ≥ 30 arrivals and ≥ 20 links to universe projects.

- **Here:** P1 supported but with a slower kernel (more weight in 15–60 and 60–240 min than post-NE09 periods). The last-day convergence is deadline drive, so R_link is low (0.1–0.2). P8: median excess lag > 15 min.
- **Counts against:** κ̂ ≤ 0 or inside the link time-shift null; κ_lead ≈ κ; κ vanishing with the momentum control; an effect only in returns.

## Result
*Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H28-links-spread-herding/G18/round1.json`).* 269 arrivals (168 first), 433 links to 30 universe projects, 63 arrivals within 60 min of a visible link. Tested.

| Test | Observed | Rule | Verdict |
| --- | --- | --- | --- |
| P1 κ (any visible link, last 60 min) | +0.28 ± 0.34 (e^κ 1.33); p 0.409; z_shift -6.1 (null +1.61 ± 0.22, n = 99) | κ > 0, z ≥ 2, p < 0.05 | failed |
| P2a lead placebo | κ_lead +3.76; κ − κ_lead -3.68 (one-sided p 1) | κ − κ_lead > 0, p < 0.05 | fail |
| P2b momentum control | κ +0.28 (p 0.407); momentum +0.76 | ≥ 50% of κ, p < 0.05 | fail |
| P3a naive agents | κ +0.12 ± 0.59 (p 0.839); first arrivals 168 | κ > 0 | fail |
| P3b pre-trend (O/E) | pre 10.46 (105 obs), post 4.56 (37 obs) | pre excess < ½ post excess | fail |
| P4 dose | d11 +0.74 (n_ev 30); d12 +0.20 (n_ev 4); d13 +1.20 (n_ev 1); dS2 -0.46 (n_ev 28); CV complex − simple +8.2 | 1-link HR > 1; S2 adds < 50% | fail |
| P5 λ (extra arrivals per exposure) | 0.012 [-0.010, 0.047]; N_exp 1322 | 0.01–0.15 | pass |
| P6 R_link | 0.06 [-0.05, 0.23]; R_all (links + occupancy) 0.32 | < 0.5 | pass |
| P10 occupancy J | J +1.41 (pd FE +0.18); without links +1.51 | J > 0 both; drop < 50% | pass |
| P7 counterfactual peak occupancy | f=0.5 ×0.99; f=0 ×0.94; cap ×0.98; burst f=0 ×0.94 | f=0: 0.70–0.90 (≥ 0.5) | fail |
| P7 calibration (unfitted) | observed peak 8 vs sim [6, 8]; burst 8 vs [6, 8] | inside 90% | pass |
| P8 latency (median excess lag) | 2 min; excess 0–15 +368.4, 15–60 -324.7, 60–240 -469.0 | post-NE09 < pre | – |

## Scorecard (period-specific axes)
- **C:** link time-shift null z -6.1; held-out (quarter-blocked) Δ log-lik primary − occupancy-only -11.5.
- **D:** simulated pile-on calibration inside the 90% interval.
- **H:** lead not beaten; momentum not survived.

## Notes
- *Post hoc robustness (coordinator request, 2026-10-04):* on the deterministic shared labels (`project_states.parquet`, 30 min, window switches) κ = +0.60 ± 0.45 (p 0.187; 57 switches), z_shift -16.2.
- *Post hoc short-lag check:* visible link in the last 15 min b = -0.05 ± 0.32 (z vs shift null +2.8); link arriving in the next 15 min b = +4.02 ± 0.34; lag − lead -4.07 (one-sided p 1). Action-only latency: median excess lag 2 min.
- Holdout days: none in this period's build (non-holdout days only).
