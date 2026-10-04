# H51 × G03: goal period #3

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #3 · regime I · active N 4.0 · units 3.

## Why this period
A non-holdout goal period with the three phase-diagram axes (H67 g_lag, H86 c_×, H85 N) and at least one observable; one point of the replication layer.

## Prediction
*The card's per-period rule, written 2026-10-04 20:40 UTC before any collapse statistic; this folder was written after the run and copies it.* Supported if the period's D1 (g_lag) leave-one-period-out residual lies inside the 80% band (|z| ≤ 1.28) for ≥ 3/4 of its observables and the card-level collapse holds; failed if the card-level collapse does not hold and the period has ≥ 2 observables; descriptive if it has < 2 observables.

## Result
Card-level D1 collapse: **does not hold** (0/4 observables; within-regime permutation p = 0.073).

| Axis | Value |
| --- | --- |
| K = g_lag (H67 pool) | 0.017 ± 0.054 |
| equal-time dial g_eq | 0.353 |
| h = c_× trimmed (H86) | 0.1372 (φ 0.507) |
| kickoff S_text (H54) | -0.57 |
| N active (H85) | 4.0 |
| f_sched (H38) | -1.85 |

| Observable | Observed | D1 prediction (LOPO) | z | regime-only prediction |
| --- | --- | --- | --- | --- |
| settling time (log h) | – | – | – | – |
| herding share | – | – | – | – |
| idea branching (logit R) | – | – | – | – |
| loop rate (logit) | -1.059 | -2.031 | 0.90 | -1.764 |

Transformed scales: settling log active hours; herding share excess; branching and loop rate in logits. Data: `data/processed/H51-one-dial-collapse/results/phase_points.parquet`.

## Scorecard (period-specific axes)
D (unfitted observables placed against the dial), H (D1 vs regime-only prediction above).
