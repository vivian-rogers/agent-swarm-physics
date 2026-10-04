# H114 × G44: goal period #44

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #44 · regime III · units 44a, 44b · 4 non-holdout days · 17 authors.

## Why this period
Eligible for the replication layer (≥ 300 agent messages and ≥ 100 DQ2 agent-to-agent parent links in at least one unit).

## Prediction
*Written 2026-10-04 21:51 UTC, before running on this period (after Amendment A1). No H114 statistic seen.*
The card's per-period rule on the random-effects pool of its units: supported if Δh > 0 (CI excluding 0), the period has ≥ 1 strong pair (lower bound of g_ij > 0.5, R_ij ≥ 10) and the strong-pair cut brings Δh′ within CI of 0 and below the 5th percentile of matched random cuts; failed if Δh's CI includes 0 or lies below 0 (tail not heavier than geometric), or if Δh > 0 with no strong pair (the HH's kill); mixed if strong pairs exist but do not carry the excess; descriptive with fewer than 100 links or fewer than 30 messages at depth ≥ 4. The card expects Δh > 0 (credence 0.75) and strong pairs in only about a third of units (0.35); A1: a missing strong pair rules out only pairs with g ≳ 0.7.

## Result
*Run 2026-10-04 ~21:55 UTC (non-holdout units).* Period pool (random effects over usable units): **Δh = 0.008 [-0.053, 0.070]**, δh = -0.011 [-0.080, 0.058], 1 strong directed pairs in 1 unit(s), the cut carries the excess in 0. Verdict by the card's rule: **failed**.

| Unit | msgs in window | g_rep | h(1) | h_tail (d ≥ 4) | Δh [95%] | δh [95%] | h_tail M1 / M2 | strong pairs | strong-link share | Δh′ after cut (random-cut 5th pct) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 44a | 221 | 0.787 | 0.810 | 0.765 | -0.022 [-0.271, 0.110] | -0.045 [-0.238, 0.027] | 0.745 / 0.744 | 1 | 0.056 | -0.033 (-0.141) |
| 44b | 610 | 0.756 | 0.766 | 0.767 | 0.012 [-0.055, 0.075] | 0.002 [-0.091, 0.070] | 0.736 / 0.735 | 0 | 0.000 | – (–) |

Data: `data/processed/H114-griffiths-phase-pairs/results/units.parquet`, `pairs.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C (Δh against M0 and M1), H (M1 vs M2 vs thread momentum).

## Notes
