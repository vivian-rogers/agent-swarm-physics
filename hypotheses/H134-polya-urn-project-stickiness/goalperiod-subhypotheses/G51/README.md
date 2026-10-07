# H134 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 09-04 (non-reserved; the tail from 09-07 is reserved))

**Verdict:** failed
**Role:** exploratory (replication)
**Period:** regime III · mode P · 21–32 agents · #general (+#focus in 51g) · 45 days. Units 51a–51l, all testable. Shared-goal code: own-role.

## Why this period
Replication layer: the common per-call leave hazard on every regime-III unit with ≥ 100 visits and ≥ 50 completed (card, Data scheme). Regime-I and II calls have no context segment, so f_proj is undefined there.

## Prediction
*Written 2026-10-07, before running H134 on this period. Structural counts (visits, completed visits, forced resets inside visits) were computed first; no outcome statistic.*
The card's replication predictions, applied to each testable unit of this period:
- P1: β_F > 0 with CI > 0 in model (b) (B + F + ln d + K). Counts against: CI includes 0.
- P2: β_F's CI contains 1 in model (b).
- P4 / Kill A: the observed dwell slope γ and the KM survival at d = 100 lie inside the 95% bands simulated from B + F (O3).
- O2 (ε(F)) and O5 (calibration curve) are reported; ε(F) is read only where G(A) > 0 with CI above 0.

Period-specific (natives and G51-only predictions):
- P3: ε(F) summed over the G51 units lies above the proxy band from the synthetic W2, W3 and W4 worlds. Kill B fires if it lies inside.
- P5: β_d < 0 with CI < 0 in model (b) (random-effects mean over the G51 units).
- N2: G51 is an own-role period; it enters the own-role vs shared-goal contrast only through the regime-III cross-check, not the pre-registered N2 set (G39, G42 vs G37, G38, G41).
- The reset native N1 for G51 is in `../NE41/`.

## Result
Run 2026-10-07 with `analysis/run.py` (agent-day block bootstrap, 200 draws; O3-pp 200 copies) and `analysis/summarize.py`. Numbers: `data/processed/H134-polya-urn-project-stickiness/results/<unit>.json`. Kill A fires in every unit: the fitted per-call rule without ln d does not reproduce the observed dwell aging.

