# H52 × G10: humans as loud agents, replication (2025-08-18 → 2025-08-22)

**Verdict:** descriptive — reply 0.020, content -0.022
**Role:** replication
**Period:** regime I · non-holdout days only · human messages 19 on 5 days (133 message × recipient rows; goal kickoffs excluded) · agent rows 7438. Not powered (fewer than 300 matched human content rows or fewer than 6 days with human messages): read as a phase-diagram point, not a test.

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
| content (DiD χ) | -0.022 [-0.050, 0.004] (n 97, 15 msgs; matched 0.97) | -0.033 | -0.009 | -0.019 [-0.038, 0.025] | inconclusive |
| reply (parent) | 0.020 [-0.009, 0.054] (n 126, 19 msgs; matched 0.88) | 0.063 | 0.016 | 0.094 [0.074, 0.136] | equivalent |
| activity (min / 30 min, BC) | 0.15 [-0.98, 2.01] (n 99, 17 msgs; matched 0.76) | 0.04 | 26.01 | 0.77 [0.10, 1.72] | inconclusive |
| stance (soft) | 0.150 [-0.202, 0.514] (n 9, 7 msgs; matched 1.00) | 0.110 | 0.570 | -0.143 [-0.376, 0.011] | inconclusive |

Robustness (content, human): H30 orthogonalized χ 0.013 [-0.012, 0.034]; gte-modernbert 0.006 [-0.026, 0.038]; joint per-call deconvolution -0.009 [-0.041, 0.022]; H29 boundary design: too few human rows at the boundary. Regime-I content premia carry a synthetic null bias of about −0.024 (Amendment A1). Bootstrap clusters: message.

Data: `data/processed/H52-humans-loud-agents/G10/` (`rows.parquet`, `boundary.parquet`, `results.json`).

## Scorecard (period-specific axes)
- C: premium vs the matched-agent null and the placebo-class null (see `results.json`).
- G: agents' own naming effect reproduces H29/H30's addressed > broadcast where powered.

## Notes
- Written by `analysis/write_period_folders.py` (replication layer; templated by design).
