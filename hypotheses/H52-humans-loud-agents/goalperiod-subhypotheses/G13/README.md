# H52 × G13: humans as loud agents, replication (2025-09-08 → 2025-09-19)

**Verdict:** mixed — reply 0.081*, content 0.023
**Role:** replication
**Period:** regime I · non-holdout days only · human messages 49 on 9 days (294 message × recipient rows; goal kickoffs excluded) · agent rows 22846. Not powered (fewer than 300 matched human content rows or fewer than 6 days with human messages): read as a phase-diagram point, not a test.

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
| content (DiD χ) | 0.023 [-0.012, 0.052] (n 250, 46 msgs; matched 0.99) | 0.025 | 0.001 | 0.017 [0.002, 0.030] | inconclusive |
| reply (parent) | 0.081 [0.046, 0.155] (n 293, 49 msgs; matched 0.96) | 0.051 | 0.015 | 0.116 [0.082, 0.150] | premium+ |
| activity (min / 30 min, BC) | -0.41 [-0.94, 0.16] (n 246, 43 msgs; matched 0.87) | -0.08 | 24.25 | -0.12 [-0.89, 0.40] | inconclusive |
| stance (soft) | 0.316 [0.256, 0.423] (n 27, 20 msgs; matched 1.00) | 0.316 | 0.596 | -0.013 [-0.097, 0.071] | premium+ |

Robustness (content, human): H30 orthogonalized χ 0.033 [0.006, 0.048]; gte-modernbert 0.015 [0.004, 0.054]; joint per-call deconvolution 0.027 [-0.001, 0.058]; H29 boundary design, human − agent jump (unnamed) 0.083 [0.001, 0.306]. Regime-I content premia carry a synthetic null bias of about −0.024 (Amendment A1). Bootstrap clusters: day.

Data: `data/processed/H52-humans-loud-agents/G13/` (`rows.parquet`, `boundary.parquet`, `results.json`).

## Scorecard (period-specific axes)
- C: premium vs the matched-agent null and the placebo-class null (see `results.json`).
- G: agents' own naming effect reproduces H29/H30's addressed > broadcast where powered.

## Notes
- Written by `analysis/write_period_folders.py` (replication layer; templated by design).
