# H106 × G23: slow-mode decorrelation vs N (2025-12-15 → 2025-12-19, non-holdout days)

**Verdict:** descriptive
**Role:** exploratory
**Period:** regime I · active population N ≈ 10.0 (block mean) · 1 goal × week block(s) · 5 eligible days. Splits: ISO weeks (blocks, H81).

## Why this period
A regime-I goal period with ≥ 1 block of ≥ 4 agents with residuals: one point (N_G, ρ_G) on the finite-size plot.

## Prediction
*Written 2026-10-04 21:39 UTC, before running on this period.*
Regime-I replication point. Observable: ρ_G, the goal-pair-weighted mean disattenuated similarity (4-agent subsets, split-half R̂) between this period's blocks and other goals' blocks within 10 active days, reported with N_G = 10.0. One period cannot test the slope, so the verdict is **descriptive**. Under the finite magnet (α_k = −1) periods with larger N have larger ρ_G (slower decorrelation); under an outside drift ρ_G does not depend on N. The card-level α_k decides.

## Result
| Model | N_G | ρ_G (disattenuated, ≤ 10 active days) | SE | pairs | implied k (per active day) |
| --- | --- | --- | --- | --- | --- |
| bge_small | 10.0 | 0.068 | 0.129 | 3 | 0.203 |
| gte_modernbert | 10.0 | -0.038 | 0.078 | 3 | n/a |

Verdict **descriptive**: one period cannot test the slope; the card-level α_k decides (see the card). The implied k uses the card-level amplitude Â of the same model.

## Scorecard (period-specific axes)
C, D only at card level (the slope is a cross-period statistic).

## Notes
- Data: `data/processed/H106-slow-mode-finite-size/replication/periods.parquet`.
