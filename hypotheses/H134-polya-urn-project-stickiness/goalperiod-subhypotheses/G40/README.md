# H134 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 05-08)

**Verdict:** mixed
**Role:** exploratory (replication)
**Period:** regime III · mode C · 15 agents · #universe-coordination (NE42 merge) · 5 days. One unit (40). Shared-goal code: shared.

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
Run 2026-10-07 with `analysis/run.py` (agent-day block bootstrap, 200 draws; O3-pp 200 copies) and `analysis/summarize.py`. Numbers: `data/processed/H134-polya-urn-project-stickiness/results/<unit>.json`. The urn slope fits (β_F +1.26, CI ∋ 1), but Kill A fires: the rule does not reproduce the dwell aging.

| Unit | risk calls / leaves | β_F (b) [95% CI] | β_d (b) | γ observed | γ band (O3-pp) | KM(100) obs / band | G(A), ε(F) | Δ_reset ± SE (pred) | P1 / P2 / Kill A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 40 | 39,073 / 450 | +1.26 [+0.70, +2.09] | -0.82 [-0.88, -0.70] | -0.90 | [-0.30, -0.13] | 0.157 / [0.094, 0.292] | 15.2 [8.0, 26.0], +0.029 | +0.14 ± 0.53 (+0.371) | pass / pass / fires |

γ is the dwell hazard slope (logit h(d) = a + γ ln d). Δ_reset is the MH log OR of leaving at the first call after a forced reset (d ≥ 10) vs matched calls; "pred" is the urn's −β_F ln(1 − f_pre) with the unit's β_F.


## Scorecard (period-specific axes)
- C adequacy: 0. Self-share adds no held-out information (G(F) ≈ 0 where readable).
- D unfitted predictions: 0. The dwell slope is outside the O3-pp band in every unit.
