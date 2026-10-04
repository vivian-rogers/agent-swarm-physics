# H106 × G37: slow-mode decorrelation vs N (2026-03-30 → 2026-04-01, non-holdout days)

**Verdict:** descriptive
**Role:** exploratory
**Period:** regime III · active population N ≈ 12.0 (block mean) · 1 goal × week block(s) · 3 eligible days. Splits: ISO weeks (blocks, H81).

## Why this period
A regime-III goal period with ≥ 1 block of ≥ 4 agents with residuals: one point (N_G, ρ_G) on the finite-size plot.

## Prediction
*Written 2026-10-04 21:39 UTC, before running on this period.*
Regime-III point (descriptive, separate phase-diagram point; never pooled with regime I). Observable: ρ_G as in regime I, N_G = 12.0. H81 found the regime-III slow mode marginal, so ρ_G may be near 0. No verdict.

## Result
| Model | N_G | ρ_G (disattenuated, ≤ 10 active days) | SE | pairs | implied k (per active day) |
| --- | --- | --- | --- | --- | --- |
| bge_small | 12.0 | 0.107 | 0.026 | 3 | 0.433 |
| gte_modernbert | 12.0 | 0.093 | 0.052 | 3 | 0.543 |

Verdict **descriptive**: one period cannot test the slope; the card-level α_k decides (see the card). The implied k uses the card-level amplitude Â of the same model.

## Scorecard (period-specific axes)
C, D only at card level (the slope is a cross-period statistic).

## Notes
- Data: `data/processed/H106-slow-mode-finite-size/replication/periods.parquet`.
