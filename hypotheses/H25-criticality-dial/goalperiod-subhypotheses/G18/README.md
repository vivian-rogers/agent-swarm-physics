# H25 × G18: Reduce global poverty as much as you can (2025-10-20 → 2025-10-31)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode C · 7 agents at start · 10 non-holdout days · 4.0 h/day (empirical).

## Why this period
One day-resolved stretch of the dial. Every non-holdout period gets the same daily dial (activity, talk, content) so periods can be compared through their fitted values. Reference values: H19 g_eq active 0.08, talk 0.24; H03 n̂ TALK 0.70.

## Prediction
*Written 2026-10-04 02:00 UTC, before running the dial on this period.* The card's predictions (P1–P7) as they apply here; H19's per-period values were known (disclosed in the card).
- **Activity dial** (stalls masked): daily values mostly in [−0.1, 0.4]; period mean near H19's g_eq active = 0.08 (± 0.04), lowered by 0–0.05 where stalls are masked: predicted range [-0.00, 0.11].
- **Talk dial** (stalls kept): period mean within ± max(0.05, 2 SE) of H19's g_eq talk = 0.24.
- **Content dial** (F2): period median in [0.15, 0.6], above the activity dial (HH108; credence 0.55), and below H01's 0.74.
- **Subcritical:** every day's upper 90% bound < 0.8 in all channels.
- Regime I/II: activity dial expected lower than in regime III; talk dial comparatively higher (H19).
- **Verdict rule** (card): *supported* if (i) all days subcritical in all estimable channels, (ii) the activity and talk dials with stalls kept reproduce H19's g_eq within max(0.05, 2 SE), and (iii) the period's median content dial (F2) is < 0.74; *failed* if any day has a lower 90% bound > 0.8 in any channel, or (ii) and (iii) both fail; *mixed* otherwise.
- *Against:* a confidently near-critical day; a period mean far from H19's estimator (implementation or stall effect larger than expected); content at or above 0.74 after field removal.
- First empirical 4-hour days (10-20): exploratory hours-switch event.

## Result
| Dial | days | fixed-effect mean ± SE | random-effects mean ± SE | median | between-day I² (Cochran p) | share of days with upper bound < 0.8 | max lower bound |
| --- | --- | --- | --- | --- | --- | --- | --- |
| activity (stalls masked) | 10 | 0.087 ± 0.037 | 0.089 ± 0.053 | 0.046 | 0.47 (p 0.047) | 1.00 | 0.13 |
| activity (stalls kept) | 10 | 0.095 ± 0.038 | 0.093 ± 0.052 | 0.046 | 0.43 (p 0.074) | 1.00 | 0.13 |
| talk (stalls masked) | 9 | 0.268 ± 0.034 | 0.263 ± 0.039 | 0.247 | 0.22 (p 0.248) | 1.00 | 0.32 |
| talk (stalls kept) | 9 | 0.265 ± 0.035 | 0.260 ± 0.040 | 0.247 | 0.23 (p 0.240) | 1.00 | 0.31 |
| content F1 | 10 | 0.814 ± 0.009 | 0.799 ± 0.020 | 0.776 | 0.55 (p 0.019) | 0.00 | 0.87 |
| content F2 (primary) | 10 | 0.809 ± 0.010 | 0.795 ± 0.017 | 0.778 | 0.37 (p 0.115) | 0.00 | 0.87 |
| content F3 | 10 | 0.810 ± 0.009 | 0.800 ± 0.014 | 0.784 | 0.20 (p 0.258) | 0.00 | 0.86 |

| Check | Observed | Outcome |
| --- | --- | --- |
| (i) every day subcritical (upper 90% bound < 0.8, all channels) | no | fail |
| (ii) stalls-kept dials vs H19 g_eq (active 0.08, talk 0.24) | activity 0.10, talk 0.26 | pass |
| (iii) content F2 median < 0.74 | 0.78 | fail |
| any day confidently near-critical (lower bound > 0.8) | yes | – |


Stall minutes masked: 0.0% of the day on average. T/T_c = 1/g for the activity dial (stalls masked): 11.48; amplification 1/(1 − g) = 1.10.

![daily dial](figures/G18_dial.png)  
Data: `data/processed/H25-criticality-dial/G18/dial_daily.parquet`, `results.json`.

## Scorecard (period-specific axes)
- **C (adequacy):** day-level null band (circular shifts): share of days with activity dial above its null 95th percentile = 0.40.
- **D (unfitted):** H19 agreement (ii) passes; H03 n̂ TALK 0.70 vs talk dial 0.27 (cross-period test in the card).
- **G (known structure):** see the card's event tests (regime switch, goal changes) where this period is involved.

## Notes
- 2026-10-04 02:14 UTC: results filled by `analysis/write_period_folders.py --results` from `analysis/explore.py` (exploratory round 1). Prediction block above unchanged from the --predict pass.
- Reading notes (card, Results): the content dial's upper bounds are wide, so check (i) fails in every period; fixed-effect means are pulled toward days with 3–4 talkers, whose bootstrap SEs are small (compare the random-effects mean); per-pair correlation, not g, is the size-free quantity (card, post hoc PH1).
