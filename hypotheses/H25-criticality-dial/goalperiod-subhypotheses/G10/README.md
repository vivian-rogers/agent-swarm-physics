# H25 × G10: Complete as many games as you can in a week! (2025-08-18 → 2025-08-22)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1: mixed; corrected table, same rule)
**Role:** replication (exploratory (round 1, non-holdout))
**Period:** regime I · mode I · 7 agents at start · 5 non-holdout days · 3.0 h/day (empirical).

## Why this period
One day-resolved stretch of the dial. Every non-holdout period gets the same daily dial (activity, talk, content) so periods can be compared through their fitted values. Reference values: H19 g_eq active 0.29, talk 0.15; H03 n̂ TALK 0.22.

## Prediction
*Written 2026-10-04 02:00 UTC, before running the dial on this period.* The card's predictions (P1–P7) as they apply here; H19's per-period values were known (disclosed in the card).
- **Activity dial** (stalls masked): daily values mostly in [−0.1, 0.4]; period mean near H19's g_eq active = 0.29 (± 0.14), lowered by 0–0.05 where stalls are masked: predicted range [0.21, 0.32].
- **Talk dial** (stalls kept): period mean within ± max(0.05, 2 SE) of H19's g_eq talk = 0.15.
- **Content dial** (F2): period median in [0.15, 0.6], above the activity dial (HH108; credence 0.55), and below H01's 0.74.
- **Subcritical:** every day's upper 90% bound < 0.8 in all channels.
- Regime I/II: activity dial expected lower than in regime III; talk dial comparatively higher (H19).
- **Verdict rule** (card): *supported* if (i) all days subcritical in all estimable channels, (ii) the activity and talk dials with stalls kept reproduce H19's g_eq within max(0.05, 2 SE), and (iii) the period's median content dial (F2) is < 0.74; *failed* if any day has a lower 90% bound > 0.8 in any channel, or (ii) and (iii) both fail; *mixed* otherwise.
- *Against:* a confidently near-critical day; a period mean far from H19's estimator (implementation or stall effect larger than expected); content at or above 0.74 after field removal.
- Batch join (NE27, N 4 → 7) on its first day.

## Result
| Dial | days | fixed-effect mean ± SE | random-effects mean ± SE | median | between-day I² (Cochran p) | share of days with upper bound < 0.8 | max lower bound |
| --- | --- | --- | --- | --- | --- | --- | --- |
| activity (stalls masked) | 5 | 0.242 ± 0.060 | 0.201 ± 0.096 | 0.125 | 0.56 (p 0.060) | 1.00 | 0.21 |
| activity (stalls kept) | 5 | 0.311 ± 0.058 | 0.250 ± 0.122 | 0.125 | 0.76 (p 0.002) | 1.00 | 0.38 |
| talk (stalls masked) | 5 | 0.126 ± 0.057 | 0.126 ± 0.057 | 0.101 | 0.00 (p 0.754) | 1.00 | 0.01 |
| talk (stalls kept) | 5 | 0.139 ± 0.055 | 0.139 ± 0.055 | 0.101 | 0.00 (p 0.689) | 1.00 | 0.03 |
| content F1 | 5 | 0.594 ± 0.169 | 0.594 ± 0.169 | 0.318 | 0.00 (p 0.996) | 0.20 | 0.37 |
| content F2 (primary) | 5 | 0.525 ± 0.205 | 0.525 ± 0.205 | 0.192 | 0.00 (p 0.995) | 0.20 | 0.19 |
| content F3 | 5 | 0.423 ± 1.840 | 0.423 ± 1.840 | 0.254 | 0.00 (p 1.000) | 0.40 | -0.10 |

| Check | Observed | Outcome |
| --- | --- | --- |
| (i) every day subcritical (upper 90% bound < 0.8, all channels) | no | fail |
| (ii) stalls-kept dials vs H19 g_eq (active 0.29, talk 0.15) | activity 0.31, talk 0.14 | pass |
| (iii) content F2 median < 0.74 | 0.19 | pass |
| any day confidently near-critical (lower bound > 0.8) | no | – |


Stall minutes masked: 3.8% of the day on average. T/T_c = 1/g for the activity dial (stalls masked): 4.13; amplification 1/(1 − g) = 1.32.

![daily dial](figures/G10_dial.png)  
Data: `data/processed/H25-criticality-dial/G10/dial_daily.parquet`, `results.json`.

## Scorecard (period-specific axes)
- **C (adequacy):** day-level null band (circular shifts): share of days with activity dial above its null 95th percentile = 0.60.
- **D (unfitted):** H19 agreement (ii) passes; H03 n̂ TALK 0.22 vs talk dial 0.13 (cross-period test in the card).
- **G (known structure):** see the card's event tests (regime switch, goal changes) where this period is involved.

## Round 1b (improved data, 2026-10-04)
Same pipeline (`analysis/explore.py --data-version fixed`) on DQ8's `activity_bins_fixed` and the shared `outages_fixed` stall table (round 1's activity table dropped about half of all events). Predictions and verdict rule unchanged; check (ii) now compares with H19's estimator recomputed on the fixed table (round-1 H19 values are stale). The DQ8 row trims each day to the window in which all agents are between their first and last active minute before the block-shift null is drawn (whole-day block-shift nulls reject 28–34% of independent swarms).

| Quantity | Round 1 (old table) | Round 1b (fixed table) |
| --- | --- | --- |
| activity dial, stalls masked (fixed-effect mean; median) | 0.24; 0.12 | 0.30; 0.10 |
| activity dial, stalls kept vs H19 g_eq | 0.31 vs 0.29 | 0.37 vs 0.37 (H19 estimator on the fixed table) |
| talk dial, stalls masked (fixed-effect; random-effects) | 0.13; 0.13 | 0.14; 0.14 |
| talk dial, stalls kept vs H19 g_eq talk | 0.14 vs 0.15 | 0.15 vs 0.14 |
| days above the block-shift null q95: activity (round-1 design → **DQ8 trim**) | 3/5 | 2/5 → 2/5 |
| median activity dial with the DQ8 trim | – | 0.01 |
| content dial F2 median (inputs unchanged) | 0.19 | 0.19 |
| per-period verdict (card rule) | mixed | mixed |

Data: `data/processed/H25-criticality-dial/r1b/G10/`.

## Notes
- 2026-10-04 02:14 UTC: results filled by `analysis/write_period_folders.py --results` from `analysis/explore.py` (exploratory round 1). Prediction block above unchanged from the --predict pass.
- Reading notes (card, Results): the content dial's upper bounds are wide, so check (i) fails in every period; fixed-effect means are pulled toward days with 3–4 talkers, whose bootstrap SEs are small (compare the random-effects mean); per-pair correlation, not g, is the size-free quantity (card, post hoc PH1).
