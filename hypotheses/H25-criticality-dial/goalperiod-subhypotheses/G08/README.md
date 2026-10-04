# H25 × G08: Design the AI Village benchmark for open-ended goal pursuit – and test yourselves on it! (2025-07-18 → 2025-08-12)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode C · 4 agents at start · 18 non-holdout days · 3.0 h/day (empirical).

## Why this period
One day-resolved stretch of the dial. Every non-holdout period gets the same daily dial (activity, talk, content) so periods can be compared through their fitted values. Reference values: H19 g_eq active 0.03, talk -0.01; H03 n̂ TALK 0.27.

## Prediction
*Written 2026-10-04 02:00 UTC, before running the dial on this period.* The card's predictions (P1–P7) as they apply here; H19's per-period values were known (disclosed in the card).
- **Activity dial** (stalls masked): daily values mostly in [−0.1, 0.4]; period mean near H19's g_eq active = 0.03 (± 0.02), lowered by 0–0.05 where stalls are masked: predicted range [-0.05, 0.06].
- **Talk dial** (stalls kept): period mean within ± max(0.05, 2 SE) of H19's g_eq talk = -0.01.
- **Content dial** (F2): period median in [0.15, 0.6], above the activity dial (HH108; credence 0.55), and below H01's 0.74.
- **Subcritical:** every day's upper 90% bound < 0.8 in all channels.
- Regime I/II: activity dial expected lower than in regime III; talk dial comparatively higher (H19).
- **Verdict rule** (card): *supported* if (i) all days subcritical in all estimable channels, (ii) the activity and talk dials with stalls kept reproduce H19's g_eq within max(0.05, 2 SE), and (iii) the period's median content dial (F2) is < 0.74; *failed* if any day has a lower 90% bound > 0.8 in any channel, or (ii) and (iii) both fail; *mixed* otherwise.
- *Against:* a confidently near-critical day; a period mean far from H19's estimator (implementation or stall effect larger than expected); content at or above 0.74 after field removal.
- First 3-hour days (07-18): exploratory hours-switch event.

## Result
| Dial | days | fixed-effect mean ± SE | random-effects mean ± SE | median | between-day I² (Cochran p) | share of days with upper bound < 0.8 | max lower bound |
| --- | --- | --- | --- | --- | --- | --- | --- |
| activity (stalls masked) | 18 | 0.020 ± 0.028 | 0.020 ± 0.028 | 0.035 | 0.00 (p 0.997) | 1.00 | -0.06 |
| activity (stalls kept) | 18 | 0.037 ± 0.029 | 0.037 ± 0.029 | 0.035 | 0.00 (p 0.854) | 1.00 | 0.12 |
| talk (stalls masked) | 18 | -0.030 ± 0.029 | -0.030 ± 0.029 | -0.024 | 0.00 (p 0.962) | 1.00 | -0.04 |
| talk (stalls kept) | 18 | -0.031 ± 0.030 | -0.031 ± 0.030 | -0.024 | 0.00 (p 0.963) | 1.00 | -0.09 |
| content F1 | 18 | 0.423 ± 0.044 | 0.400 ± 0.049 | 0.265 | 0.08 (p 0.355) | 1.00 | 0.52 |
| content F2 (primary) | 18 | 0.418 ± 0.043 | 0.418 ± 0.043 | 0.305 | 0.00 (p 0.471) | 0.94 | 0.52 |
| content F3 | 18 | 0.417 ± 0.046 | 0.417 ± 0.046 | 0.251 | 0.00 (p 0.725) | 0.89 | 0.47 |

| Check | Observed | Outcome |
| --- | --- | --- |
| (i) every day subcritical (upper 90% bound < 0.8, all channels) | no | fail |
| (ii) stalls-kept dials vs H19 g_eq (active 0.03, talk -0.01) | activity 0.04, talk -0.03 | pass |
| (iii) content F2 median < 0.74 | 0.30 | pass |
| any day confidently near-critical (lower bound > 0.8) | no | – |


Stall minutes masked: 0.6% of the day on average. T/T_c = 1/g for the activity dial (stalls masked): 49.85; amplification 1/(1 − g) = 1.02.

![daily dial](figures/G08_dial.png)  
Data: `data/processed/H25-criticality-dial/G08/dial_daily.parquet`, `results.json`.

## Scorecard (period-specific axes)
- **C (adequacy):** day-level null band (circular shifts): share of days with activity dial above its null 95th percentile = 0.06.
- **D (unfitted):** H19 agreement (ii) passes; H03 n̂ TALK 0.27 vs talk dial -0.03 (cross-period test in the card).
- **G (known structure):** see the card's event tests (regime switch, goal changes) where this period is involved.

## Notes
- 2026-10-04 02:14 UTC: results filled by `analysis/write_period_folders.py --results` from `analysis/explore.py` (exploratory round 1). Prediction block above unchanged from the --predict pass.
- Reading notes (card, Results): the content dial's upper bounds are wide, so check (i) fails in every period; fixed-effect means are pulled toward days with 3–4 talkers, whose bootstrap SEs are small (compare the random-effects mean); per-pair correlation, not g, is the size-free quantity (card, post hoc PH1).
