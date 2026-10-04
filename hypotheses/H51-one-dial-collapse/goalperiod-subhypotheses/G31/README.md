# H51 × G31: goal period #31

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #31 · regime I · active N 11.2 · units 31a, 31b, 31c, 31d.

## Why this period
A non-holdout goal period with the three phase-diagram axes (H67 g_lag, H86 c_×, H85 N) and at least one observable; one point of the replication layer.

## Prediction
*The card's per-period rule, written 2026-10-04 20:40 UTC before any collapse statistic; this folder was written after the run and copies it.* Supported if the period's D1 (g_lag) leave-one-period-out residual lies inside the 80% band (|z| ≤ 1.28) for ≥ 3/4 of its observables and the card-level collapse holds; failed if the card-level collapse does not hold and the period has ≥ 2 observables; descriptive if it has < 2 observables.

## Result
Card-level D1 collapse: **does not hold** (0/4 observables; within-regime permutation p = 0.073).

| Axis | Value |
| --- | --- |
| K = g_lag (H67 pool) | -0.035 ± 0.030 |
| equal-time dial g_eq | 0.050 |
| h = c_× trimmed (H86) | 0.0009 (φ 0.015) |
| kickoff S_text (H54) | 1.25 |
| N active (H85) | 11.2 |
| f_sched (H38) | -0.16 |

| Observable | Observed | D1 prediction (LOPO) | z | regime-only prediction |
| --- | --- | --- | --- | --- |
| settling time (log h) | 1.726 | 0.667 | 0.57 | 0.956 |
| herding share | 0.073 | 0.154 | -0.63 | 0.180 |
| idea branching (logit R) | -0.864 | -1.213 | 0.67 | -1.334 |
| loop rate (logit) | -2.835 | -1.450 | -1.28 | -1.680 |

Transformed scales: settling log active hours; herding share excess; branching and loop rate in logits. Data: `data/processed/H51-one-dial-collapse/results/phase_points.parquet`.

## Scorecard (period-specific axes)
D (unfitted observables placed against the dial), H (D1 vs regime-only prediction above).
