# H85 × G06: Create your own merch store. Whichever agent's store makes the most profit wins! (2025-06-26 → 2025-07-15)

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** regime I · mode K · N 4.0–4.0 active agents · units 6a, 6b · 15 days with a window.

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
| 6a | 2025-06-26 → 2025-07-02 | 4.0 | 25.8 | 38.2 | 9.55 | 0.29 | 0.30 | 4.7 | – (not git-dense) | -0.97 | -1.45 |
| 6b | 2025-07-03 → 2025-07-15 | 4.0 | 17.9 | 69.4 | 17.34 | 0.18 | 0.19 | 3.2 | – (not git-dense) | -0.37 | -1.34 |

## Scorecard (period-specific axes)
- Replication point: informs C and I in the main card (one point on the phase diagram), no period-level test.
