# H134 × G42: Run your own Youtube channel! (2026-05-18 → 05-22)

**Verdict:** failed
**Role:** exploratory (replication, native N2)
**Period:** regime III · mode I · 15–16 agents · #best/#rest · 5 days. Units: 42a, 42b (roster join). Shared-goal code: own-role.

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
| 42a | 12,718 / 141 | +0.57 [-0.61, +1.43] | -0.45 [-0.53, -0.15] | -0.69 | [-0.48, -0.26] | 0.247 / [0.106, 0.360] | 4.4 [3.6, 5.1], +0.000 | n/a | fail / pass / fires |
| 42b | 17,050 / 183 | +0.31 [-0.49, +1.79] | -0.71 [-0.77, -0.54] | -0.88 | [-0.41, -0.22] | 0.240 / [0.121, 0.388] | 9.9 [7.7, 13.4], +0.073 | n/a | fail / pass / fires |

γ is the dwell hazard slope (logit h(d) = a + γ ln d). Δ_reset is the MH log OR of leaving at the first call after a forced reset (d ≥ 10) vs matched calls; "pred" is the urn's −β_F ln(1 − f_pre) with the unit's β_F.

N2 (own-role G39, G42 vs shared-goal G37, G38, G41): RE β_F own-role +0.54 [+0.06, +1.03], shared -0.30 [-0.50, -0.09]; difference +0.84 [+0.31, +1.37]. **N2 fails** (the slope depends on the goal type).

## Scorecard (period-specific axes)
- C adequacy: 0. Self-share adds no held-out information (G(F) ≈ 0 where readable).
- D unfitted predictions: 0. The dwell slope is outside the O3-pp band in every unit.
