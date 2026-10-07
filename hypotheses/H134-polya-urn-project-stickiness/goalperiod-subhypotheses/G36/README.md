# H134 × G36: Interact with other AI agents outside the Village! (2026-03-24 → 03-27 (regime-III units 36b, 36c))

**Verdict:** failed
**Role:** exploratory (replication)
**Period:** regime III units only · mode C · 12 agents · #best/#rest · 4 days. Units: 36b, 36c (NE14/NE16 splits). Shared-goal code: shared.

## Why this period
Replication layer: the common per-call leave hazard on every regime-III unit with ≥ 100 visits and ≥ 50 completed (card, Data scheme). Regime-I and II calls have no context segment, so f_proj is undefined there.

## Prediction
*Written 2026-10-07, before running H134 on this period. Structural counts (visits, completed visits, forced resets inside visits) were computed first; no outcome statistic.*
The card's replication predictions, applied to each testable unit of this period:
- P1: β_F > 0 with CI > 0 in model (b) (B + F + ln d + K). Counts against: CI includes 0.
- P2: β_F's CI contains 1 in model (b).
- P4 / Kill A: the observed dwell slope γ and the KM survival at d = 100 lie inside the 95% bands simulated from B + F (O3).
- O2 (ε(F)) and O5 (calibration curve) are reported; ε(F) is read only where G(A) > 0 with CI above 0.


## Result
Run 2026-10-07 with `analysis/run.py` (agent-day block bootstrap, 200 draws; O3-pp 200 copies) and `analysis/summarize.py`. Numbers: `data/processed/H134-polya-urn-project-stickiness/results/<unit>.json`. Kill A fires in every unit: the fitted per-call rule without ln d does not reproduce the observed dwell aging.

| Unit | risk calls / leaves | β_F (b) [95% CI] | β_d (b) | γ observed | γ band (O3-pp) | KM(100) obs / band | G(A), ε(F) | Δ_reset ± SE (pred) | P1 / P2 / Kill A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 36b | 12,699 / 960 | +0.20 [-0.31, +0.47] | -0.59 [-0.66, -0.48] | -0.72 | [-0.33, -0.17] | 0.023 / [0.001, 0.006] | 23.0 [22.7, 23.4], -0.008 | +0.24 ± 0.44 (+0.030) | fail / fail / fires |
| 36c | 13,402 / 1,336 | -0.26 [-0.39, +0.01] | -0.59 [-0.66, -0.45] | -0.72 | [-0.29, -0.20] | 0.013 / [0.000, 0.001] | 28.1 [25.2, 31.0], +0.080 | +0.25 ± 0.40 (-0.027) | fail / fail / fires |

γ is the dwell hazard slope (logit h(d) = a + γ ln d). Δ_reset is the MH log OR of leaving at the first call after a forced reset (d ≥ 10) vs matched calls; "pred" is the urn's −β_F ln(1 − f_pre) with the unit's β_F.


## Scorecard (period-specific axes)
- C adequacy: 0. Self-share adds no held-out information (G(F) ≈ 0 where readable).
- D unfitted predictions: 0. The dwell slope is outside the O3-pp band in every unit.
