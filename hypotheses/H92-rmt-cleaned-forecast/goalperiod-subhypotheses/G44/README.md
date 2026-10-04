# H92 × G44: Finetune your leader! (2026-05-27 → 2026-05-29, forecast target days)

**Verdict:** supported
**Role:** replication (exploratory)
**Period:** regime III · forecasts within `period_units` units only (no forecast crosses a step change).

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
| content_bge | 2 | 16 | +0.156 | +0.025 | +0.038 | +0.367 | E6_clip_mp |
| content_gte | 2 | 16 | +0.195 | +0.026 | +0.039 | +0.437 | E5_clip |
| content_bge_style_resid_period | 2 | 16 | -0.044 | -0.164 | -0.181 | +0.116 | E6_clip_mp |
| content_gte_style_resid_period | 2 | 16 | +0.262 | +0.127 | +0.107 | +0.428 | E5_clip |
| talk | 1 | 10 | +0.640 | -0.000 | +0.026 | -0.044 | E1_mean |
| act | 1 | 15 | +0.527 | +0.039 | +0.055 | -0.034 | E1_mean |

Data: `data/processed/H92-rmt-cleaned-forecast/periods.parquet`, `forecasts.parquet`. CIs are in the shared estimates table.

## Scorecard (period-specific axes)
- C (adequacy): the forecast comparison against the strongest rival on this period, as tabulated.
- H (comparative): E5 vs E3/E4 here.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
