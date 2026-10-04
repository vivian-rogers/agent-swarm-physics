# H51 × G38: goal period #38

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #38 · regime III · active N 12.4 · units 38a, 38b, 38c, 38d, 38e.

## Why this period
A non-holdout goal period with the three phase-diagram axes (H67 g_lag, H86 c_×, H85 N) and at least one observable; one point of the replication layer.

## Prediction
*The card's per-period rule, written 2026-10-04 20:40 UTC before any collapse statistic; this folder was written after the run and copies it.* Supported if the period's D1 (g_lag) leave-one-period-out residual lies inside the 80% band (|z| ≤ 1.28) for ≥ 3/4 of its observables and the card-level collapse holds; failed if the card-level collapse does not hold and the period has ≥ 2 observables; descriptive if it has < 2 observables.

## Result
Card-level D1 collapse: **does not hold** (0/4 observables; within-regime permutation p = 0.073).

| Axis | Value |
| --- | --- |
| K = g_lag (H67 pool) | 0.066 ± 0.013 |
| equal-time dial g_eq | 0.108 |
| h = c_× trimmed (H86) | 0.0019 (φ 0.019) |
| kickoff S_text (H54) | 0.05 |
| N active (H85) | 12.4 |
| f_sched (H38) | 0.89 |

| Observable | Observed | D1 prediction (LOPO) | z | regime-only prediction |
| --- | --- | --- | --- | --- |
| settling time (log h) | -1.386 | 1.374 | -1.48 | 2.308 |
| herding share | 0.012 | 0.114 | -0.79 | 0.035 |
| idea branching (logit R) | -1.027 | -1.331 | 0.59 | -1.486 |
| loop rate (logit) | -1.379 | -2.455 | 1.00 | -3.240 |

Transformed scales: settling log active hours; herding share excess; branching and loop rate in logits. Data: `data/processed/H51-one-dial-collapse/results/phase_points.parquet`.

## Scorecard (period-specific axes)
D (unfitted observables placed against the dial), H (D1 vs regime-only prediction above).
