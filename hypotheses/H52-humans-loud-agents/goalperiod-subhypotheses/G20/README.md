# H52 × G20: humans as loud agents, replication (2025-11-17 → 2025-11-28)

**Verdict:** mixed — reply 0.085, content -0.028*
**Role:** replication
**Period:** regime I · non-holdout days only · human messages 14 on 8 days (122 message × recipient rows; goal kickoffs excluded) · agent rows 37931. Not powered (fewer than 300 matched human content rows or fewer than 6 days with human messages): read as a phase-diagram point, not a test.

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
| content (DiD χ) | -0.028 [-0.076, -0.006] (n 88, 11 msgs; matched 1.00) | -0.028 | 0.004 | -0.008 [-0.017, -0.001] | premium- |
| reply (parent) | 0.085 [-0.012, 0.237] (n 122, 14 msgs; matched 0.87) | 0.083 | 0.009 | 0.035 [0.017, 0.061] | inconclusive |
| activity (min / 30 min, BC) | -0.43 [-1.28, 0.36] (n 99, 14 msgs; matched 0.90) | -0.63 | 23.43 | 0.43 [-0.20, 0.90] | inconclusive |
| stance (soft) | 0.234 [0.104, 0.334] (n 14, 5 msgs; matched 1.00) | 0.269 | 0.635 | -0.074 [-0.131, -0.008] | premium+ |

Robustness (content, human): H30 orthogonalized χ -0.012 [-0.040, 0.001]; gte-modernbert -0.026 [-0.060, 0.001]; joint per-call deconvolution -0.030 [-0.080, -0.008]; H29 boundary design: too few human rows at the boundary. Regime-I content premia carry a synthetic null bias of about −0.024 (Amendment A1). Bootstrap clusters: day.

Data: `data/processed/H52-humans-loud-agents/G20/` (`rows.parquet`, `boundary.parquet`, `results.json`).

## Scorecard (period-specific axes)
- C: premium vs the matched-agent null and the placebo-class null (see `results.json`).
- G: agents' own naming effect reproduces H29/H30's addressed > broadcast where powered.

## Notes
- Written by `analysis/write_period_folders.py` (replication layer; templated by design).
