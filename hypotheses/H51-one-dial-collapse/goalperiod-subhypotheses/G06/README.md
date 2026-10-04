# H51 × G06: goal period #6

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #6 · regime I · active N 4.0 · units 6a, 6b.

## Why this period
A non-holdout goal period with the three phase-diagram axes (H67 g_lag, H86 c_×, H85 N) and at least one observable; one point of the replication layer.

## Prediction
*The card's per-period rule, written 2026-10-04 20:40 UTC before any collapse statistic; this folder was written after the run and copies it.* Supported if the period's D1 (g_lag) leave-one-period-out residual lies inside the 80% band (|z| ≤ 1.28) for ≥ 3/4 of its observables and the card-level collapse holds; failed if the card-level collapse does not hold and the period has ≥ 2 observables; descriptive if it has < 2 observables.

## Result
Card-level D1 collapse: **does not hold** (0/4 observables; within-regime permutation p = 0.073).

| Axis | Value |
| --- | --- |
| K = g_lag (H67 pool) | -0.008 ± 0.015 |
| equal-time dial g_eq | 0.158 |
| h = c_× trimmed (H86) | 0.4375 (φ 0.327) |
| kickoff S_text (H54) | -0.29 |
| N active (H85) | 4.0 |
| f_sched (H38) | 0.74 |

| Observable | Observed | D1 prediction (LOPO) | z | regime-only prediction |
| --- | --- | --- | --- | --- |
| settling time (log h) | 2.264 | 0.810 | 0.78 | 0.928 |
| herding share | – | – | – | – |
| idea branching (logit R) | -2.073 | -1.178 | -1.72 | -1.270 |
| loop rate (logit) | -2.006 | -1.772 | -0.22 | -1.719 |

Transformed scales: settling log active hours; herding share excess; branching and loop rate in logits. Data: `data/processed/H51-one-dial-collapse/results/phase_points.parquet`.

## Scorecard (period-specific axes)
D (unfitted observables placed against the dial), H (D1 vs regime-only prediction above).
