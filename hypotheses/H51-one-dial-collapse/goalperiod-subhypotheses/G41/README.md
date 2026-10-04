# H51 × G41: goal period #41

**Verdict:** failed
**Role:** replication (exploratory); native test in [NE42](../NE42/README.md)
**Period:** goal #41 · regime III · active N 15.0 · units 41.

## Why this period
A non-holdout goal period with the three phase-diagram axes (H67 g_lag, H86 c_×, H85 N) and at least one observable; one point of the replication layer.

## Prediction
*The card's per-period rule, written 2026-10-04 20:40 UTC before any collapse statistic; this folder was written after the run and copies it.* Supported if the period's D1 (g_lag) leave-one-period-out residual lies inside the 80% band (|z| ≤ 1.28) for ≥ 3/4 of its observables and the card-level collapse holds; failed if the card-level collapse does not hold and the period has ≥ 2 observables; descriptive if it has < 2 observables.

## Result
Card-level D1 collapse: **does not hold** (0/4 observables; within-regime permutation p = 0.073).

| Axis | Value |
| --- | --- |
| K = g_lag (H67 pool) | 0.189 ± 0.049 |
| equal-time dial g_eq | 0.162 |
| h = c_× trimmed (H86) | 0.0785 (φ 0.311) |
| kickoff S_text (H54) | 0.04 |
| N active (H85) | 15.0 |
| f_sched (H38) | 0.66 |

| Observable | Observed | D1 prediction (LOPO) | z | regime-only prediction |
| --- | --- | --- | --- | --- |
| settling time (log h) | 1.943 | 1.775 | 0.09 | 1.642 |
| herding share | 0.028 | 0.070 | -0.32 | 0.033 |
| idea branching (logit R) | -1.137 | -1.549 | 0.79 | -1.471 |
| loop rate (logit) | -2.617 | -3.661 | 0.97 | -3.063 |

Transformed scales: settling log active hours; herding share excess; branching and loop rate in logits. Data: `data/processed/H51-one-dial-collapse/results/phase_points.parquet`.

## Scorecard (period-specific axes)
D (unfitted observables placed against the dial), H (D1 vs regime-only prediction above).
