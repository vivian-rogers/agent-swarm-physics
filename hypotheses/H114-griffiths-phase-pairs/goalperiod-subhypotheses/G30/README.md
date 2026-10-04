# H114 × G30: goal period #30

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #30 · regime I · units 30a, 30b · 5 non-holdout days · 12 authors.

## Why this period
Eligible for the replication layer (≥ 300 agent messages and ≥ 100 DQ2 agent-to-agent parent links in at least one unit).

## Prediction
*Written 2026-10-04 21:51 UTC, before running on this period (after Amendment A1). No H114 statistic seen.*
The card's per-period rule on the random-effects pool of its units: supported if Δh > 0 (CI excluding 0), the period has ≥ 1 strong pair (lower bound of g_ij > 0.5, R_ij ≥ 10) and the strong-pair cut brings Δh′ within CI of 0 and below the 5th percentile of matched random cuts; failed if Δh's CI includes 0 or lies below 0 (tail not heavier than geometric), or if Δh > 0 with no strong pair (the HH's kill); mixed if strong pairs exist but do not carry the excess; descriptive with fewer than 100 links or fewer than 30 messages at depth ≥ 4. The card expects Δh > 0 (credence 0.75) and strong pairs in only about a third of units (0.35); A1: a missing strong pair rules out only pairs with g ≳ 0.7.

## Result
*Run 2026-10-04 ~21:55 UTC (non-holdout units).* Period pool (random effects over usable units): **Δh = 0.067 [-0.083, 0.217]**, δh = -0.076 [-0.221, 0.069], 0 strong directed pairs in 0 unit(s), the cut carries the excess in 0. Verdict by the card's rule: **failed**.

| Unit | msgs in window | g_rep | h(1) | h_tail (d ≥ 4) | Δh [95%] | δh [95%] | h_tail M1 / M2 | strong pairs | strong-link share | Δh′ after cut (random-cut 5th pct) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 30a | 513 | 0.283 | 0.462 | 0.300 | 0.017 [-0.268, 0.137] | -0.162 [-0.511, -0.026] | 0.307 / 0.306 | 0 | 0.000 | – (–) |
| 30b | 2033 | 0.357 | 0.500 | 0.424 | 0.067 [-0.122, 0.178] | -0.076 [-0.249, 0.041] | 0.375 / 0.374 | 0 | 0.000 | – (–) |

Data: `data/processed/H114-griffiths-phase-pairs/results/units.parquet`, `pairs.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C (Δh against M0 and M1), H (M1 vs M2 vs thread momentum).

## Notes
