# H52 × G16: humans as loud agents, replication (2025-10-06 → 2025-10-10)

**Verdict:** mixed — reply 0.094*, content -0.013
**Role:** replication
**Period:** regime I · non-holdout days only · human messages 26 on 5 days (182 message × recipient rows; goal kickoffs excluded) · agent rows 11548. Not powered (fewer than 300 matched human content rows or fewer than 6 days with human messages): read as a phase-diagram point, not a test.

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
| content (DiD χ) | -0.013 [-0.037, 0.007] (n 161, 23 msgs; matched 0.99) | -0.007 | 0.007 | -0.010 [-0.026, 0.002] | inconclusive |
| reply (parent) | 0.094 [0.030, 0.146] (n 182, 26 msgs; matched 0.98) | 0.080 | 0.007 | 0.065 [0.022, 0.131] | premium+ |
| activity (min / 30 min, BC) | 1.72 [0.61, 3.13] (n 168, 26 msgs; matched 0.88) | 0.93 | 22.37 | -0.74 [-2.12, 0.54] | premium+ |
| stance (soft) | 0.174 [0.046, 0.341] (n 19, 12 msgs; matched 1.00) | 0.163 | 0.629 | -0.126 [-0.204, -0.003] | premium+ |

Robustness (content, human): H30 orthogonalized χ -0.023 [-0.039, -0.007]; gte-modernbert -0.009 [-0.026, 0.013]; joint per-call deconvolution -0.002 [-0.024, 0.019]; H29 boundary design: too few human rows at the boundary. Regime-I content premia carry a synthetic null bias of about −0.024 (Amendment A1). Bootstrap clusters: message.

Data: `data/processed/H52-humans-loud-agents/G16/` (`rows.parquet`, `boundary.parquet`, `results.json`).

## Scorecard (period-specific axes)
- C: premium vs the matched-agent null and the placebo-class null (see `results.json`).
- G: agents' own naming effect reproduces H29/H30's addressed > broadcast where powered.

## Notes
- Written by `analysis/write_period_folders.py` (replication layer; templated by design).
