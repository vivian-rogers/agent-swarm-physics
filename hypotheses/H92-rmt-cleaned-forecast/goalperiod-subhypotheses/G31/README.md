# H92 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-17 → 2026-02-17, forecast target days)

**Verdict:** descriptive
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
| content_bge | 1 | 11 | +0.110 | +0.213 | +0.073 | +0.161 | E5_clip |
| content_gte | 1 | 11 | +0.170 | +0.194 | +0.021 | -0.101 | E1_mean |
| content_bge_style_resid_period | 1 | 11 | +0.086 | +0.204 | +0.063 | +0.156 | E5_clip |
| content_gte_style_resid_period | 1 | 11 | +0.127 | +0.162 | -0.032 | -0.122 | E1_mean |
| talk | 1 | 11 | +0.525 | -0.000 | +0.101 | +0.101 | E3_lwi |
| act | 1 | 11 | +0.647 | +0.000 | +0.220 | -0.027 | E1_mean |

Data: `data/processed/H92-rmt-cleaned-forecast/periods.parquet`, `forecasts.parquet`. CIs are in the shared estimates table.

## Scorecard (period-specific axes)
- C (adequacy): the forecast comparison against the strongest rival on this period, as tabulated.
- H (comparative): E5 vs E3/E4 here.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
