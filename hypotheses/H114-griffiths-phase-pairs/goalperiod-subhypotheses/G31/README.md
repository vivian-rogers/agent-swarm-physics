# H114 × G31: goal period #31

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #31 · regime I · units 31a, 31b, 31c, 31d · 5 non-holdout days · 13 authors.

## Why this period
Eligible for the replication layer (≥ 300 agent messages and ≥ 100 DQ2 agent-to-agent parent links in at least one unit).

## Prediction
*Written 2026-10-04 21:51 UTC, before running on this period (after Amendment A1). No H114 statistic seen.*
The card's per-period rule on the random-effects pool of its units: supported if Δh > 0 (CI excluding 0), the period has ≥ 1 strong pair (lower bound of g_ij > 0.5, R_ij ≥ 10) and the strong-pair cut brings Δh′ within CI of 0 and below the 5th percentile of matched random cuts; failed if Δh's CI includes 0 or lies below 0 (tail not heavier than geometric), or if Δh > 0 with no strong pair (the HH's kill); mixed if strong pairs exist but do not carry the excess; descriptive with fewer than 100 links or fewer than 30 messages at depth ≥ 4. The card expects Δh > 0 (credence 0.75) and strong pairs in only about a third of units (0.35); A1: a missing strong pair rules out only pairs with g ≳ 0.7.

## Result
*Run 2026-10-04 ~21:55 UTC (non-holdout units).* Period pool (random effects over usable units): **Δh = 0.187 [0.080, 0.294]**, δh = 0.042 [-0.063, 0.147], 0 strong directed pairs in 0 unit(s), the cut carries the excess in 0. Verdict by the card's rule: **failed**.

| Unit | msgs in window | g_rep | h(1) | h_tail (d ≥ 4) | Δh [95%] | δh [95%] | h_tail M1 / M2 | strong pairs | strong-link share | Δh′ after cut (random-cut 5th pct) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 31a | 1198 | 0.314 | 0.476 | 0.458 | 0.144 [-0.042, 0.220] | -0.018 [-0.185, 0.099] | 0.341 / 0.348 | 0 | 0.000 | – (–) |
| 31b | 581 | 0.334 | 0.433 | 0.440 | 0.106 [-0.323, 0.221] | 0.007 [-0.363, 0.105] | 0.335 / 0.329 | 0 | 0.000 | – (–) |
| 31c | 536 | 0.271 | 0.572 | 0.631 | 0.360 [-0.048, 0.443] | 0.058 [-0.316, 0.096] | 0.301 / 0.303 | 0 | 0.000 | – (–) |
| 31d | 700 | 0.329 | 0.496 | 0.585 | 0.257 [0.027, 0.366] | 0.090 [-0.079, 0.168] | 0.387 / 0.392 | 0 | 0.000 | – (–) |

Data: `data/processed/H114-griffiths-phase-pairs/results/units.parquet`, `pairs.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C (Δh against M0 and M1), H (M1 vs M2 vs thread momentum).

## Notes
