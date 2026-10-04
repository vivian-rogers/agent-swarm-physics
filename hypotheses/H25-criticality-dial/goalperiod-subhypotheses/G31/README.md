# H25 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-20)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime I · mode F · 12 agents at start · 5 non-holdout days · 4.0 h/day (empirical).

## Why this period
One day-resolved stretch of the dial. Every non-holdout period gets the same daily dial (activity, talk, content) so periods can be compared through their fitted values. Reference values: H19 g_eq active 0.07, talk 0.13; H03 n̂ TALK 0.07.

## Prediction
*Written 2026-10-04 02:00 UTC, before running the dial on this period.* The card's predictions (P1–P7) as they apply here; H19's per-period values were known (disclosed in the card).
- **Activity dial** (stalls masked): daily values mostly in [−0.1, 0.4]; period mean near H19's g_eq active = 0.07 (± 0.07), lowered by 0–0.05 where stalls are masked: predicted range [-0.01, 0.10].
- **Talk dial** (stalls kept): period mean within ± max(0.05, 2 SE) of H19's g_eq talk = 0.13.
- **Content dial** (F2): period median in [0.15, 0.6], above the activity dial (HH108; credence 0.55), and below H01's 0.74.
- **Subcritical:** every day's upper 90% bound < 0.8 in all channels.
- Regime I/II: activity dial expected lower than in regime III; talk dial comparatively higher (H19).
- **Verdict rule** (card): *supported* if (i) all days subcritical in all estimable channels, (ii) the activity and talk dials with stalls kept reproduce H19's g_eq within max(0.05, 2 SE), and (iii) the period's median content dial (F2) is < 0.74; *failed* if any day has a lower 90% bound > 0.8 in any channel, or (ii) and (iii) both fail; *mixed* otherwise.
- *Against:* a confidently near-critical day; a period mean far from H19's estimator (implementation or stall effect larger than expected); content at or above 0.74 after field removal.

## Result
| Dial | days | fixed-effect mean ± SE | random-effects mean ± SE | median | between-day I² (Cochran p) | share of days with upper bound < 0.8 | max lower bound |
| --- | --- | --- | --- | --- | --- | --- | --- |
| activity (stalls masked) | 5 | 0.053 ± 0.063 | 0.053 ± 0.063 | 0.003 | 0.00 (p 0.427) | 1.00 | -0.01 |
| activity (stalls kept) | 5 | 0.048 ± 0.058 | 0.049 ± 0.061 | 0.003 | 0.08 (p 0.362) | 1.00 | -0.01 |
| talk (stalls masked) | 4 | 0.143 ± 0.057 | 0.143 ± 0.057 | 0.125 | 0.00 (p 0.969) | 1.00 | -0.00 |
| talk (stalls kept) | 4 | 0.141 ± 0.058 | 0.141 ± 0.058 | 0.125 | 0.00 (p 0.970) | 1.00 | -0.01 |
| content F1 | 5 | 0.818 ± 0.017 | 0.818 ± 0.017 | 0.807 | 0.00 (p 0.642) | 0.00 | 0.83 |
| content F2 (primary) | 5 | 0.811 ± 0.018 | 0.811 ± 0.018 | 0.807 | 0.00 (p 0.743) | 0.00 | 0.82 |
| content F3 | 5 | 0.813 ± 0.017 | 0.813 ± 0.017 | 0.782 | 0.00 (p 0.724) | 0.00 | 0.82 |

| Check | Observed | Outcome |
| --- | --- | --- |
| (i) every day subcritical (upper 90% bound < 0.8, all channels) | no | fail |
| (ii) stalls-kept dials vs H19 g_eq (active 0.07, talk 0.13) | activity 0.05, talk 0.14 | pass |
| (iii) content F2 median < 0.74 | 0.81 | fail |
| any day confidently near-critical (lower bound > 0.8) | yes | – |


Stall minutes masked: 0.0% of the day on average. T/T_c = 1/g for the activity dial (stalls masked): 18.86; amplification 1/(1 − g) = 1.06.

![daily dial](figures/G31_dial.png)  
Data: `data/processed/H25-criticality-dial/G31/dial_daily.parquet`, `results.json`.

## Scorecard (period-specific axes)
- **C (adequacy):** day-level null band (circular shifts): share of days with activity dial above its null 95th percentile = 0.20.
- **D (unfitted):** H19 agreement (ii) passes; H03 n̂ TALK 0.07 vs talk dial 0.14 (cross-period test in the card).
- **G (known structure):** see the card's event tests (regime switch, goal changes) where this period is involved.

## Notes
- 2026-10-04 02:14 UTC: results filled by `analysis/write_period_folders.py --results` from `analysis/explore.py` (exploratory round 1). Prediction block above unchanged from the --predict pass.
- Reading notes (card, Results): the content dial's upper bounds are wide, so check (i) fails in every period; fixed-effect means are pulled toward days with 3–4 talkers, whose bootstrap SEs are small (compare the random-effects mean); per-pair correlation, not g, is the size-free quantity (card, post hoc PH1).
