# H52 × G23: humans as loud agents, replication (2025-12-15 → 2025-12-19)

**Verdict:** mixed — reply 0.010, content 0.001
**Role:** replication
**Period:** regime I · non-holdout days only · human messages 21 on 3 days (210 message × recipient rows; goal kickoffs excluded) · agent rows 16004. Not powered (fewer than 300 matched human content rows or fewer than 6 days with human messages): read as a phase-diagram point, not a test.

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
| content (DiD χ) | 0.001 [-0.044, 0.043] (n 86, 21 msgs; matched 1.00) | -0.001 | 0.001 | -0.015 [-0.022, -0.006] | inconclusive |
| reply (parent) | 0.010 [-0.013, 0.035] (n 210, 21 msgs; matched 1.00) | 0.009 | 0.014 | 0.109 [0.071, 0.140] | equivalent |
| activity (min / 30 min, BC) | -0.22 [-0.78, 0.49] (n 210, 21 msgs; matched 0.95) | -0.32 | 25.74 | 0.06 [-0.21, 0.32] | inconclusive |
| stance (soft) | 0.400 [0.149, 0.587] (n 6, 5 msgs; matched 1.00) | 0.412 | 0.425 | 0.006 [-0.077, 0.102] | premium+ |

Robustness (content, human): H30 orthogonalized χ 0.028 [0.000, 0.057]; gte-modernbert -0.013 [-0.044, 0.017]; joint per-call deconvolution -0.004 [-0.058, 0.044]; H29 boundary design: too few human rows at the boundary. Regime-I content premia carry a synthetic null bias of about −0.024 (Amendment A1). Bootstrap clusters: message.

Data: `data/processed/H52-humans-loud-agents/G23/` (`rows.parquet`, `boundary.parquet`, `results.json`).

## Scorecard (period-specific axes)
- C: premium vs the matched-agent null and the placebo-class null (see `results.json`).
- G: agents' own naming effect reproduces H29/H30's addressed > broadcast where powered.

## Notes
- Written by `analysis/write_period_folders.py` (replication layer; templated by design).
