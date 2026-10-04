# H85 × G10: Complete as many games as you can in a week! (2025-08-18 → 2025-08-22)

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** regime I · mode I · N 7.0–7.0 active agents · units 10a, 10b · 5 days with a window.

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
| 10a | 2025-08-18 → 2025-08-19 | 7.0 | 5.2 | 91.9 | 13.13 | 0.22 | 0.10 | 8.7 | – (not git-dense) | -0.27 | -1.48 |
| 10b | 2025-08-20 → 2025-08-22 | 7.0 | 9.0 | 86.1 | 12.30 | 0.10 | 0.05 | 6.1 | – (not git-dense) | -0.34 | -2.36 |

## Scorecard (period-specific axes)
- Replication point: informs C and I in the main card (one point on the phase diagram), no period-level test.
