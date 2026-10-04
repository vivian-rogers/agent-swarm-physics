# H52 × G05: humans as loud agents, replication (2025-06-19 → 2025-06-25)

**Verdict:** mixed — reply 0.030*, content 0.001
**Role:** replication
**Period:** regime I · non-holdout days only · human messages 1083 on 5 days (3703 message × recipient rows; goal kickoffs excluded) · agent rows 3593. Not powered (fewer than 300 matched human content rows or fewer than 6 days with human messages): read as a phase-diagram point, not a test.

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
| content (DiD χ) | 0.001 [-0.024, 0.036] (n 3311, 859 msgs; matched 0.98) | 0.026 | 0.007 | 0.001 [-0.032, 0.024] | inconclusive |
| reply (parent) | 0.030 [0.020, 0.039] (n 3648, 1082 msgs; matched 0.94) | -0.037 | 0.016 | 0.251 [0.171, 0.354] | premium+ |
| activity (min / 30 min, BC) | -0.27 [-0.52, 0.08] (n 2657, 693 msgs; matched 0.57) | -0.06 | 27.32 | 0.16 [-0.24, 0.72] | inconclusive |
| stance (soft) | 0.053 [-0.061, 0.175] (n 174, 157 msgs; matched 1.00) | 0.033 | 0.550 | 0.051 [-0.024, 0.100] | inconclusive |

Robustness (content, human): H30 orthogonalized χ 0.006 [-0.008, 0.029]; gte-modernbert 0.012 [-0.019, 0.040]; joint per-call deconvolution -0.006 [-0.031, 0.025]; H29 boundary design, human − agent jump (unnamed) 0.091 [0.053, 0.151]. Regime-I content premia carry a synthetic null bias of about −0.024 (Amendment A1). Bootstrap clusters: message.

Data: `data/processed/H52-humans-loud-agents/G05/` (`rows.parquet`, `boundary.parquet`, `results.json`).

## Scorecard (period-specific axes)
- C: premium vs the matched-agent null and the placebo-class null (see `results.json`).
- G: agents' own naming effect reproduces H29/H30's addressed > broadcast where powered.

## Notes
- Written by `analysis/write_period_folders.py` (replication layer; templated by design).
