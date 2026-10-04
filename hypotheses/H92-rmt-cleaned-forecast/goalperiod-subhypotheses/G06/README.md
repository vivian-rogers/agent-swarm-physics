# H92 × G06: Create your own merch store. Whichever agent's store makes the most profit wins! (2025-06-27 → 2025-07-15, forecast target days)

**Verdict:** supported
**Role:** replication (exploratory)
**Period:** regime I · forecasts within `period_units` units only (no forecast crosses a step change).

## Why this period
A replication point for the common estimator (layer 1). Every eligible goal period gets the same forecast comparison, so periods are comparable points, not independent tests.

## Prediction
*Templated from the card's replication rule, written 2026-10-04 ~20:15 UTC before any real-data forecast.*
- RMT clipping at the calibrated edge (E5) has the lowest mean next-day MSE among raw (E2), Ledoit–Wolf identity (E3), Ledoit–Wolf constant correlation (E4) and E5, in the content channel with both embedding models.
- *Supported* if that holds in both models; *failed* if E5's mean MSE exceeds raw's in both; *mixed* otherwise; *descriptive* with < 2 target days.

## Result
Relative gain of E5 over each rival, r = 1 − MSE_E5/MSE_rival, mean over target days (positive = clipping forecasts better). Expanding training window.

| Channel | target days | median N | vs raw | vs LW identity | vs LW const. corr. | vs mean field | best estimator |
| --- | --- | --- | --- | --- | --- | --- | --- |
| content_bge | 12 | 4 | +0.191 | -0.002 | +0.069 | -0.039 | E1_mean |
| content_gte | 12 | 4 | -0.068 | -0.316 | -0.191 | -0.003 | E6_clip_mp |
| content_bge_style_resid_period | 12 | 4 | +0.133 | -0.035 | +0.028 | -0.148 | E1_mean |
| content_gte_style_resid_period | 12 | 4 | +0.031 | -0.167 | -0.043 | -0.005 | E6_clip_mp |
| talk | 13 | 4 | +0.133 | -0.138 | -0.029 | +0.025 | E3_lwi |
| act | 2 | 4 | -0.001 | -0.019 | -0.002 | +0.004 | E3_lwi |

**Correction (2026-10-04, blind-rater check).** The verdict stays **supported**. The rule compares *period-mean MSE*, and E5 has the lowest mean MSE among E2–E5 in both models. bge: E5 0.0283, E3 0.0297, E4 0.0311, E2 0.0362. gte: E5 0.0345, E3 0.0364, E4 0.0378, E2 0.0415 (`periods.parquet`, `mse_*`). The table above reports a different statistic: the *mean of per-day relative gains* r = 1 − MSE_E5/MSE_rival. In gte these gains are negative (vs raw −0.07, vs LW identity −0.32, vs LW constant correlation −0.19). E5 wins on the high-MSE days that dominate the mean MSE, and it loses on most low-MSE days. Under the per-day-gain reading this period would be mixed. So G06's "supported" depends on how days are aggregated. It is not a robust point.

Data: `data/processed/H92-rmt-cleaned-forecast/periods.parquet`, `forecasts.parquet`. CIs are in the shared estimates table.

## Scorecard (period-specific axes)
- C (adequacy): the forecast comparison against the strongest rival on this period, as tabulated.
- H (comparative): E5 vs E3/E4 here.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
