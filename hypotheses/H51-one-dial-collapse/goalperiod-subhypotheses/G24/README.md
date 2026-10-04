# H51 × G24: goal period #24

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #24 · regime I · active N 10.0 · units 24.

## Why this period
A non-holdout goal period with the three phase-diagram axes (H67 g_lag, H86 c_×, H85 N) and at least one observable; one point of the replication layer.

## Prediction
*The card's per-period rule, written 2026-10-04 20:40 UTC before any collapse statistic; this folder was written after the run and copies it.* Supported if the period's D1 (g_lag) leave-one-period-out residual lies inside the 80% band (|z| ≤ 1.28) for ≥ 3/4 of its observables and the card-level collapse holds; failed if the card-level collapse does not hold and the period has ≥ 2 observables; descriptive if it has < 2 observables.

## Result
Card-level D1 collapse: **does not hold** (0/4 observables; within-regime permutation p = 0.073).

| Axis | Value |
| --- | --- |
| K = g_lag (H67 pool) | 0.009 ± 0.018 |
| equal-time dial g_eq | 0.138 |
| h = c_× trimmed (H86) | 0.0038 (φ 0.076) |
| kickoff S_text (H54) | 0.78 |
| N active (H85) | 10.0 |
| f_sched (H38) | – |

| Observable | Observed | D1 prediction (LOPO) | z | regime-only prediction |
| --- | --- | --- | --- | --- |
| settling time (log h) | 4.331 | 0.818 | 1.88 | 0.819 |
| herding share | 0.065 | 0.134 | -0.54 | 0.180 |
| idea branching (logit R) | -1.766 | -1.223 | -1.04 | -1.286 |
| loop rate (logit) | -2.187 | -1.920 | -0.25 | -1.710 |

Transformed scales: settling log active hours; herding share excess; branching and loop rate in logits. Data: `data/processed/H51-one-dial-collapse/results/phase_points.parquet`.

## Scorecard (period-specific axes)
D (unfitted observables placed against the dial), H (D1 vs regime-only prediction above).
