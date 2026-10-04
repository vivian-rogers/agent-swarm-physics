# H25 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-24)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III · mode C · 12 agents at start · 17 non-holdout days · 4.0 h/day (empirical).

## Why this period
One day-resolved stretch of the dial. Every non-holdout period gets the same daily dial (activity, talk, content) so periods can be compared through their fitted values. Reference values: H19 g_eq active 0.12, talk 0.04; H03 n̂ TALK 0.32.

## Prediction
*Written 2026-10-04 02:00 UTC, before running the dial on this period.* The card's predictions (P1–P7) as they apply here; H19's per-period values were known (disclosed in the card).
- **Activity dial** (stalls masked): daily values mostly in [−0.1, 0.4]; period mean near H19's g_eq active = 0.12 (± 0.02), lowered by 0–0.05 where stalls are masked: predicted range [0.04, 0.15].
- **Talk dial** (stalls kept): period mean within ± max(0.05, 2 SE) of H19's g_eq talk = 0.04.
- **Content dial** (F2): period median in [0.15, 0.6], above the activity dial (HH108; credence 0.55), and below H01's 0.74.
- **Subcritical:** every day's upper 90% bound < 0.8 in all channels.
- Regime III: activity dial expected higher than in regime I (H19's +0.11), talk dial lower.
- **Verdict rule** (card): *supported* if (i) all days subcritical in all estimable channels, (ii) the activity and talk dials with stalls kept reproduce H19's g_eq within max(0.05, 2 SE), and (iii) the period's median content dial (F2) is < 0.74; *failed* if any day has a lower 90% bound > 0.8 in any channel, or (ii) and (iii) both fail; *mixed* otherwise.
- *Against:* a confidently near-critical day; a period mean far from H19's estimator (implementation or stall effect larger than expected); content at or above 0.74 after field removal.
- Self-repetition loops (H12: 16–60% self near-copies): content dedupe matters here.

## Result
| Dial | days | fixed-effect mean ± SE | random-effects mean ± SE | median | between-day I² (Cochran p) | share of days with upper bound < 0.8 | max lower bound |
| --- | --- | --- | --- | --- | --- | --- | --- |
| activity (stalls masked) | 17 | 0.099 ± 0.036 | 0.099 ± 0.036 | 0.129 | 0.00 (p 0.984) | 1.00 | -0.05 |
| activity (stalls kept) | 17 | 0.118 ± 0.038 | 0.118 ± 0.038 | 0.148 | 0.00 (p 0.994) | 1.00 | -0.07 |
| talk (stalls masked) | 16 | -0.028 ± 0.022 | 0.017 ± 0.033 | 0.036 | 0.43 (p 0.036) | 1.00 | 0.02 |
| talk (stalls kept) | 16 | -0.034 ± 0.022 | 0.017 ± 0.034 | 0.039 | 0.44 (p 0.031) | 1.00 | 0.04 |
| content F1 | 15 | 0.757 ± 0.038 | 0.757 ± 0.038 | 0.697 | 0.00 (p 0.990) | 0.00 | 0.84 |
| content F2 (primary) | 15 | 0.780 ± 0.042 | 0.780 ± 0.042 | 0.712 | 0.00 (p 1.000) | 0.00 | 0.81 |
| content F3 | 16 | 0.785 ± 0.040 | 0.785 ± 0.040 | 0.653 | 0.00 (p 0.992) | 0.00 | 0.83 |

| Check | Observed | Outcome |
| --- | --- | --- |
| (i) every day subcritical (upper 90% bound < 0.8, all channels) | no | fail |
| (ii) stalls-kept dials vs H19 g_eq (active 0.12, talk 0.04) | activity 0.12, talk -0.03 | fail |
| (iii) content F2 median < 0.74 | 0.71 | pass |
| any day confidently near-critical (lower bound > 0.8) | yes | – |


Stall minutes masked: 2.9% of the day on average. T/T_c = 1/g for the activity dial (stalls masked): 10.13; amplification 1/(1 − g) = 1.11.

![daily dial](figures/G38_dial.png)  
Data: `data/processed/H25-criticality-dial/G38/dial_daily.parquet`, `results.json`.

## Scorecard (period-specific axes)
- **C (adequacy):** day-level null band (circular shifts): share of days with activity dial above its null 95th percentile = 0.47.
- **D (unfitted):** H19 agreement (ii) fails; H03 n̂ TALK 0.32 vs talk dial -0.03 (cross-period test in the card).
- **G (known structure):** see the card's event tests (regime switch, goal changes) where this period is involved.

## Notes
- 2026-10-04 02:14 UTC: results filled by `analysis/write_period_folders.py --results` from `analysis/explore.py` (exploratory round 1). Prediction block above unchanged from the --predict pass.
- Reading notes (card, Results): the content dial's upper bounds are wide, so check (i) fails in every period; fixed-effect means are pulled toward days with 3–4 talkers, whose bootstrap SEs are small (compare the random-effects mean); per-pair correlation, not g, is the size-free quantity (card, post hoc PH1).
