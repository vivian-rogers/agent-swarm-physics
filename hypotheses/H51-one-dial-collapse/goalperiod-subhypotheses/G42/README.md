# H51 × G42: goal period #42

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #42 · regime III · active N 15.6 · units 42a, 42b.

## Why this period
A non-holdout goal period with the three phase-diagram axes (H67 g_lag, H86 c_×, H85 N) and at least one observable; one point of the replication layer.

## Prediction
*The card's per-period rule, written 2026-10-04 20:40 UTC before any collapse statistic; this folder was written after the run and copies it.* Supported if the period's D1 (g_lag) leave-one-period-out residual lies inside the 80% band (|z| ≤ 1.28) for ≥ 3/4 of its observables and the card-level collapse holds; failed if the card-level collapse does not hold and the period has ≥ 2 observables; descriptive if it has < 2 observables.

## Result
Card-level D1 collapse: **does not hold** (0/4 observables; within-regime permutation p = 0.073).

| Axis | Value |
| --- | --- |
| K = g_lag (H67 pool) | 0.154 ± 0.048 |
| equal-time dial g_eq | 0.091 |
| h = c_× trimmed (H86) | 0.0025 (φ 0.034) |
| kickoff S_text (H54) | -0.33 |
| N active (H85) | 15.6 |
| f_sched (H38) | 0.87 |

| Observable | Observed | D1 prediction (LOPO) | z | regime-only prediction |
| --- | --- | --- | --- | --- |
| settling time (log h) | 1.607 | 1.673 | -0.04 | 1.709 |
| herding share | 0.008 | 0.085 | -0.59 | 0.036 |
| idea branching (logit R) | -1.864 | -1.388 | -0.92 | -1.367 |
| loop rate (logit) | -3.907 | -3.105 | -0.74 | -2.878 |

Transformed scales: settling log active hours; herding share excess; branching and loop rate in logits. Data: `data/processed/H51-one-dial-collapse/results/phase_points.parquet`.

## Scorecard (period-specific axes)
D (unfitted observables placed against the dial), H (D1 vs regime-only prediction above).
