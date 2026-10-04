# H85 × G44: Finetune your leader! (2026-05-26 → 2026-05-29)

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** regime III · mode C · N 16.0–17.5 active agents · units 44a, 44b · 4 days with a window.

## Why this period
A point (or points) on the cross-unit scaling lines (layer 1). Each unit contributes one ln(Y/T) at its active population N; the exponent is the slope across units with regime intercepts and goal-cluster CIs (`analysis/replication.py`).

## Prediction
*Written 2026-10-04 20:04 UTC in the card, before any real-data statistic (templated replication prediction).*
- This period's units are points on the cross-unit lines ln(Y/T) = α_regime + β ln N. One period cannot test β.
- Card predictions the points feed: messages β ∈ [0.85, 1.15]; addressing per message rises with N as 0.34 γ_k; reply parents β ≈ 1.25 (budget-corrected); committed work β = 1.0 ± 0.1 (descriptive after A3).
- *Counts against (card level only):* the cross-unit CIs; a single period's residual is descriptive.

## Result
*Run 2026-10-04 20:13 UTC (`analysis/replication.py` → `data/processed/H85-output-scaling-with-n/replication/`).* Residuals are from the M1 fits across all 71 units (ln units; positive = above the line). Card-level: β_msg = 0.33 [-0.18, 0.64].

| Unit | Days | N | T (h) | msg / h | msg per agent-h | addressed / msg | reply share | k at talk | commits per agent-h | resid msg | resid addressed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 44a | 2026-05-26 → 2026-05-27 | 16.0 | 8.1 | 93.5 | 5.84 | 1.30 | 0.74 | 6.0 | 5.74 | 0.18 | 0.71 |
| 44b | 2026-05-28 → 2026-05-29 | 17.5 | 8.1 | 121.5 | 6.94 | 1.13 | 0.72 | 8.2 | 5.26 | 0.41 | 0.73 |

## Scorecard (period-specific axes)
- Replication point: informs C and I in the main card (one point on the phase diagram), no period-level test.
