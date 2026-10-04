# H51 × G20: goal period #20

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #20 · regime I · active N 9.2 · units 20a, 20b, 20c, 20d.

## Why this period
A non-holdout goal period with the three phase-diagram axes (H67 g_lag, H86 c_×, H85 N) and at least one observable; one point of the replication layer.

## Prediction
*The card's per-period rule, written 2026-10-04 20:40 UTC before any collapse statistic; this folder was written after the run and copies it.* Supported if the period's D1 (g_lag) leave-one-period-out residual lies inside the 80% band (|z| ≤ 1.28) for ≥ 3/4 of its observables and the card-level collapse holds; failed if the card-level collapse does not hold and the period has ≥ 2 observables; descriptive if it has < 2 observables.

## Result
Card-level D1 collapse: **does not hold** (0/4 observables; within-regime permutation p = 0.073).

| Axis | Value |
| --- | --- |
| K = g_lag (H67 pool) | -0.020 ± 0.013 |
| equal-time dial g_eq | 0.148 |
| h = c_× trimmed (H86) | 0.0237 (φ 0.233) |
| kickoff S_text (H54) | -0.42 |
| N active (H85) | 9.2 |
| f_sched (H38) | 1.06 |

| Observable | Observed | D1 prediction (LOPO) | z | regime-only prediction |
| --- | --- | --- | --- | --- |
| settling time (log h) | 1.547 | 0.780 | 0.41 | 0.966 |
| herding share | 0.072 | 0.147 | -0.59 | 0.180 |
| idea branching (logit R) | -0.937 | -1.224 | 0.55 | -1.330 |
| loop rate (logit) | -1.671 | -1.675 | 0.00 | -1.735 |

Transformed scales: settling log active hours; herding share excess; branching and loop rate in logits. Data: `data/processed/H51-one-dial-collapse/results/phase_points.parquet`.

## Scorecard (period-specific axes)
D (unfitted observables placed against the dial), H (D1 vs regime-only prediction above).
