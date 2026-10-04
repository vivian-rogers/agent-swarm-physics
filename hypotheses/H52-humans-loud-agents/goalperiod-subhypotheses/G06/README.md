# H52 × G06: humans as loud agents, replication (2025-06-26 → 2025-07-15)

**Verdict:** mixed — reply 0.009, content 0.003
**Role:** replication
**Period:** regime I · non-holdout days only · human messages 439 on 12 days (1754 message × recipient rows; goal kickoffs excluded) · agent rows 6677. Powered (pre-registered rule).

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
| content (DiD χ) | 0.003 [-0.009, 0.027] (n 1610, 424 msgs; matched 0.98) | 0.001 | 0.002 | -0.018 [-0.036, -0.003] | inconclusive |
| reply (parent) | 0.009 [-0.002, 0.040] (n 1692, 439 msgs; matched 0.96) | -0.020 | 0.020 | 0.156 [0.092, 0.239] | equivalent |
| activity (min / 30 min, BC) | 0.19 [-0.58, 0.57] (n 1412, 358 msgs; matched 0.83) | -0.03 | 26.54 | -0.35 [-1.74, 0.83] | inconclusive |
| stance (soft) | 0.269 [0.113, 0.477] (n 64, 61 msgs; matched 1.00) | 0.264 | 0.456 | -0.116 [-0.324, 0.054] | premium+ |

Robustness (content, human): H30 orthogonalized χ 0.008 [-0.010, 0.040]; gte-modernbert 0.010 [-0.001, 0.022]; joint per-call deconvolution 0.005 [-0.011, 0.029]; H29 boundary design, human − agent jump (unnamed) 0.002 [-0.031, 0.069]. Regime-I content premia carry a synthetic null bias of about −0.024 (Amendment A1). Bootstrap clusters: day.

Data: `data/processed/H52-humans-loud-agents/G06/` (`rows.parquet`, `boundary.parquet`, `results.json`).

## Scorecard (period-specific axes)
- C: premium vs the matched-agent null and the placebo-class null (see `results.json`).
- G: agents' own naming effect reproduces H29/H30's addressed > broadcast where powered.

## Notes
- Written by `analysis/write_period_folders.py` (replication layer; templated by design).
