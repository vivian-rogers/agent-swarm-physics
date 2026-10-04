# H106 × G21: slow-mode decorrelation vs N (2025-12-01 → 2025-12-05, non-holdout days)

**Verdict:** descriptive
**Role:** exploratory
**Period:** regime I · active population N ≈ 8.4 (block mean) · 1 goal × week block(s) · 5 eligible days. Splits: ISO weeks (blocks, H81).

## Why this period
A regime-I goal period with ≥ 1 block of ≥ 4 agents with residuals: one point (N_G, ρ_G) on the finite-size plot.

## Prediction
*Written 2026-10-04 21:39 UTC, before running on this period.*
Regime-I replication point. Observable: ρ_G, the goal-pair-weighted mean disattenuated similarity (4-agent subsets, split-half R̂) between this period's blocks and other goals' blocks within 10 active days, reported with N_G = 8.4. One period cannot test the slope, so the verdict is **descriptive**. Under the finite magnet (α_k = −1) periods with larger N have larger ρ_G (slower decorrelation); under an outside drift ρ_G does not depend on N. The card-level α_k decides.

## Result
| Model | N_G | ρ_G (disattenuated, ≤ 10 active days) | SE | pairs | implied k (per active day) |
| --- | --- | --- | --- | --- | --- |
| bge_small | 8.4 | 0.078 | 0.085 | 3 | 0.177 |
| gte_modernbert | 8.4 | 0.001 | 0.058 | 3 | 0.777 |

Verdict **descriptive**: one period cannot test the slope; the card-level α_k decides (see the card). The implied k uses the card-level amplitude Â of the same model.

## Scorecard (period-specific axes)
C, D only at card level (the slope is a cross-period statistic).

## Notes
- Data: `data/processed/H106-slow-mode-finite-size/replication/periods.parquet`.
