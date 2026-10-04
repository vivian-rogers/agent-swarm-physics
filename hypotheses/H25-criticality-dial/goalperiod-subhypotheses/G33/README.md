# H25 × G33: Discuss, debate, and act on your views about the recent Pentagon-AI company news (2026-03-02 → 2026-03-04)

**Verdict:** failed
**Verdict (1b):** failed (round 1: failed; corrected table, same rule)
**Role:** exploratory (round 1, non-holdout)
**Period:** regime II · mode C · 12 agents at start · 3 non-holdout days · 4.0 h/day (empirical).

## Why this period
One day-resolved stretch of the dial. Every non-holdout period gets the same daily dial (activity, talk, content) so periods can be compared through their fitted values. Reference values: H19 g_eq active 0.11, talk 0.07; H03 n̂ TALK 0.76.

## Prediction
*Written 2026-10-04 02:00 UTC, before running the dial on this period.* The card's predictions (P1–P7) as they apply here; H19's per-period values were known (disclosed in the card).
- **Activity dial** (stalls masked): daily values mostly in [−0.1, 0.4]; period mean near H19's g_eq active = 0.11 (± 0.06), lowered by 0–0.05 where stalls are masked: predicted range [0.03, 0.14].
- **Talk dial** (stalls kept): period mean within ± max(0.05, 2 SE) of H19's g_eq talk = 0.07.
- **Content dial** (F2): period median in [0.15, 0.6], above the activity dial (HH108; credence 0.55), and below H01's 0.74.
- **Subcritical:** every day's upper 90% bound < 0.8 in all channels.
- Regime I/II: activity dial expected lower than in regime III; talk dial comparatively higher (H19).
- **Verdict rule** (card): *supported* if (i) all days subcritical in all estimable channels, (ii) the activity and talk dials with stalls kept reproduce H19's g_eq within max(0.05, 2 SE), and (iii) the period's median content dial (F2) is < 0.74; *failed* if any day has a lower 90% bound > 0.8 in any channel, or (ii) and (iii) both fail; *mixed* otherwise.
- *Against:* a confidently near-critical day; a period mean far from H19's estimator (implementation or stall effect larger than expected); content at or above 0.74 after field removal.
- Only 3 day(s): low power; the period mean has a wide interval.

## Result
| Dial | days | fixed-effect mean ± SE | random-effects mean ± SE | median | between-day I² (Cochran p) | share of days with upper bound < 0.8 | max lower bound |
| --- | --- | --- | --- | --- | --- | --- | --- |
| activity (stalls masked) | 3 | 0.114 ± 0.064 | 0.114 ± 0.064 | 0.106 | 0.00 (p 0.982) | 1.00 | -0.04 |
| activity (stalls kept) | 3 | 0.114 ± 0.067 | 0.114 ± 0.067 | 0.106 | 0.00 (p 0.984) | 1.00 | -0.06 |
| talk (stalls masked) | 3 | 0.067 ± 0.071 | 0.067 ± 0.071 | 0.095 | 0.00 (p 0.817) | 1.00 | -0.09 |
| talk (stalls kept) | 3 | 0.065 ± 0.068 | 0.065 ± 0.068 | 0.095 | 0.00 (p 0.793) | 1.00 | -0.09 |
| content F1 | 3 | 0.862 ± 0.016 | 0.862 ± 0.016 | 0.858 | 0.00 (p 0.923) | 0.00 | 0.86 |
| content F2 (primary) | 3 | 0.865 ± 0.017 | 0.865 ± 0.017 | 0.865 | 0.00 (p 0.853) | 0.00 | 0.86 |
| content F3 | 3 | 0.864 ± 0.018 | 0.864 ± 0.018 | 0.864 | 0.00 (p 0.716) | 0.00 | 0.86 |

| Check | Observed | Outcome |
| --- | --- | --- |
| (i) every day subcritical (upper 90% bound < 0.8, all channels) | no | fail |
| (ii) stalls-kept dials vs H19 g_eq (active 0.11, talk 0.07) | activity 0.11, talk 0.07 | pass |
| (iii) content F2 median < 0.74 | 0.86 | fail |
| any day confidently near-critical (lower bound > 0.8) | yes | – |


Stall minutes masked: 0.0% of the day on average. T/T_c = 1/g for the activity dial (stalls masked): 8.75; amplification 1/(1 − g) = 1.13.

![daily dial](figures/G33_dial.png)  
Data: `data/processed/H25-criticality-dial/G33/dial_daily.parquet`, `results.json`.

## Scorecard (period-specific axes)
- **C (adequacy):** day-level null band (circular shifts): share of days with activity dial above its null 95th percentile = 0.00.
- **D (unfitted):** H19 agreement (ii) passes; H03 n̂ TALK 0.76 vs talk dial 0.07 (cross-period test in the card).
- **G (known structure):** see the card's event tests (regime switch, goal changes) where this period is involved.

## Round 1b (improved data, 2026-10-04)
Same pipeline (`analysis/explore.py --data-version fixed`) on DQ8's `activity_bins_fixed` and the shared `outages_fixed` stall table (round 1's activity table dropped about half of all events). Predictions and verdict rule unchanged; check (ii) now compares with H19's estimator recomputed on the fixed table (round-1 H19 values are stale). The DQ8 row trims each day to the window in which all agents are between their first and last active minute before the block-shift null is drawn (whole-day block-shift nulls reject 28–34% of independent swarms).

| Quantity | Round 1 (old table) | Round 1b (fixed table) |
| --- | --- | --- |
| activity dial, stalls masked (fixed-effect mean; median) | 0.11; 0.11 | 0.12; 0.14 |
| activity dial, stalls kept vs H19 g_eq | 0.11 vs 0.11 | 0.12 vs 0.13 (H19 estimator on the fixed table) |
| talk dial, stalls masked (fixed-effect; random-effects) | 0.07; 0.07 | 0.11; 0.11 |
| talk dial, stalls kept vs H19 g_eq talk | 0.07 vs 0.07 | 0.11 vs 0.11 |
| days above the block-shift null q95: activity (round-1 design → **DQ8 trim**) | 0/3 | 2/3 → 1/3 |
| median activity dial with the DQ8 trim | – | 0.07 |
| content dial F2 median (inputs unchanged) | 0.86 | 0.86 |
| per-period verdict (card rule) | failed | failed |

Data: `data/processed/H25-criticality-dial/r1b/G33/`.

## Notes
- 2026-10-04 02:14 UTC: results filled by `analysis/write_period_folders.py --results` from `analysis/explore.py` (exploratory round 1). Prediction block above unchanged from the --predict pass.
- Reading notes (card, Results): the content dial's upper bounds are wide, so check (i) fails in every period; fixed-effect means are pulled toward days with 3–4 talkers, whose bootstrap SEs are small (compare the random-effects mean); per-pair correlation, not g, is the size-free quantity (card, post hoc PH1).
