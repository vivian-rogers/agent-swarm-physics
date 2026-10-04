# H92 × G19: Create a popular daily puzzle game like Wordle (2025-11-04 → 2025-11-13, forecast target days)

**Verdict:** failed
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
| content_bge | 8 | 7 | -0.158 | -0.184 | -0.169 | +0.303 | E4_lwcc |
| content_gte | 8 | 7 | -0.129 | -0.137 | -0.139 | +0.256 | E3_lwi |
| content_bge_style_resid_period | 8 | 7 | -0.125 | -0.149 | -0.131 | +0.284 | E4_lwcc |
| content_gte_style_resid_period | 8 | 7 | -0.080 | -0.089 | -0.098 | +0.281 | E3_lwi |
| talk | 8 | 7 | +0.102 | +0.015 | +0.021 | +0.065 | E5_clip |
| act | 8 | 7 | +0.084 | -0.033 | -0.022 | -0.013 | E4_lwcc |

Data: `data/processed/H92-rmt-cleaned-forecast/periods.parquet`, `forecasts.parquet`. CIs are in the shared estimates table.

## Scorecard (period-specific axes)
- C (adequacy): the forecast comparison against the strongest rival on this period, as tabulated.
- H (comparative): E5 vs E3/E4 here.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
