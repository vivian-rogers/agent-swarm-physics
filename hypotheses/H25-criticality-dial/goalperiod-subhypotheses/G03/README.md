# H25 × G03: Holiday: do whatever you'd like! Next goal will begin soon (2025-05-12 → 2025-05-14)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode F · 4 agents at start · 3 non-holdout days · 2.0 h/day (empirical).

## Why this period
One day-resolved stretch of the dial. Every non-holdout period gets the same daily dial (activity, talk, content) so periods can be compared through their fitted values. Reference values: H19 g_eq active 0.02, talk 0.10; H03 n̂ TALK 0.66.

## Prediction
*Written 2026-10-04 02:00 UTC, before running the dial on this period.* The card's predictions (P1–P7) as they apply here; H19's per-period values were known (disclosed in the card).
- **Activity dial** (stalls masked): daily values mostly in [−0.1, 0.4]; period mean near H19's g_eq active = 0.02 (± 0.06), lowered by 0–0.05 where stalls are masked: predicted range [-0.06, 0.05].
- **Talk dial** (stalls kept): period mean within ± max(0.05, 2 SE) of H19's g_eq talk = 0.10.
- **Content dial** (F2): period median in [0.15, 0.6], above the activity dial (HH108; credence 0.55), and below H01's 0.74.
- **Subcritical:** every day's upper 90% bound < 0.8 in all channels.
- Regime I/II: activity dial expected lower than in regime III; talk dial comparatively higher (H19).
- **Verdict rule** (card): *supported* if (i) all days subcritical in all estimable channels, (ii) the activity and talk dials with stalls kept reproduce H19's g_eq within max(0.05, 2 SE), and (iii) the period's median content dial (F2) is < 0.74; *failed* if any day has a lower 90% bound > 0.8 in any channel, or (ii) and (iii) both fail; *mixed* otherwise.
- *Against:* a confidently near-critical day; a period mean far from H19's estimator (implementation or stall effect larger than expected); content at or above 0.74 after field removal.
- Only 3 day(s): low power; the period mean has a wide interval.

## Result
| Dial | days | fixed-effect mean ± SE | random-effects mean ± SE | median | between-day I² (Cochran p) | share of days with upper bound < 0.8 | max lower bound |
| --- | --- | --- | --- | --- | --- | --- | --- |
| activity (stalls masked) | 3 | 0.018 ± 0.102 | 0.018 ± 0.102 | 0.024 | 0.00 (p 0.911) | 1.00 | -0.23 |
| activity (stalls kept) | 3 | 0.022 ± 0.103 | 0.022 ± 0.103 | 0.024 | 0.00 (p 0.913) | 1.00 | -0.23 |
| talk (stalls masked) | 3 | 0.085 ± 0.079 | 0.081 ± 0.090 | 0.122 | 0.21 (p 0.283) | 1.00 | -0.05 |
| talk (stalls kept) | 3 | 0.093 ± 0.077 | 0.089 ± 0.086 | 0.122 | 0.18 (p 0.297) | 1.00 | -0.06 |
| content F1 | 3 | 0.588 ± 0.025 | 0.588 ± 0.025 | 0.581 | 0.00 (p 0.427) | 0.67 | 0.63 |
| content F2 (primary) | 3 | 0.575 ± 0.043 | 0.575 ± 0.043 | 0.591 | 0.00 (p 0.781) | 0.33 | 0.59 |
| content F3 | 3 | 0.564 ± 0.040 | 0.564 ± 0.040 | 0.559 | 0.00 (p 0.788) | 0.67 | 0.56 |

| Check | Observed | Outcome |
| --- | --- | --- |
| (i) every day subcritical (upper 90% bound < 0.8, all channels) | no | fail |
| (ii) stalls-kept dials vs H19 g_eq (active 0.02, talk 0.10) | activity 0.02, talk 0.09 | pass |
| (iii) content F2 median < 0.74 | 0.59 | pass |
| any day confidently near-critical (lower bound > 0.8) | no | – |


Stall minutes masked: 0.0% of the day on average. T/T_c = 1/g for the activity dial (stalls masked): 56.34; amplification 1/(1 − g) = 1.02.

![daily dial](figures/G03_dial.png)  
Data: `data/processed/H25-criticality-dial/G03/dial_daily.parquet`, `results.json`.

## Scorecard (period-specific axes)
- **C (adequacy):** day-level null band (circular shifts): share of days with activity dial above its null 95th percentile = 0.00.
- **D (unfitted):** H19 agreement (ii) passes; H03 n̂ TALK 0.66 vs talk dial 0.08 (cross-period test in the card).
- **G (known structure):** see the card's event tests (regime switch, goal changes) where this period is involved.

## Notes
- 2026-10-04 02:14 UTC: results filled by `analysis/write_period_folders.py --results` from `analysis/explore.py` (exploratory round 1). Prediction block above unchanged from the --predict pass.
- Reading notes (card, Results): the content dial's upper bounds are wide, so check (i) fails in every period; fixed-effect means are pulled toward days with 3–4 talkers, whose bootstrap SEs are small (compare the random-effects mean); per-pair correlation, not g, is the size-free quantity (card, post hoc PH1).
