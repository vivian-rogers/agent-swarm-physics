# H92 × G33: Discuss, debate, and act on your views about the recent Pentagon-AI company news (2026-03-03 → 2026-03-04, forecast target days)

**Verdict:** supported
**Role:** replication (exploratory)
**Period:** regime II · forecasts within `period_units` units only (no forecast crosses a step change).

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
| content_bge | 2 | 11 | +0.146 | +0.165 | +0.040 | +0.215 | E5_clip |
| content_gte | 2 | 11 | +0.188 | +0.185 | +0.078 | +0.172 | E5_clip |
| content_bge_style_resid_period | 2 | 11 | +0.137 | +0.165 | +0.035 | +0.216 | E5_clip |
| content_gte_style_resid_period | 2 | 11 | +0.157 | +0.163 | +0.038 | +0.165 | E5_clip |
| talk | 2 | 10 | +0.542 | +0.000 | -0.092 | -0.093 | E1_mean |
| act | 2 | 11 | +0.415 | -0.034 | +0.039 | -0.257 | E1_mean |

Data: `data/processed/H92-rmt-cleaned-forecast/periods.parquet`, `forecasts.parquet`. CIs are in the shared estimates table.

## Scorecard (period-specific axes)
- C (adequacy): the forecast comparison against the strongest rival on this period, as tabulated.
- H (comparative): E5 vs E3/E4 here.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
