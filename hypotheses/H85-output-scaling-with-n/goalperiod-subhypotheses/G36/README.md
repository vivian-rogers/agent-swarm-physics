# H85 × G36: Interact with other AI agents outside the Village! (2026-03-23 → 2026-03-27)

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** regime II/III · mode C · N 12.0–12.0 active agents · units 36a, 36b, 36c · 5 days with a window.

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
| 36a | 2026-03-23 → 2026-03-23 | 12.0 | 4.0 | 116.3 | 9.69 | 0.70 | 0.41 | 6.0 | 2.46 | -0.05 | -0.27 |
| 36b | 2026-03-24 → 2026-03-25 | 12.0 | 8.1 | 69.6 | 5.80 | 0.69 | 0.37 | 4.4 | 2.21 | -0.02 | 0.10 |
| 36c | 2026-03-26 → 2026-03-27 | 12.0 | 8.1 | 68.3 | 5.70 | 1.08 | 0.49 | 5.1 | 1.78 | -0.04 | 0.53 |

## Scorecard (period-specific axes)
- Replication point: informs C and I in the main card (one point on the phase diagram), no period-level test.
