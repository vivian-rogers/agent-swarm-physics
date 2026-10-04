# H52 × G08: humans as loud agents, replication (2025-07-18 → 2025-08-12)

**Verdict:** mixed — reply 0.036, content 0.022
**Role:** replication
**Period:** regime I · non-holdout days only · human messages 40 on 11 days (158 message × recipient rows; goal kickoffs excluded) · agent rows 9575. Not powered (fewer than 300 matched human content rows or fewer than 6 days with human messages): read as a phase-diagram point, not a test.

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
| content (DiD χ) | 0.022 [-0.003, 0.039] (n 115, 33 msgs; matched 0.98) | 0.018 | 0.002 | -0.022 [-0.034, -0.008] | inconclusive |
| reply (parent) | 0.036 [-0.012, 0.078] (n 153, 40 msgs; matched 0.83) | 0.057 | 0.027 | 0.131 [0.086, 0.176] | inconclusive |
| activity (min / 30 min, BC) | 0.34 [-0.80, 1.42] (n 132, 33 msgs; matched 0.83) | -0.06 | 25.58 | -0.28 [-1.13, 1.03] | inconclusive |
| stance (soft) | 0.286 [0.117, 0.454] (n 15, 12 msgs; matched 1.00) | 0.305 | 0.564 | -0.166 [-0.331, -0.020] | premium+ |

Robustness (content, human): H30 orthogonalized χ 0.010 [-0.011, 0.026]; gte-modernbert 0.019 [-0.011, 0.047]; joint per-call deconvolution 0.019 [0.003, 0.032]; H29 boundary design: too few human rows at the boundary. Regime-I content premia carry a synthetic null bias of about −0.024 (Amendment A1). Bootstrap clusters: day.

Data: `data/processed/H52-humans-loud-agents/G08/` (`rows.parquet`, `boundary.parquet`, `results.json`).

## Scorecard (period-specific axes)
- C: premium vs the matched-agent null and the placebo-class null (see `results.json`).
- G: agents' own naming effect reproduces H29/H30's addressed > broadcast where powered.

## Notes
- Written by `analysis/write_period_folders.py` (replication layer; templated by design).
