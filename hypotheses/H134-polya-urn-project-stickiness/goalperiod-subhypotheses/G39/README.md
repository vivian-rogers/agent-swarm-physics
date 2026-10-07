# H134 × G39: Build your own interactive world! (2026-04-27 → 05-01)

**Verdict:** failed
**Role:** exploratory (replication, native N2)
**Period:** regime III · mode I · 15 agents · #best/#rest · 5 days. One unit (39). Shared-goal code: own-role.

## Why this period
Replication layer: the common per-call leave hazard on every regime-III unit with ≥ 100 visits and ≥ 50 completed (card, Data scheme). Regime-I and II calls have no context segment, so f_proj is undefined there.

## Prediction
*Written 2026-10-07, before running H134 on this period. Structural counts (visits, completed visits, forced resets inside visits) were computed first; no outcome statistic.*
The card's replication predictions, applied to each testable unit of this period:
- P1: β_F > 0 with CI > 0 in model (b) (B + F + ln d + K). Counts against: CI includes 0.
- P2: β_F's CI contains 1 in model (b).
- P4 / Kill A: the observed dwell slope γ and the KM survival at d = 100 lie inside the 95% bands simulated from B + F (O3).
- O2 (ε(F)) and O5 (calibration curve) are reported; ε(F) is read only where G(A) > 0 with CI above 0.

Period-specific: own-role week in N2. Prediction N2: β_F here differs from the shared-goal weeks (G37, G38, G41) by < 0.3, CIs overlapping.

## Result
Run 2026-10-07 with `analysis/run.py` (agent-day block bootstrap, 200 draws; O3-pp 200 copies) and `analysis/summarize.py`. Numbers: `data/processed/H134-polya-urn-project-stickiness/results/<unit>.json`. Kill A fires in every unit: the fitted per-call rule without ln d does not reproduce the observed dwell aging.

| Unit | risk calls / leaves | β_F (b) [95% CI] | β_d (b) | γ observed | γ band (O3-pp) | KM(100) obs / band | G(A), ε(F) | Δ_reset ± SE (pred) | P1 / P2 / Kill A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 39 | 35,004 / 502 | +0.61 [-0.01, +1.25] | -0.73 [-0.78, -0.62] | -0.78 | [-0.27, -0.12] | 0.142 / [0.090, 0.213] | 10.7 [7.9, 14.1], -0.007 | +0.20 ± 0.48 (+0.091) | fail / pass / fires |

γ is the dwell hazard slope (logit h(d) = a + γ ln d). Δ_reset is the MH log OR of leaving at the first call after a forced reset (d ≥ 10) vs matched calls; "pred" is the urn's −β_F ln(1 − f_pre) with the unit's β_F.

N2 (own-role G39, G42 vs shared-goal G37, G38, G41): RE β_F own-role +0.54 [+0.06, +1.03], shared -0.30 [-0.50, -0.09]; difference +0.84 [+0.31, +1.37]. **N2 fails** (the slope depends on the goal type).

## Scorecard (period-specific axes)
- C adequacy: 0. Self-share adds no held-out information (G(F) ≈ 0 where readable).
- D unfitted predictions: 0. The dwell slope is outside the O3-pp band in every unit.
