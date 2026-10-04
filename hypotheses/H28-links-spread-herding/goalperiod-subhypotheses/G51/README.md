# H28 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-07 (non-holdout part; the tail to 09-21 is held out))

**Verdict:** supported (P1 supported)
**Role:** exploratory (candidate)
**Period:** regime III · mode I/K (private roles) · 32 agents on the roster · 45 non-holdout days.

## Why this period
Named candidate; 45 non-holdout days, 21–32 agents, ≈ 7,400 links: by far the most power. H22: a random-field system (private roles pin positions) with a weak positive room pull, so links should matter little relative to fields. #focus room from 2026-08-05 gives an other-room placebo.

## Prediction
*Written 2026-10-04, before running on this period.*

Card rules (P1–P10, Amendment 1) apply; tested only if ≥ 30 arrivals and ≥ 20 links to universe projects.

- **Here:** P1 supported on power but κ small (e^κ ≈ 1.3–2); R_link < 0.1; room placebo κ_other ≈ 0.
- **Counts against:** κ̂ ≤ 0 or inside the link time-shift null; κ_lead ≈ κ; κ vanishing with the momentum control; an effect only in returns.

## Result
*Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H28-links-spread-herding/G51/round1.json`).* 6870 arrivals (609 first), 7426 links to 30 universe projects, 2176 arrivals within 60 min of a visible link. Tested.

| Test | Observed | Rule | Verdict |
| --- | --- | --- | --- |
| P1 κ (any visible link, last 60 min) | +0.58 ± 0.05 (e^κ 1.78); p 3.19e-33; z_shift +4.8 (null +0.40 ± 0.04, n = 39) | κ > 0, z ≥ 2, p < 0.05 | supported |
| P2a lead placebo | κ_lead +0.76; κ − κ_lead -0.39 (one-sided p 1) | κ − κ_lead > 0, p < 0.05 | fail |
| P2b momentum control | κ +0.57 (p 6.84e-33); momentum +0.48 | ≥ 50% of κ, p < 0.05 | pass |
| P2c other-room placebo | κ_same +0.58; κ_other -0.05 ± 0.20 (34310 exposed rows, 80 arrivals) | κ_other < κ_same, CI ∋ 0 | pass |
| P3a naive agents | κ +1.05 ± 0.15 (p 1.56e-12); first arrivals 609 | κ > 0 | pass |
| P3b pre-trend (O/E) | pre 2.98 (71 obs), post 5.51 (133 obs) | pre excess < ½ post excess | pass |
| P4 dose | d11 +0.54 (n_ev 867); d12 +0.61 (n_ev 386); d13 +0.51 (n_ev 582); dS2 +0.79 (n_ev 341); CV complex − simple -618.5 | 1-link HR > 1; S2 adds < 50% | pass |
| P5 λ (extra arrivals per exposure) | 0.006 [0.005, 0.007]; N_exp 155379 | 0.01–0.15 | fail |
| P6 R_link | 0.14 [0.12, 0.16]; R_all (links + occupancy) 0.27 | < 0.5 | pass |
| P10 occupancy J | J +0.25 (pd FE -0.62); without links +0.55 | J > 0 both; drop < 50% | fail |
| P7 counterfactual peak occupancy | f=0.5 ×0.88; f=0 ×0.73; cap ×0.84; burst f=0 ×0.80 | f=0: 0.70–0.90 (≥ 0.5) | pass |
| P7 calibration (unfitted) | observed peak 17 vs sim [4, 9]; burst 14 vs [4, 8] | inside 90% | fail |
| P8 latency (median excess lag) | 2 min; excess 0–15 +1411.8, 15–60 -22.2, 60–240 -559.3 | post-NE09 < pre | – |

## Scorecard (period-specific axes)
- **C:** link time-shift null z +4.8; held-out (quarter-blocked) Δ log-lik primary − occupancy-only -18.8.
- **D:** simulated pile-on calibration outside the 90% interval.
- **H:** lead not beaten; momentum survived; other-room placebo clean.

## Notes
- *Post hoc robustness (coordinator request, 2026-10-04):* on the deterministic shared labels (`project_states.parquet`, 30 min, window switches) κ = -0.13 ± 0.10 (p 0.178; 712 switches), z_shift +0.7.
- *Post hoc short-lag check:* visible link in the last 15 min b = +0.56 ± 0.05 (z vs shift null +10.8); link arriving in the next 15 min b = +0.80 ± 0.05; lag − lead -0.25 (one-sided p 1). Action-only latency: median excess lag 2 min.
- Holdout days: none in this period's build (non-holdout days only).
