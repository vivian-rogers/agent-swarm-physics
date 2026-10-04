# H52 × G30: humans as loud agents, replication (2026-02-09 → 2026-02-13)

**Verdict:** mixed — reply 0.026, content 0.030
**Role:** replication
**Period:** regime I · non-holdout days only · human messages 14 on 5 days (154 message × recipient rows; goal kickoffs excluded) · agent rows 26597 · bot rows 132. Not powered (fewer than 300 matched human content rows or fewer than 6 days with human messages): read as a phase-diagram point, not a test.

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
| content (DiD χ) | 0.030 [-0.010, 0.074] (n 143, 13 msgs; matched 1.00) | 0.036 | 0.000 | -0.020 [-0.035, -0.009] | inconclusive |
| reply (parent) | 0.026 [-0.009, 0.061] (n 152, 14 msgs; matched 1.00) | 0.009 | 0.014 | 0.088 [0.073, 0.100] | equivalent |
| activity (min / 30 min, BC) | 0.07 [-0.48, 0.63] (n 133, 13 msgs; matched 0.99) | 0.19 | 24.54 | -0.13 [-0.45, 0.17] | inconclusive |
| stance (soft) | 0.291 [0.030, 0.540] (n 6, 5 msgs; matched 1.00) | 0.321 | 0.555 | -0.134 [-0.220, -0.035] | premium+ |

**Bot (automated nudges; named = leading @):**

| Outcome | Bot premium [95% CI] | n rows |
| --- | --- | --- |
| content (DiD χ) | — [—] | 0 |
| reply (parent) | -0.002 [-0.032, 0.052] | 125 |
| activity (min / 30 min, BC) | -0.29 [-0.79, 0.25] | 110 |
| stance (soft) | — [—] | 3 |

Robustness (content, human): H30 orthogonalized χ 0.010 [-0.021, 0.038]; gte-modernbert 0.024 [0.002, 0.053]; joint per-call deconvolution 0.034 [0.003, 0.064]; H29 boundary design: too few human rows at the boundary. Regime-I content premia carry a synthetic null bias of about −0.024 (Amendment A1). Bootstrap clusters: message.

Data: `data/processed/H52-humans-loud-agents/G30/` (`rows.parquet`, `boundary.parquet`, `results.json`).

## Scorecard (period-specific axes)
- C: premium vs the matched-agent null and the placebo-class null (see `results.json`).
- G: agents' own naming effect reproduces H29/H30's addressed > broadcast where powered.

## Notes
- Written by `analysis/write_period_folders.py` (replication layer; templated by design).
