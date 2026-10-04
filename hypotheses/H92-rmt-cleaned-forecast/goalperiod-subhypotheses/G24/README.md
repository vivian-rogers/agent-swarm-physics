# H92 × G24: Do random acts of kindness! (2025-12-23 → 2025-12-26, forecast target days)

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
| content_bge | 4 | 10 | +0.216 | +0.072 | +0.096 | -0.072 | E1_mean |
| content_gte | 4 | 10 | +0.207 | +0.102 | +0.123 | +0.008 | E5_clip |
| content_bge_style_resid_period | 4 | 10 | +0.217 | +0.027 | +0.060 | -0.196 | E1_mean |
| content_gte_style_resid_period | 4 | 10 | +0.233 | +0.084 | +0.104 | -0.044 | E1_mean |
| talk | 4 | 10 | +0.245 | -0.027 | -0.025 | +0.008 | E4_lwcc |
| act | 4 | 8 | +0.295 | +0.060 | +0.053 | +0.081 | E5_clip |

Data: `data/processed/H92-rmt-cleaned-forecast/periods.parquet`, `forecasts.parquet`. CIs are in the shared estimates table.

## Scorecard (period-specific axes)
- C (adequacy): the forecast comparison against the strongest rival on this period, as tabulated.
- H (comparative): E5 vs E3/E4 here.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
