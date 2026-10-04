# H106 × G44: slow-mode decorrelation vs N (2026-05-26 → 2026-05-29, non-holdout days)

**Verdict:** descriptive
**Role:** exploratory
**Period:** regime III · active population N ≈ 16.8 (block mean) · 1 goal × week block(s) · 4 eligible days. Splits: ISO weeks (blocks, H81).

## Why this period
A regime-III goal period with ≥ 1 block of ≥ 4 agents with residuals: one point (N_G, ρ_G) on the finite-size plot.

## Prediction
*Written 2026-10-04 21:39 UTC, before running on this period.*
Regime-III point (descriptive, separate phase-diagram point; never pooled with regime I). Observable: ρ_G as in regime I, N_G = 16.8. H81 found the regime-III slow mode marginal, so ρ_G may be near 0. No verdict.

## Result
| Model | N_G | ρ_G (disattenuated, ≤ 10 active days) | SE | pairs | implied k (per active day) |
| --- | --- | --- | --- | --- | --- |
| bge_small | 16.8 | 0.069 | n/a | 1 | 0.376 |
| gte_modernbert | 16.8 | 0.111 | n/a | 1 | 0.337 |

Verdict **descriptive**: one period cannot test the slope; the card-level α_k decides (see the card). The implied k uses the card-level amplitude Â of the same model.

## Scorecard (period-specific axes)
C, D only at card level (the slope is a cross-period statistic).

## Notes
- Data: `data/processed/H106-slow-mode-finite-size/replication/periods.parquet`.
