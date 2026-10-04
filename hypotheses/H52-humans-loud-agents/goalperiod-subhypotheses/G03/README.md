# H52 × G03: humans as loud agents, replication (2025-05-12 → 2025-05-14)

**Verdict:** mixed — reply 0.050*, content 0.025
**Role:** replication
**Period:** regime I · non-holdout days only · human messages 74 on 3 days (284 message × recipient rows; goal kickoffs excluded) · agent rows 4724. Not powered (fewer than 300 matched human content rows or fewer than 6 days with human messages): read as a phase-diagram point, not a test.

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
| content (DiD χ) | 0.025 [-0.001, 0.056] (n 270, 74 msgs; matched 1.00) | 0.049 | 0.012 | -0.005 [-0.041, 0.012] | inconclusive |
| reply (parent) | 0.050 [0.012, 0.090] (n 283, 74 msgs; matched 1.00) | -0.015 | 0.043 | 0.116 [0.067, 0.139] | premium+ |
| activity (min / 30 min, BC) | -0.58 [-1.28, 0.28] (n 265, 69 msgs; matched 0.83) | -1.23 | 24.50 | 0.49 [-2.39, 0.81] | inconclusive |
| stance (soft) | 0.059 [-0.136, 0.246] (n 26, 20 msgs; matched 1.00) | 0.073 | 0.628 | -0.038 [-0.093, 0.098] | inconclusive |

Robustness (content, human): H30 orthogonalized χ 0.012 [-0.009, 0.034]; gte-modernbert 0.026 [-0.002, 0.054]; joint per-call deconvolution 0.021 [-0.006, 0.044]; H29 boundary design, human − agent jump (unnamed) 0.030 [-0.035, 0.096]. Regime-I content premia carry a synthetic null bias of about −0.024 (Amendment A1). Bootstrap clusters: message.

Data: `data/processed/H52-humans-loud-agents/G03/` (`rows.parquet`, `boundary.parquet`, `results.json`).

## Scorecard (period-specific axes)
- C: premium vs the matched-agent null and the placebo-class null (see `results.json`).
- G: agents' own naming effect reproduces H29/H30's addressed > broadcast where powered.

## Notes
- Written by `analysis/write_period_folders.py` (replication layer; templated by design).
