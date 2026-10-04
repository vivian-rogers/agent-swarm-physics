# H52 × G18: humans as loud agents, replication (2025-10-20 → 2025-10-31)

**Verdict:** descriptive — reply 0.061, content -0.061
**Role:** replication
**Period:** regime I · non-holdout days only · human messages 21 on 8 days (163 message × recipient rows; goal kickoffs excluded) · agent rows 46701. Not powered (fewer than 300 matched human content rows or fewer than 6 days with human messages): read as a phase-diagram point, not a test.

## Why this period
Replication layer: the common estimator on every non-holdout goal period with ≥ 100 non-kickoff human (message, recipient) rows on ≥ 3 days. Regime I: the 2025 public chat, where many human viewers wrote to the agents.

## Prediction
*Templated replication prediction, copied from the card (written 2026-10-04 ~06:10 UTC, before any outcome statistic).*
- H52: the matched human premium is equivalent to 0 in content and activity; reply and stance premia reported.
- Author's expectation (card P1–P4): content premium > 0 in regime III and ≤ 0 in regime I; reply premium > 0; activity premium CI includes 0; stance premium > 0.
- Counts against H52: a content or reply premium whose CI lies beyond the margin (δ_con = 0.5 × pooled agent naming effect; δ_rep likewise).

## Result
Margins: δ_con 0.0073, δ_rep 0.0637, δ_act 0.5 min, δ_st 0.05. Premium = CEM ATT of human rows vs agent rows in the same salience stratum (Amendment A1 estimators). In the verdict line, * marks a 95% CI that excludes 0.

| Outcome | Human premium [95% CI] | Naive human − agent | Matched agent mean | Agent naming effect | Verdict |
| --- | --- | --- | --- | --- | --- |
| content (DiD χ) | -0.061 [-0.093, 0.015] (n 110, 15 msgs; matched 0.99) | -0.037 | 0.029 | -0.020 [-0.041, 0.006] | inconclusive |
| reply (parent) | 0.061 [-0.003, 0.181] (n 162, 21 msgs; matched 0.87) | 0.066 | 0.024 | 0.019 [0.001, 0.033] | inconclusive |
| activity (min / 30 min, BC) | 1.22 [-0.50, 2.77] (n 116, 19 msgs; matched 0.82) | 1.15 | 21.67 | 0.14 [-0.63, 0.99] | inconclusive |
| stance (soft) | 0.151 [-0.116, 0.364] (n 19, 11 msgs; matched 1.00) | 0.142 | 0.626 | -0.069 [-0.119, 0.003] | inconclusive |

Robustness (content, human): H30 orthogonalized χ -0.062 [-0.101, -0.001]; gte-modernbert -0.049 [-0.063, -0.033]; joint per-call deconvolution -0.037 [-0.063, 0.021]; H29 boundary design: too few human rows at the boundary. Regime-I content premia carry a synthetic null bias of about −0.024 (Amendment A1). Bootstrap clusters: day.

Data: `data/processed/H52-humans-loud-agents/G18/` (`rows.parquet`, `boundary.parquet`, `results.json`).

## Scorecard (period-specific axes)
- C: premium vs the matched-agent null and the placebo-class null (see `results.json`).
- G: agents' own naming effect reproduces H29/H30's addressed > broadcast where powered.

## Notes
- Written by `analysis/write_period_folders.py` (replication layer; templated by design).
