# H92 × G36: Interact with other AI agents outside the Village! (2026-03-25 → 2026-03-27, forecast target days)

**Verdict:** mixed
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
| content_bge | 2 | 12 | +0.325 | -0.062 | -0.027 | -0.186 | E1_mean |
| content_gte | 2 | 12 | +0.311 | +0.026 | +0.042 | -0.017 | E1_mean |
| content_bge_style_resid_period | 2 | 12 | +0.339 | -0.058 | -0.040 | -0.192 | E1_mean |
| content_gte_style_resid_period | 2 | 12 | +0.266 | -0.007 | -0.020 | -0.050 | E1_mean |
| talk | 2 | 8 | +0.479 | -0.000 | +0.050 | +0.050 | E4_lwcc |
| act | 2 | 12 | +0.500 | +0.068 | +0.156 | +0.084 | E5_clip |

Data: `data/processed/H92-rmt-cleaned-forecast/periods.parquet`, `forecasts.parquet`. CIs are in the shared estimates table.

## Scorecard (period-specific axes)
- C (adequacy): the forecast comparison against the strongest rival on this period, as tabulated.
- H (comparative): E5 vs E3/E4 here.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
