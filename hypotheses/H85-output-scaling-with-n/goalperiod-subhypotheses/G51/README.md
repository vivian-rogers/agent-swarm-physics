# H85 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-04)

**Verdict:** descriptive
**Role:** native (exploratory)
**Period:** regime III · mode I/K · N 21.0–32.0 active agents · units 51a, 51b, 51c, 51d, 51e, 51f, 51g, 51h, 51i, 51j, 51k, 51l · 45 days with a window.

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
| 51a | 2026-07-06 → 2026-07-08 | 21.0 | 32.9 | 119.5 | 5.69 | 1.23 | 0.55 | 20.6 | 3.31 | 0.33 | 0.60 |
| 51b | 2026-07-09 → 2026-07-09 | 24.0 | 8.1 | 116.7 | 4.86 | 1.03 | 0.63 | 19.5 | 3.39 | 0.26 | 0.24 |
| 51c | 2026-07-10 → 2026-07-16 | 25.0 | 42.2 | 93.7 | 3.75 | 0.95 | 0.51 | 24.0 | 5.54 | 0.03 | -0.11 |
| 51d | 2026-07-17 → 2026-07-23 | 26.0 | 40.5 | 123.7 | 4.76 | 1.28 | 0.57 | 26.1 | 5.99 | 0.30 | 0.43 |
| 51e | 2026-07-24 → 2026-07-28 | 27.0 | 28.8 | 98.7 | 3.66 | 1.18 | 0.59 | 26.0 | 5.10 | 0.06 | 0.08 |
| 51f | 2026-07-29 → 2026-08-04 | 27.0 | 40.4 | 105.8 | 3.92 | 1.22 | 0.57 | 25.2 | 4.91 | 0.13 | 0.18 |
| 51g | 2026-08-05 → 2026-08-21 | 27.0 | 105.4 | 111.4 | 4.13 | 0.79 | 0.57 | 18.0 | 4.68 | 0.18 | -0.21 |
| 51h | 2026-08-24 → 2026-08-27 | 27.0 | 32.5 | 95.7 | 3.55 | 0.79 | 0.50 | 23.3 | 5.69 | 0.03 | -0.35 |
| 51i | 2026-08-28 → 2026-08-31 | 28.0 | 16.2 | 90.8 | 3.24 | 0.69 | 0.48 | 25.8 | 3.86 | -0.04 | -0.59 |
| 51j | 2026-09-01 → 2026-09-02 | 29.0 | 16.4 | 95.4 | 3.29 | 0.79 | 0.40 | 23.9 | 4.31 | -0.00 | -0.44 |
| 51k | 2026-09-03 → 2026-09-03 | 31.0 | 8.1 | 121.0 | 3.90 | 1.14 | 0.52 | 22.4 | 2.97 | 0.22 | 0.09 |
| 51l | 2026-09-04 → 2026-09-04 | 32.0 | 8.1 | 141.8 | 4.43 | 0.96 | 0.59 | 22.6 | 3.25 | 0.36 | 0.04 |

## Native N2: roster-growth sweep (day level)
*Prediction written 2026-10-04 20:04 UTC in the card:* β_msg ∈ [0.7, 1.3]; β_ment − β_msg > 0; β_commit CI includes 1 (day points, NE43 step dummies at 08-05 and 08-21; sensitivity with a linear day trend).

- Non-holdout days: 45 (n_d 21–32); SD ln n_d after steps is small (0.079).
- β_msg = -0.02 [-0.76, 2.08]
- β_ment = 0.59 [-0.90, 5.45]
- β_reply = 0.20 [-1.05, 3.26]
- β_commit = 1.63 [-2.40, 2.91]
- β_ment_per_msg = 0.62 [-0.21, 4.06]
- β_k = 0.93 [0.31, 2.65]
- **Verdict: descriptive (unidentified).** Every CI spans more than two units of exponent: day-level N barely varies once the NE43 steps are absorbed, and roster joins coincide with time since kickoff.

## Scorecard (period-specific axes)
- Replication point: informs C and I in the main card (one point on the phase diagram), no period-level test.
