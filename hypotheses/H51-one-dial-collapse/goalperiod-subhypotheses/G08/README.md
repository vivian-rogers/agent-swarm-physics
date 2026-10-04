# H51 × G08: goal period #8

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #8 · regime I · active N 4.0 · units 8.

## Why this period
A non-holdout goal period with the three phase-diagram axes (H67 g_lag, H86 c_×, H85 N) and at least one observable; one point of the replication layer.

## Prediction
*The card's per-period rule, written 2026-10-04 20:40 UTC before any collapse statistic; this folder was written after the run and copies it.* Supported if the period's D1 (g_lag) leave-one-period-out residual lies inside the 80% band (|z| ≤ 1.28) for ≥ 3/4 of its observables and the card-level collapse holds; failed if the card-level collapse does not hold and the period has ≥ 2 observables; descriptive if it has < 2 observables.

## Result
Card-level D1 collapse: **does not hold** (0/4 observables; within-regime permutation p = 0.073).

| Axis | Value |
| --- | --- |
| K = g_lag (H67 pool) | 0.005 ± 0.011 |
| equal-time dial g_eq | -0.014 |
| h = c_× trimmed (H86) | 0.0171 (φ 0.185) |
| kickoff S_text (H54) | -0.14 |
| N active (H85) | 4.0 |
| f_sched (H38) | 0.11 |

| Observable | Observed | D1 prediction (LOPO) | z | regime-only prediction |
| --- | --- | --- | --- | --- |
| settling time (log h) | -1.075 | 1.054 | -1.14 | 1.104 |
| herding share | 0.282 | 0.125 | 1.23 | 0.167 |
| idea branching (logit R) | -1.898 | -1.209 | -1.32 | -1.279 |
| loop rate (logit) | -2.346 | -1.869 | -0.44 | -1.703 |

Transformed scales: settling log active hours; herding share excess; branching and loop rate in logits. Data: `data/processed/H51-one-dial-collapse/results/phase_points.parquet`.

## Scorecard (period-specific axes)
D (unfitted observables placed against the dial), H (D1 vs regime-only prediction above).
