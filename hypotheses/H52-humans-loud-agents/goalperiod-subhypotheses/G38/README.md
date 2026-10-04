# H52 × G38: humans as loud agents, replication (2026-04-02 → 2026-04-24)

**Verdict:** mixed — reply 0.128*, content 0.026
**Role:** replication
**Period:** regime III · non-holdout days only · human messages 26 on 12 days (133 message × recipient rows; goal kickoffs excluded) · agent rows 24354 · bot rows 781. Not powered (fewer than 300 matched human content rows or fewer than 6 days with human messages): read as a phase-diagram point, not a test.

## Why this period
Replication layer: the common estimator on every non-holdout goal period with ≥ 100 non-kickoff human (message, recipient) rows on ≥ 3 days. Regime III: human messages are mostly operator or staff messages.

## Prediction
*Templated replication prediction, copied from the card (written 2026-10-04 ~06:10 UTC, before any outcome statistic).*
- H52: the matched human premium is equivalent to 0 in content and activity; reply and stance premia reported.
- Author's expectation (card P1–P4): content premium > 0 in regime III and ≤ 0 in regime I; reply premium > 0; activity premium CI includes 0; stance premium > 0.
- Counts against H52: a content or reply premium whose CI lies beyond the margin (δ_con = 0.5 × pooled agent naming effect; δ_rep likewise).

## Result
Margins: δ_con 0.0073, δ_rep 0.0637, δ_act 0.5 min, δ_st 0.05. Premium = CEM ATT of human rows vs agent rows in the same salience stratum (Amendment A1 estimators). In the verdict line, * marks a 95% CI that excludes 0.

| Outcome | Human premium [95% CI] | Naive human − agent | Matched agent mean | Agent naming effect | Verdict |
| --- | --- | --- | --- | --- | --- |
| content (DiD χ) | 0.026 [-0.003, 0.057] (n 105, 21 msgs; matched 0.99) | 0.029 | -0.001 | -0.017 [-0.028, -0.007] | inconclusive |
| reply (parent) | 0.128 [0.017, 0.248] (n 120, 26 msgs; matched 0.97) | 0.085 | 0.052 | 0.218 [0.171, 0.280] | premium+ |
| activity (min / 30 min, BC) | 0.83 [-0.17, 2.14] (n 118, 25 msgs; matched 0.79) | 0.97 | 22.29 | 0.45 [-0.31, 0.95] | inconclusive |
| stance (soft) | 0.009 [-0.115, 0.215] (n 22, 14 msgs; matched 1.00) | 0.002 | 0.661 | -0.036 [-0.092, 0.019] | inconclusive |

**Bot (automated nudges; named = leading @):**

| Outcome | Bot premium [95% CI] | n rows |
| --- | --- | --- |
| content (DiD χ) | -0.011 [-0.018, -0.002] | 700 |
| reply (parent) | -0.052 [-0.076, -0.028] | 527 |
| activity (min / 30 min, BC) | -0.24 [-0.53, 0.23] | 639 |
| stance (soft) | -0.107 [-0.248, 0.054] | 23 |

Robustness (content, human): H30 orthogonalized χ 0.006 [-0.018, 0.023]; gte-modernbert 0.043 [0.003, 0.094]; joint per-call deconvolution 0.031 [0.005, 0.061]; H29 boundary design: too few human rows at the boundary. Regime-III content premia carry a synthetic null bias of about −0.006 (Amendment A1). Bootstrap clusters: day.

Data: `data/processed/H52-humans-loud-agents/G38/` (`rows.parquet`, `boundary.parquet`, `results.json`).

## Scorecard (period-specific axes)
- C: premium vs the matched-agent null and the placebo-class null (see `results.json`).
- G: agents' own naming effect reproduces H29/H30's addressed > broadcast where powered.

## Notes
- Written by `analysis/write_period_folders.py` (replication layer; templated by design).
