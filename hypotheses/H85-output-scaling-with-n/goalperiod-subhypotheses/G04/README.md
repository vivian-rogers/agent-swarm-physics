# H85 × G04: Write a story and celebrate it with 100 people in person (2025-05-15 → 2025-06-18)

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** regime I · mode C · N 4.0–4.0 active agents · units 4a, 4b, 4c, 4d · 26 days with a window.

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
| 4a | 2025-05-15 → 2025-05-21 | 4.0 | 9.5 | 175.2 | 43.80 | 0.72 | 0.49 | 3.3 | – (not git-dense) | 0.56 | 0.97 |
| 4b | 2025-05-22 → 2025-05-22 | 4.0 | 2.0 | 157.9 | 39.46 | 0.36 | 0.37 | 4.3 | – (not git-dense) | 0.45 | 0.18 |
| 4c | 2025-05-23 → 2025-06-18 | 4.0 | 37.7 | 112.3 | 28.08 | 0.54 | 0.40 | 4.2 | – (not git-dense) | 0.11 | 0.24 |
| 4d | 2025-06-18 → 2025-06-18 | 4.0 | 3.0 | 107.9 | 26.98 | 0.23 | 0.34 | 4.9 | – (not git-dense) | 0.07 | -0.67 |

## Scorecard (period-specific axes)
- Replication point: informs C and I in the main card (one point on the phase diagram), no period-level test.
