# H92 × G12: Form two teams and debate each other, while one agent judges. Choose your teammates wisely! (2025-09-02 → 2025-09-04, forecast target days)

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
| content_bge | 3 | 7 | -0.694 | -0.752 | -0.710 | +0.566 | E4_lwcc |
| content_gte | 3 | 7 | -0.548 | -0.624 | -0.554 | +0.543 | E4_lwcc |
| content_bge_style_resid_period | 3 | 7 | -0.487 | -0.533 | -0.490 | +0.564 | E4_lwcc |
| content_gte_style_resid_period | 3 | 7 | -0.306 | -0.364 | -0.332 | +0.527 | E4_lwcc |
| talk | 3 | 7 | +0.062 | -0.099 | +0.113 | +0.132 | E3_lwi |
| act | 3 | 7 | +0.197 | -0.012 | -0.117 | -0.117 | E4_lwcc |

Data: `data/processed/H92-rmt-cleaned-forecast/periods.parquet`, `forecasts.parquet`. CIs are in the shared estimates table.

## Scorecard (period-specific axes)
- C (adequacy): the forecast comparison against the strongest rival on this period, as tabulated.
- H (comparative): E5 vs E3/E4 here.

## Notes
- Templated folder (replication layer), written by `analysis/write_period_folders.py`.
