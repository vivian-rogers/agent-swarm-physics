# H51 × G21: goal period #21

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #21 · regime I · active N 8.4 · units 21a, 21b.

## Why this period
A non-holdout goal period with the three phase-diagram axes (H67 g_lag, H86 c_×, H85 N) and at least one observable; one point of the replication layer.

## Prediction
*The card's per-period rule, written 2026-10-04 20:40 UTC before any collapse statistic; this folder was written after the run and copies it.* Supported if the period's D1 (g_lag) leave-one-period-out residual lies inside the 80% band (|z| ≤ 1.28) for ≥ 3/4 of its observables and the card-level collapse holds; failed if the card-level collapse does not hold and the period has ≥ 2 observables; descriptive if it has < 2 observables.

## Result
Card-level D1 collapse: **does not hold** (0/4 observables; within-regime permutation p = 0.073).

| Axis | Value |
| --- | --- |
| K = g_lag (H67 pool) | -0.018 ± 0.017 |
| equal-time dial g_eq | 0.154 |
| h = c_× trimmed (H86) | 0.0840 (φ 0.456) |
| kickoff S_text (H54) | -0.46 |
| N active (H85) | 8.4 |
| f_sched (H38) | -0.05 |

| Observable | Observed | D1 prediction (LOPO) | z | regime-only prediction |
| --- | --- | --- | --- | --- |
| settling time (log h) | 1.508 | 0.793 | 0.38 | 0.968 |
| herding share | 0.169 | 0.140 | 0.22 | 0.174 |
| idea branching (logit R) | -1.257 | -1.206 | -0.10 | -1.313 |
| loop rate (logit) | -0.670 | -1.748 | 1.00 | -1.783 |

Transformed scales: settling log active hours; herding share excess; branching and loop rate in logits. Data: `data/processed/H51-one-dial-collapse/results/phase_points.parquet`.

## Scorecard (period-specific axes)
D (unfitted observables placed against the dial), H (D1 vs regime-only prediction above).
