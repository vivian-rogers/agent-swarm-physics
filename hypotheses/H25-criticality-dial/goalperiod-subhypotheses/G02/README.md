# H25 × G02: Unsupervised agents look back on their previous goal and forward to their next (2025-05-10 → 2025-05-11)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1: mixed; corrected table, same rule)
**Role:** replication (exploratory (round 1, non-holdout))
**Period:** regime I · mode F · 4 agents at start · 2 non-holdout days · 1.9 h/day (empirical).

## Why this period
One day-resolved stretch of the dial. Every non-holdout period gets the same daily dial (activity, talk, content) so periods can be compared through their fitted values. Reference values: H19 g_eq active 0.23, talk 0.28; H03 n̂ TALK 0.72.

## Prediction
*Written 2026-10-04 02:00 UTC, before running the dial on this period.* The card's predictions (P1–P7) as they apply here; H19's per-period values were known (disclosed in the card).
- **Activity dial** (stalls masked): daily values mostly in [−0.1, 0.4]; period mean near H19's g_eq active = 0.23 (± 0.05), lowered by 0–0.05 where stalls are masked: predicted range [0.15, 0.26].
- **Talk dial** (stalls kept): period mean within ± max(0.05, 2 SE) of H19's g_eq talk = 0.28.
- **Content dial** (F2): period median in [0.15, 0.6], above the activity dial (HH108; credence 0.55), and below H01's 0.74.
- **Subcritical:** every day's upper 90% bound < 0.8 in all channels.
- Regime I/II: activity dial expected lower than in regime III; talk dial comparatively higher (H19).
- **Verdict rule** (card): *supported* if (i) all days subcritical in all estimable channels, (ii) the activity and talk dials with stalls kept reproduce H19's g_eq within max(0.05, 2 SE), and (iii) the period's median content dial (F2) is < 0.74; *failed* if any day has a lower 90% bound > 0.8 in any channel, or (ii) and (iii) both fail; *mixed* otherwise.
- *Against:* a confidently near-critical day; a period mean far from H19's estimator (implementation or stall effect larger than expected); content at or above 0.74 after field removal.
- Only 2 day(s): low power; the period mean has a wide interval.

## Result
| Dial | days | fixed-effect mean ± SE | random-effects mean ± SE | median | between-day I² (Cochran p) | share of days with upper bound < 0.8 | max lower bound |
| --- | --- | --- | --- | --- | --- | --- | --- |
| activity (stalls masked) | 2 | 0.224 ± 0.071 | 0.224 ± 0.071 | 0.225 | 0.00 (p 0.979) | 1.00 | 0.07 |
| activity (stalls kept) | 2 | 0.224 ± 0.073 | 0.224 ± 0.073 | 0.225 | 0.00 (p 0.980) | 1.00 | 0.04 |
| talk (stalls masked) | 2 | 0.344 ± 0.052 | 0.312 ± 0.097 | 0.292 | 0.61 (p 0.109) | 1.00 | 0.29 |
| talk (stalls kept) | 2 | 0.333 ± 0.057 | 0.308 ± 0.097 | 0.292 | 0.60 (p 0.114) | 1.00 | 0.26 |
| content F1 | 2 | 0.674 ± 0.074 | 0.662 ± 0.093 | 0.639 | 0.33 (p 0.223) | 0.50 | 0.63 |
| content F2 (primary) | 2 | 0.667 ± 0.068 | 0.655 ± 0.095 | 0.640 | 0.46 (p 0.174) | 0.50 | 0.63 |
| content F3 | 2 | 0.653 ± 0.108 | 0.653 ± 0.108 | 0.598 | 0.00 (p 0.345) | 0.00 | 0.56 |

| Check | Observed | Outcome |
| --- | --- | --- |
| (i) every day subcritical (upper 90% bound < 0.8, all channels) | no | fail |
| (ii) stalls-kept dials vs H19 g_eq (active 0.23, talk 0.28) | activity 0.22, talk 0.33 | pass |
| (iii) content F2 median < 0.74 | 0.64 | pass |
| any day confidently near-critical (lower bound > 0.8) | no | – |


Stall minutes masked: 0.0% of the day on average. T/T_c = 1/g for the activity dial (stalls masked): 4.47; amplification 1/(1 − g) = 1.29.

![daily dial](figures/G02_dial.png)  
Data: `data/processed/H25-criticality-dial/G02/dial_daily.parquet`, `results.json`.

## Scorecard (period-specific axes)
- **C (adequacy):** day-level null band (circular shifts): share of days with activity dial above its null 95th percentile = 1.00.
- **D (unfitted):** H19 agreement (ii) passes; H03 n̂ TALK 0.72 vs talk dial 0.34 (cross-period test in the card).
- **G (known structure):** see the card's event tests (regime switch, goal changes) where this period is involved.

## Round 1b (improved data, 2026-10-04)
Same pipeline (`analysis/explore.py --data-version fixed`) on DQ8's `activity_bins_fixed` and the shared `outages_fixed` stall table (round 1's activity table dropped about half of all events). Predictions and verdict rule unchanged; check (ii) now compares with H19's estimator recomputed on the fixed table (round-1 H19 values are stale). The DQ8 row trims each day to the window in which all agents are between their first and last active minute before the block-shift null is drawn (whole-day block-shift nulls reject 28–34% of independent swarms).

| Quantity | Round 1 (old table) | Round 1b (fixed table) |
| --- | --- | --- |
| activity dial, stalls masked (fixed-effect mean; median) | 0.22; 0.22 | 0.29; 0.29 |
| activity dial, stalls kept vs H19 g_eq | 0.22 vs 0.23 | 0.29 vs 0.29 (H19 estimator on the fixed table) |
| talk dial, stalls masked (fixed-effect; random-effects) | 0.34; 0.31 | 0.42; 0.42 |
| talk dial, stalls kept vs H19 g_eq talk | 0.33 vs 0.28 | 0.42 vs 0.39 |
| days above the block-shift null q95: activity (round-1 design → **DQ8 trim**) | 2/2 | 2/2 → 2/2 |
| median activity dial with the DQ8 trim | – | 0.35 |
| content dial F2 median (inputs unchanged) | 0.64 | 0.64 |
| per-period verdict (card rule) | mixed | mixed |

Data: `data/processed/H25-criticality-dial/r1b/G02/`.

## Notes
- 2026-10-04 02:14 UTC: results filled by `analysis/write_period_folders.py --results` from `analysis/explore.py` (exploratory round 1). Prediction block above unchanged from the --predict pass.
- Reading notes (card, Results): the content dial's upper bounds are wide, so check (i) fails in every period; fixed-effect means are pulled toward days with 3–4 talkers, whose bootstrap SEs are small (compare the random-effects mean); per-pair correlation, not g, is the size-free quantity (card, post hoc PH1).
