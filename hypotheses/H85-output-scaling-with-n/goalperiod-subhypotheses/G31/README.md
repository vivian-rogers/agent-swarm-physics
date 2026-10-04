# H85 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-20)

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** regime I · mode F · N 11.0–12.0 active agents · units 31a, 31b, 31c, 31d · 5 days with a window.

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
| 31a | 2026-02-16 → 2026-02-17 | 11.0 | 8.0 | 132.5 | 12.05 | 1.20 | 0.36 | 11.9 | 4.98 | -0.06 | 0.06 |
| 31b | 2026-02-18 → 2026-02-18 | 12.0 | 4.0 | 143.4 | 11.95 | 1.12 | 0.35 | 12.4 | 5.87 | -0.01 | -0.02 |
| 31c | 2026-02-19 → 2026-02-19 | 11.0 | 4.0 | 139.4 | 12.67 | 0.94 | 0.28 | 10.5 | 6.78 | -0.01 | -0.13 |
| 31d | 2026-02-20 → 2026-02-20 | 11.0 | 4.0 | 148.4 | 13.49 | 1.11 | 0.40 | 12.5 | 6.38 | 0.05 | 0.10 |

## Scorecard (period-specific axes)
- Replication point: informs C and I in the main card (one point on the phase diagram), no period-level test.
