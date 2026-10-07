# H134 × G44: Finetune your leader! (2026-05-26 → 05-29)

**Verdict:** failed
**Role:** exploratory (replication)
**Period:** regime III · mode C · 17–18 agents · #best/#rest · 4 days. Units: 44a, 44b. Shared-goal code: shared.

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
| 44a | 10,956 / 731 | +0.44 [-0.31, +1.18] | -0.26 [-0.37, -0.12] | -0.47 | [-0.35, -0.22] | 0.018 / [0.003, 0.012] | 3.1 [2.2, 4.1], -0.047 | +2.14 ± 0.58 (+0.053) | fail / pass / fires |
| 44b | 12,240 / 691 | -0.12 [-0.62, +0.51] | -0.49 [-0.59, -0.35] | -0.71 | [-0.42, -0.31] | 0.033 / [0.003, 0.018] | 10.9 [9.9, 11.9], -0.004 | +0.67 ± 0.44 (-0.016) | fail / fail / fires |

γ is the dwell hazard slope (logit h(d) = a + γ ln d). Δ_reset is the MH log OR of leaving at the first call after a forced reset (d ≥ 10) vs matched calls; "pred" is the urn's −β_F ln(1 − f_pre) with the unit's β_F.


## Scorecard (period-specific axes)
- C adequacy: 0. Self-share adds no held-out information (G(F) ≈ 0 where readable).
- D unfitted predictions: 0. The dwell slope is outside the O3-pp band in every unit.
