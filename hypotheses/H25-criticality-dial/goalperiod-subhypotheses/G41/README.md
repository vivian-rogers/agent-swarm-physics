# H25 × G41: Perform novel research! (2026-05-11 → 2026-05-15)

**Verdict:** failed
**Verdict (1b):** failed (round 1: failed; corrected table, same rule)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode I · 15 agents at start · 5 non-holdout days · 4.0 h/day (empirical).

## Why this period
One day-resolved stretch of the dial. Every non-holdout period gets the same daily dial (activity, talk, content) so periods can be compared through their fitted values. Reference values: H19 g_eq active 0.13, talk 0.08; H03 n̂ TALK 0.31.

## Prediction
*Written 2026-10-04 02:00 UTC, before running the dial on this period.* The card's predictions (P1–P7) as they apply here; H19's per-period values were known (disclosed in the card).
- **Activity dial** (stalls masked): daily values mostly in [−0.1, 0.4]; period mean near H19's g_eq active = 0.13 (± 0.07), lowered by 0–0.05 where stalls are masked: predicted range [0.05, 0.16].
- **Talk dial** (stalls kept): period mean within ± max(0.05, 2 SE) of H19's g_eq talk = 0.08.
- **Content dial** (F2): period median in [0.15, 0.6], above the activity dial (HH108; credence 0.55), and below H01's 0.74.
- **Subcritical:** every day's upper 90% bound < 0.8 in all channels.
- Regime III: activity dial expected higher than in regime I (H19's +0.11), talk dial lower.
- **Verdict rule** (card): *supported* if (i) all days subcritical in all estimable channels, (ii) the activity and talk dials with stalls kept reproduce H19's g_eq within max(0.05, 2 SE), and (iii) the period's median content dial (F2) is < 0.74; *failed* if any day has a lower 90% bound > 0.8 in any channel, or (ii) and (iii) both fail; *mixed* otherwise.
- *Against:* a confidently near-critical day; a period mean far from H19's estimator (implementation or stall effect larger than expected); content at or above 0.74 after field removal.
- Starts with the 05-11 room split (NE42).

## Result
| Dial | days | fixed-effect mean ± SE | random-effects mean ± SE | median | between-day I² (Cochran p) | share of days with upper bound < 0.8 | max lower bound |
| --- | --- | --- | --- | --- | --- | --- | --- |
| activity (stalls masked) | 5 | 0.074 ± 0.078 | 0.067 ± 0.098 | 0.170 | 0.36 (p 0.181) | 1.00 | 0.04 |
| activity (stalls kept) | 5 | 0.089 ± 0.078 | 0.086 ± 0.094 | 0.170 | 0.30 (p 0.221) | 1.00 | -0.00 |
| talk (stalls masked) | 4 | 0.108 ± 0.052 | 0.108 ± 0.052 | 0.093 | 0.00 (p 0.829) | 1.00 | 0.00 |
| talk (stalls kept) | 4 | 0.105 ± 0.054 | 0.105 ± 0.054 | 0.093 | 0.00 (p 0.840) | 1.00 | -0.02 |
| content F1 | 5 | 0.786 ± 0.035 | 0.786 ± 0.035 | 0.793 | 0.00 (p 0.663) | 0.00 | 0.81 |
| content F2 (primary) | 5 | 0.791 ± 0.033 | 0.791 ± 0.033 | 0.802 | 0.00 (p 0.763) | 0.00 | 0.82 |
| content F3 | 5 | 0.789 ± 0.036 | 0.789 ± 0.036 | 0.787 | 0.00 (p 0.774) | 0.00 | 0.80 |

| Check | Observed | Outcome |
| --- | --- | --- |
| (i) every day subcritical (upper 90% bound < 0.8, all channels) | no | fail |
| (ii) stalls-kept dials vs H19 g_eq (active 0.13, talk 0.08) | activity 0.09, talk 0.10 | pass |
| (iii) content F2 median < 0.74 | 0.80 | fail |
| any day confidently near-critical (lower bound > 0.8) | yes | – |


Stall minutes masked: 0.4% of the day on average. T/T_c = 1/g for the activity dial (stalls masked): 13.57; amplification 1/(1 − g) = 1.08.

![daily dial](figures/G41_dial.png)  
Data: `data/processed/H25-criticality-dial/G41/dial_daily.parquet`, `results.json`.

## Scorecard (period-specific axes)
- **C (adequacy):** day-level null band (circular shifts): share of days with activity dial above its null 95th percentile = 0.60.
- **D (unfitted):** H19 agreement (ii) passes; H03 n̂ TALK 0.31 vs talk dial 0.11 (cross-period test in the card).
- **G (known structure):** see the card's event tests (regime switch, goal changes) where this period is involved.

## Round 1b (improved data, 2026-10-04)
Same pipeline (`analysis/explore.py --data-version fixed`) on DQ8's `activity_bins_fixed` and the shared `outages_fixed` stall table (round 1's activity table dropped about half of all events). Predictions and verdict rule unchanged; check (ii) now compares with H19's estimator recomputed on the fixed table (round-1 H19 values are stale). The DQ8 row trims each day to the window in which all agents are between their first and last active minute before the block-shift null is drawn (whole-day block-shift nulls reject 28–34% of independent swarms).

| Quantity | Round 1 (old table) | Round 1b (fixed table) |
| --- | --- | --- |
| activity dial, stalls masked (fixed-effect mean; median) | 0.07; 0.17 | 0.21; 0.25 |
| activity dial, stalls kept vs H19 g_eq | 0.09 vs 0.13 | 0.23 vs 0.30 (H19 estimator on the fixed table) |
| talk dial, stalls masked (fixed-effect; random-effects) | 0.11; 0.11 | 0.18; 0.18 |
| talk dial, stalls kept vs H19 g_eq talk | 0.10 vs 0.08 | 0.18 vs 0.20 |
| days above the block-shift null q95: activity (round-1 design → **DQ8 trim**) | 3/5 | 4/5 → 0/5 |
| median activity dial with the DQ8 trim | – | -0.06 |
| content dial F2 median (inputs unchanged) | 0.80 | 0.80 |
| per-period verdict (card rule) | failed | failed |

Data: `data/processed/H25-criticality-dial/r1b/G41/`.

## Notes
- 2026-10-04 02:14 UTC: results filled by `analysis/write_period_folders.py --results` from `analysis/explore.py` (exploratory round 1). Prediction block above unchanged from the --predict pass.
- Reading notes (card, Results): the content dial's upper bounds are wide, so check (i) fails in every period; fixed-effect means are pulled toward days with 3–4 talkers, whose bootstrap SEs are small (compare the random-effects mean); per-pair correlation, not g, is the size-free quantity (card, post hoc PH1).
