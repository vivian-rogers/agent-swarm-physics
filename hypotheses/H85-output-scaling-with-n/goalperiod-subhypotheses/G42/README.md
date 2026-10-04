# H85 × G42: Run your own Youtube channel! (2026-05-18 → 2026-05-22)

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** regime III · mode I · N 15.0–16.0 active agents · units 42a, 42b · 5 days with a window.

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
| 42a | 2026-05-18 → 2026-05-19 | 15.0 | 8.0 | 54.1 | 3.60 | 1.08 | 0.46 | 8.2 | 4.02 | -0.35 | 0.05 |
| 42b | 2026-05-20 → 2026-05-22 | 16.0 | 12.1 | 64.5 | 4.03 | 0.96 | 0.51 | 7.5 | 5.84 | -0.19 | 0.03 |

## Scorecard (period-specific axes)
- Replication point: informs C and I in the main card (one point on the phase diagram), no period-level test.
