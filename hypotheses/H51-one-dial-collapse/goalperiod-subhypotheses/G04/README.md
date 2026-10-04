# H51 × G04: goal period #4

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #4 · regime I · active N 4.0 · units 4a, 4b, 4c, 4d.

## Why this period
A non-holdout goal period with the three phase-diagram axes (H67 g_lag, H86 c_×, H85 N) and at least one observable; one point of the replication layer.

## Prediction
*The card's per-period rule, written 2026-10-04 20:40 UTC before any collapse statistic; this folder was written after the run and copies it.* Supported if the period's D1 (g_lag) leave-one-period-out residual lies inside the 80% band (|z| ≤ 1.28) for ≥ 3/4 of its observables and the card-level collapse holds; failed if the card-level collapse does not hold and the period has ≥ 2 observables; descriptive if it has < 2 observables.

## Result
Card-level D1 collapse: **does not hold** (0/4 observables; within-regime permutation p = 0.073).

| Axis | Value |
| --- | --- |
| K = g_lag (H67 pool) | 0.011 ± 0.018 |
| equal-time dial g_eq | 0.268 |
| h = c_× trimmed (H86) | 0.0081 (φ 0.048) |
| kickoff S_text (H54) | 0.69 |
| N active (H85) | 4.0 |
| f_sched (H38) | 0.11 |

| Observable | Observed | D1 prediction (LOPO) | z | regime-only prediction |
| --- | --- | --- | --- | --- |
| settling time (log h) | 0.530 | 1.005 | -0.25 | 1.019 |
| herding share | 0.236 | 0.125 | 0.86 | 0.170 |
| idea branching (logit R) | – | – | – | – |
| loop rate (logit) | -1.552 | -1.963 | 0.38 | -1.741 |

Transformed scales: settling log active hours; herding share excess; branching and loop rate in logits. Data: `data/processed/H51-one-dial-collapse/results/phase_points.parquet`.

## Scorecard (period-specific axes)
D (unfitted observables placed against the dial), H (D1 vs regime-only prediction above).
