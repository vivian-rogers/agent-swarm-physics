# H85 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-24)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** regime III · mode C · N 12.0–13.7 active agents · units 38a, 38b, 38c, 38d, 38e · 17 days with a window.

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
| 38a | 2026-04-02 → 2026-04-13 | 12.0 | 32.2 | 73.9 | 6.16 | 0.77 | 0.47 | 5.4 | 1.73 | 0.04 | 0.28 |
| 38b | 2026-04-14 → 2026-04-16 | 12.0 | 15.6 | 51.7 | 4.31 | 0.35 | 0.52 | 4.3 | 1.01 | -0.32 | -0.86 |
| 38c | 2026-04-17 → 2026-04-17 | 13.0 | 4.0 | 72.7 | 5.60 | 0.50 | 0.45 | 6.1 | 2.30 | -0.00 | -0.27 |
| 38d | 2026-04-20 → 2026-04-21 | 12.5 | 8.0 | 49.8 | 3.99 | 0.48 | 0.47 | 6.1 | 1.17 | -0.37 | -0.64 |
| 38e | 2026-04-22 → 2026-04-24 | 13.7 | 12.2 | 54.7 | 4.00 | 0.54 | 0.30 | 5.9 | 1.77 | -0.31 | -0.53 |

## Native N3: within-day room-size contrast (#best vs #rest)
*Prediction written 2026-10-04 20:04 UTC in the card:* β_room,msg ∈ [0.7, 1.3] and β_room,ment > β_room,msg; descriptive if the SD of the within-day log room-size ratio is < 0.1.

- Days: 17; SD of within-day ln(N_2/N_3) 0.184 (identified); mean -0.57.
- β_room,msg = 0.36 [0.02, 0.82] → outside [0.7, 1.3].
- β_room,ment = 1.12 [0.31, 2.04]; addressing per message 0.76 [-0.15, 1.62] (> 0 as predicted, CI includes 0).
- Pending set: β_room,k = 1.11 [0.82, 1.46] (k ∝ room N).
- Estimator: slope through the origin of the within-day room differences (day fixed effects, no room fixed effect; day bootstrap, 2,000 draws). Other rooms-era periods (G36, G42, G44 identified) and their random-effects mean are in the card.
- **Verdict: mixed.** Messages are sublinear in room size (fails [0.7, 1.3]); addressing grows faster than messages (as predicted, not significant).

## Scorecard (period-specific axes)
- Replication point: informs C and I in the main card (one point on the phase diagram), no period-level test.
