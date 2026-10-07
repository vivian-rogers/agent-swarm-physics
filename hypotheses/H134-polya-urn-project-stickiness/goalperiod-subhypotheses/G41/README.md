# H134 × G41: Perform novel research! (2026-05-11 → 05-15)

**Verdict:** failed
**Role:** exploratory (replication, native N2)
**Period:** regime III · mode I · 15 agents · #best/#rest · 5 days. One unit (41). Shared-goal code: shared.

## Why this period
Replication layer: the common per-call leave hazard on every regime-III unit with ≥ 100 visits and ≥ 50 completed (card, Data scheme). Regime-I and II calls have no context segment, so f_proj is undefined there.

## Prediction
*Written 2026-10-07, before running H134 on this period. Structural counts (visits, completed visits, forced resets inside visits) were computed first; no outcome statistic.*
The card's replication predictions, applied to each testable unit of this period:
- P1: β_F > 0 with CI > 0 in model (b) (B + F + ln d + K). Counts against: CI includes 0.
- P2: β_F's CI contains 1 in model (b).
- P4 / Kill A: the observed dwell slope γ and the KM survival at d = 100 lie inside the 95% bands simulated from B + F (O3).
- O2 (ε(F)) and O5 (calibration curve) are reported; ε(F) is read only where G(A) > 0 with CI above 0.

Period-specific: shared-goal week in N2 (see G39, G42).

## Result
Run 2026-10-07 with `analysis/run.py` (agent-day block bootstrap, 200 draws; O3-pp 200 copies) and `analysis/summarize.py`. Numbers: `data/processed/H134-polya-urn-project-stickiness/results/<unit>.json`. Kill A fires in every unit: the fitted per-call rule without ln d does not reproduce the observed dwell aging.

| Unit | risk calls / leaves | β_F (b) [95% CI] | β_d (b) | γ observed | γ band (O3-pp) | KM(100) obs / band | G(A), ε(F) | Δ_reset ± SE (pred) | P1 / P2 / Kill A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 41 | 33,340 / 1,096 | -0.35 [-0.63, +0.19] | -0.83 [-0.89, -0.72] | -0.99 | [-0.24, -0.13] | 0.049 / [0.009, 0.088] | 38.8 [21.7, 54.0], -0.011 | +0.07 ± 0.54 (-0.062) | fail / fail / fires |

γ is the dwell hazard slope (logit h(d) = a + γ ln d). Δ_reset is the MH log OR of leaving at the first call after a forced reset (d ≥ 10) vs matched calls; "pred" is the urn's −β_F ln(1 − f_pre) with the unit's β_F.

N2 (own-role G39, G42 vs shared-goal G37, G38, G41): RE β_F own-role +0.54 [+0.06, +1.03], shared -0.30 [-0.50, -0.09]; difference +0.84 [+0.31, +1.37]. **N2 fails** (the slope depends on the goal type).

## Scorecard (period-specific axes)
- C adequacy: 0. Self-share adds no held-out information (G(F) ≈ 0 where readable).
- D unfitted predictions: 0. The dwell slope is outside the O3-pp band in every unit.
