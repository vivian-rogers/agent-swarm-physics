# H25 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 2026-03-20)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime II · mode C · 13 agents at start · 5 non-holdout days · 4.0 h/day (empirical).

## Why this period
One day-resolved stretch of the dial. Every non-holdout period gets the same daily dial (activity, talk, content) so periods can be compared through their fitted values. Reference values: H19 g_eq active 0.10, talk 0.17; H03 n̂ TALK 0.08.

## Prediction
*Written 2026-10-04 02:00 UTC, before running the dial on this period.* The card's predictions (P1–P7) as they apply here; H19's per-period values were known (disclosed in the card).
- **Activity dial** (stalls masked): daily values mostly in [−0.1, 0.4]; period mean near H19's g_eq active = 0.10 (± 0.04), lowered by 0–0.05 where stalls are masked: predicted range [0.02, 0.13].
- **Talk dial** (stalls kept): period mean within ± max(0.05, 2 SE) of H19's g_eq talk = 0.17.
- **Content dial** (F2): period median in [0.15, 0.6], above the activity dial (HH108; credence 0.55), and below H01's 0.74.
- **Subcritical:** every day's upper 90% bound < 0.8 in all channels.
- Regime I/II: activity dial expected lower than in regime III; talk dial comparatively higher (H19).
- **Verdict rule** (card): *supported* if (i) all days subcritical in all estimable channels, (ii) the activity and talk dials with stalls kept reproduce H19's g_eq within max(0.05, 2 SE), and (iii) the period's median content dial (F2) is < 0.74; *failed* if any day has a lower 90% bound > 0.8 in any channel, or (ii) and (iii) both fail; *mixed* otherwise.
- *Against:* a confidently near-critical day; a period mean far from H19's estimator (implementation or stall effect larger than expected); content at or above 0.74 after field removal.

## Result
| Dial | days | fixed-effect mean ± SE | random-effects mean ± SE | median | between-day I² (Cochran p) | share of days with upper bound < 0.8 | max lower bound |
| --- | --- | --- | --- | --- | --- | --- | --- |
| activity (stalls masked) | 5 | 0.067 ± 0.056 | 0.067 ± 0.056 | 0.054 | 0.00 (p 0.589) | 1.00 | -0.04 |
| activity (stalls kept) | 5 | 0.092 ± 0.057 | 0.092 ± 0.057 | 0.054 | 0.00 (p 0.825) | 1.00 | -0.02 |
| talk (stalls masked) | 4 | 0.212 ± 0.061 | 0.212 ± 0.061 | 0.177 | 0.00 (p 0.596) | 1.00 | 0.13 |
| talk (stalls kept) | 4 | 0.217 ± 0.059 | 0.217 ± 0.059 | 0.177 | 0.00 (p 0.553) | 1.00 | 0.16 |
| content F1 | 5 | 0.834 ± 0.023 | 0.832 ± 0.025 | 0.848 | 0.12 (p 0.334) | 0.00 | 0.86 |
| content F2 (primary) | 5 | 0.832 ± 0.023 | 0.832 ± 0.023 | 0.839 | 0.00 (p 0.507) | 0.00 | 0.84 |
| content F3 | 5 | 0.831 ± 0.026 | 0.831 ± 0.026 | 0.835 | 0.00 (p 0.522) | 0.00 | 0.84 |

| Check | Observed | Outcome |
| --- | --- | --- |
| (i) every day subcritical (upper 90% bound < 0.8, all channels) | no | fail |
| (ii) stalls-kept dials vs H19 g_eq (active 0.10, talk 0.17) | activity 0.09, talk 0.22 | pass |
| (iii) content F2 median < 0.74 | 0.84 | fail |
| any day confidently near-critical (lower bound > 0.8) | yes | – |


Stall minutes masked: 0.4% of the day on average. T/T_c = 1/g for the activity dial (stalls masked): 14.96; amplification 1/(1 − g) = 1.07.

![daily dial](figures/G35_dial.png)  
Data: `data/processed/H25-criticality-dial/G35/dial_daily.parquet`, `results.json`.

## Scorecard (period-specific axes)
- **C (adequacy):** day-level null band (circular shifts): share of days with activity dial above its null 95th percentile = 0.40.
- **D (unfitted):** H19 agreement (ii) passes; H03 n̂ TALK 0.08 vs talk dial 0.21 (cross-period test in the card).
- **G (known structure):** see the card's event tests (regime switch, goal changes) where this period is involved.

## Notes
- 2026-10-04 02:14 UTC: results filled by `analysis/write_period_folders.py --results` from `analysis/explore.py` (exploratory round 1). Prediction block above unchanged from the --predict pass.
- Reading notes (card, Results): the content dial's upper bounds are wide, so check (i) fails in every period; fixed-effect means are pulled toward days with 3–4 talkers, whose bootstrap SEs are small (compare the random-effects mean); per-pair correlation, not g, is the size-free quantity (card, post hoc PH1).
