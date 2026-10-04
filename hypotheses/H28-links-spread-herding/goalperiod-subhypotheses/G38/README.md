# H28 × G38: Choose a charity and raise as much money as you can (2026-04-02 → 2026-04-27)

**Verdict:** mixed (P1 weak)
**Role:** exploratory (candidate)
**Period:** regime III · mode C · 14 agents on the roster · 17 non-holdout days.

## Why this period
Named candidate; 17 days, two rooms with different instructions, ≈ 800 links. H11: positive βJ but the herding failed the local-shift null (z +1.2) — a test of whether links carry fast herding where H11 saw little.

## Prediction
*Written 2026-10-04, before running on this period.*

Card rules (P1–P10, Amendment 1) apply; tested only if ≥ 30 arrivals and ≥ 20 links to universe projects.

- **Here:** P1 supported (power from 17 days) but small κ (e^κ ≈ 1.5–2.5); R_link < 0.2; room placebo κ_other ≈ 0.
- **Counts against:** κ̂ ≤ 0 or inside the link time-shift null; κ_lead ≈ κ; κ vanishing with the momentum control; an effect only in returns.

## Result
*Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H28-links-spread-herding/G38/round1.json`).* 581 arrivals (148 first), 816 links to 30 universe projects, 116 arrivals within 60 min of a visible link. Tested.

| Test | Observed | Rule | Verdict |
| --- | --- | --- | --- |
| P1 κ (any visible link, last 60 min) | +0.72 ± 0.22 (e^κ 2.05); p 0.000841; z_shift -0.7 (null +0.81 ± 0.14, n = 99) | κ > 0, z ≥ 2, p < 0.05 | weak |
| P2a lead placebo | κ_lead +1.68; κ − κ_lead -1.40 (one-sided p 1) | κ − κ_lead > 0, p < 0.05 | fail |
| P2b momentum control | κ +0.73 (p 0.000571); momentum +0.44 | ≥ 50% of κ, p < 0.05 | pass |
| P2c other-room placebo | κ_same +0.48; κ_other -2.82 ± 0.57 (11448 exposed rows, 3 arrivals) | κ_other < κ_same, CI ∋ 0 | fail |
| P3a naive agents | κ +2.60 ± 0.33 (p 5.31e-15); first arrivals 148 | κ > 0 | pass |
| P3b pre-trend (O/E) | pre 8.20 (30 obs), post 8.18 (32 obs) | pre excess < ½ post excess | fail |
| P4 dose | d11 +0.72 (n_ev 50); d12 +0.59 (n_ev 11); d13 +0.95 (n_ev 17); dS2 +0.64 (n_ev 38); CV complex − simple -1.0 | 1-link HR > 1; S2 adds < 50% | pass |
| P5 λ (extra arrivals per exposure) | 0.025 [0.011, 0.046]; N_exp 2411 | 0.01–0.15 | pass |
| P6 R_link | 0.10 [0.04, 0.19]; R_all (links + occupancy) 0.13 | < 0.5 | pass |
| P10 occupancy J | J +0.06 (pd FE -1.06); without links +0.35 | J > 0 both; drop < 50% | fail |
| P7 counterfactual peak occupancy | f=0.5 ×0.94; f=0 ×0.94; cap ×0.99; burst f=0 ×0.94 | f=0: 0.70–0.90 (≥ 0.5) | fail |
| P7 calibration (unfitted) | observed peak 7 vs sim [2, 4]; burst 7 vs [1, 4] | inside 90% | fail |
| P8 latency (median excess lag) | 132 min; excess 0–15 +55.9, 15–60 -58.6, 60–240 -28.4 | post-NE09 < pre | – |

## Scorecard (period-specific axes)
- **C:** link time-shift null z -0.7; held-out (quarter-blocked) Δ log-lik primary − occupancy-only +168.1.
- **D:** simulated pile-on calibration outside the 90% interval.
- **H:** lead not beaten; momentum survived; other-room placebo not clean.

## Notes
- *Post hoc robustness (coordinator request, 2026-10-04):* on the deterministic shared labels (`project_states.parquet`, 30 min, window switches) κ = +1.33 ± 0.32 (p 2.82e-05; 111 switches), z_shift -0.6.
- *Post hoc short-lag check:* visible link in the last 15 min b = +0.27 ± 0.18 (z vs shift null +1.8); link arriving in the next 15 min b = +1.13 ± 0.17; lag − lead -0.85 (one-sided p 1). Action-only latency: median excess lag 128 min.
- Holdout days: none in this period's build (non-holdout days only).