| Unit | risk calls / leaves | β_F (b) [95% CI] | β_d (b) | γ observed | γ band (O3-pp) | KM(100) obs / band | G(A), ε(F) | Δ_reset ± SE (pred) | P1 / P2 / Kill A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | 51,317 / 2,712 | +0.35 [+0.21, +0.73] | -0.67 [-0.75, -0.52] | -0.85 | [-0.35, -0.25] | 0.049 / [0.003, 0.021] | 26.6 [12.6, 46.9], +0.001 | +0.14 ± 0.28 (+0.046) | pass / fail / fires |
| 51b | 14,102 / 637 | -0.16 [-0.53, +0.87] | -0.58 [-0.77, -0.42] | -0.97 | [-0.71, -0.58] | 0.063 / [0.022, 0.046] | n/a (≤ 3 days) | +0.98 ± 0.43 (-0.020) | fail / fail / fires |
| 51c | 79,100 / 6,073 | +0.43 [+0.08, +0.73] | -0.66 [-0.70, -0.57] | -1.06 | [-0.69, -0.54] | 0.032 / [0.003, 0.012] | 15.7 [10.8, 22.2], -0.018 | +0.29 ± 0.23 (+0.050) | pass / fail / fires |
| 51d | 79,848 / 4,594 | +0.25 [-0.07, +0.52] | -0.59 [-0.64, -0.49] | -1.03 | [-0.72, -0.61] | 0.043 / [0.013, 0.026] | 8.6 [6.2, 11.1], -0.011 | +0.13 ± 0.26 (+0.028) | fail / fail / fires |
| 51e | 57,303 / 3,456 | +0.10 [-0.19, +0.41] | -0.50 [-0.55, -0.41] | -0.85 | [-0.56, -0.48] | 0.029 / [0.006, 0.015] | 8.6 [8.5, 8.7], +0.004 | +0.42 ± 0.23 (+0.010) | fail / fail / fires |
| 51f | 78,466 / 5,102 | +0.14 [-0.08, +0.36] | -0.62 [-0.67, -0.52] | -0.96 | [-0.57, -0.49] | 0.034 / [0.004, 0.014] | 13.2 [9.7, 17.5], +0.004 | +0.35 ± 0.23 (+0.014) | fail / fail / fires |
| 51g | 187,795 / 14,207 | +0.08 [-0.04, +0.22] | -0.62 [-0.64, -0.57] | -1.00 | [-0.63, -0.52] | 0.029 / [0.004, 0.010] | 11.8 [9.0, 15.0], -0.003 | +0.17 ± 0.15 (+0.007) | fail / fail / fires |
| 51h | 60,687 / 5,128 | -0.21 [-0.44, +0.03] | -0.60 [-0.68, -0.48] | -0.99 | [-0.63, -0.40] | 0.023 / [0.003, 0.008] | 18.1 [12.0, 26.3], +0.038 | +0.55 ± 0.23 (-0.019) | fail / fail / fires |
| 51i | 29,343 / 1,895 | +0.18 [-0.11, +0.42] | -0.56 [-0.62, -0.47] | -1.03 | [-0.78, -0.68] | 0.031 / [0.005, 0.015] | 9.6 [9.5, 9.6], -0.010 | +0.69 ± 0.35 (+0.019) | fail / fail / fires |
| 51j | 32,149 / 1,996 | +0.11 [-0.18, +0.36] | -0.49 [-0.60, -0.33] | -1.03 | [-0.81, -0.73] | 0.033 / [0.008, 0.017] | 7.6 [5.9, 9.2], +0.004 | +1.15 ± 0.32 (+0.011) | fail / fail / fires |
| 51k | 14,381 / 850 | -0.07 [-0.39, +0.39] | -0.49 [-0.61, -0.28] | -0.95 | [-0.75, -0.64] | 0.034 / [0.008, 0.021] | n/a (≤ 3 days) | +0.95 ± 0.47 (-0.005) | fail / fail / fires |
| 51l | 15,819 / 1,040 | +0.21 [-0.20, +0.44] | -0.48 [-0.59, -0.30] | -0.91 | [-0.69, -0.59] | 0.033 / [0.009, 0.020] | n/a (≤ 3 days) | +0.79 ± 0.51 (+0.019) | fail / fail / fires |

γ is the dwell hazard slope (logit h(d) = a + γ ln d). Δ_reset is the MH log OR of leaving at the first call after a forced reset (d ≥ 10) vs matched calls; "pred" is the urn's −β_F ln(1 − f_pre) with the unit's β_F.

G51 period-level:
- β_F random-effects mean over 12 units: +0.13 [+0.03, +0.23] (excludes 1).
- P5 (aging left over): β_d RE mean -0.58 [-0.62, -0.55]; CI < 0 in 12/12 units. **Holds.**
- P3 (untestable by A7, reported): ε(F) over the G51 units +0.001 [-0.005, +0.008], with G(A) 13.2 [+11.0, +15.8] nats per 1,000 risk calls. It lies inside the proxy band (0.055): self-share absorbs none of the dwell clock's held-out information.
- Kick term (A4): named reads about another project raise leaving, K +0.58 to +1.22 with CI > 0 in 6/12 units (51a, 51d–51h).
- Reset native: see `../NE41/`.

## Scorecard (period-specific axes)
- C adequacy: 0. Self-share adds no held-out information (G(F) ≈ 0 where readable).
- D unfitted predictions: 0. The dwell slope is outside the O3-pp band in every unit.
