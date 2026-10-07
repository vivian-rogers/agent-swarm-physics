# H134 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 04-24)

**Verdict:** failed
**Role:** exploratory (replication, native N3, native N2)
**Period:** regime III · mode C · 12–14 agents · #best/#rest · 17 days. Units: 38a, 38b, 38e testable; 38c (59 visits) and 38d (76 visits) fail the precondition. Shared-goal code: shared.

## Why this period
Replication layer: the common per-call leave hazard on every regime-III unit with ≥ 100 visits and ≥ 50 completed (card, Data scheme). Regime-I and II calls have no context segment, so f_proj is undefined there.

## Prediction
*Written 2026-10-07, before running H134 on this period. Structural counts (visits, completed visits, forced resets inside visits) were computed first; no outcome statistic.*
The card's replication predictions, applied to each testable unit of this period:
- P1: β_F > 0 with CI > 0 in model (b) (B + F + ln d + K). Counts against: CI includes 0.
- P2: β_F's CI contains 1 in model (b).
- P4 / Kill A: the observed dwell slope γ and the KM survival at d = 100 lie inside the 95% bands simulated from B + F (O3).
- O2 (ε(F)) and O5 (calibration curve) are reported; ε(F) is read only where G(A) > 0 with CI above 0.

Period-specific: G38 is the second NE41 period (`../NE41/`) and the N3 bridge to H129. N3 (descriptive): the simulated dwell slope γ from O3 lies between H129's work (−0.2 to −0.4) and attention (−0.5 to −1.6) values. G38 is a shared-goal week in N2.

## Result
Run 2026-10-07 with `analysis/run.py` (agent-day block bootstrap, 200 draws; O3-pp 200 copies) and `analysis/summarize.py`. Numbers: `data/processed/H134-polya-urn-project-stickiness/results/<unit>.json`. Kill A fires in every unit: the fitted per-call rule without ln d does not reproduce the observed dwell aging.

| Unit | risk calls / leaves | β_F (b) [95% CI] | β_d (b) | γ observed | γ band (O3-pp) | KM(100) obs / band | G(A), ε(F) | Δ_reset ± SE (pred) | P1 / P2 / Kill A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 38a | 45,617 / 1,744 | -0.19 [-0.35, +0.02] | -0.73 [-0.78, -0.65] | -0.80 | [-0.15, -0.04] | 0.070 / [0.014, 0.048] | 22.6 [16.6, 29.8], +0.048 | +0.21 ± 0.29 (-0.017) | fail / fail / fires |
| 38b | 13,138 / 189 | -0.16 [-0.76, +0.51] | -0.53 [-0.58, -0.36] | -0.69 | [-0.43, -0.17] | 0.218 / [0.096, 0.219] | 6.0 [5.1, 6.7], -0.050 | -0.53 ± 1.01 (-0.017) | fail / fail / fires |
| 38e | 15,218 / 190 | +0.09 [-0.53, +1.34] | -0.67 [-0.76, -0.49] | -0.92 | [-0.42, -0.23] | 0.198 / [0.068, 0.300] | 10.1 [1.8, 14.8], +0.027 | +1.22 ± 0.54 (+0.015) | fail / pass / fires |

γ is the dwell hazard slope (logit h(d) = a + γ ln d). Δ_reset is the MH log OR of leaving at the first call after a forced reset (d ≥ 10) vs matched calls; "pred" is the urn's −β_F ln(1 − f_pre) with the unit's β_F.

N3 (descriptive): the fitted per-call rule's dwell slope (O3-pp band) is −0.04 to −0.43 in G38; the card's forward design gives −0.29 to −0.62. Both lie near H129's work range (−0.2 to −0.4), not its attention range (−0.5 to −1.6). The observed γ (−0.69 to −0.92) sits in H129's attention range.
N2 (own-role G39, G42 vs shared-goal G37, G38, G41): RE β_F own-role +0.54 [+0.06, +1.03], shared -0.30 [-0.50, -0.09]; difference +0.84 [+0.31, +1.37]. **N2 fails** (the slope depends on the goal type).

## Scorecard (period-specific axes)
- C adequacy: 0. Self-share adds no held-out information (G(F) ≈ 0 where readable).
- D unfitted predictions: 0. The dwell slope is outside the O3-pp band in every unit.
