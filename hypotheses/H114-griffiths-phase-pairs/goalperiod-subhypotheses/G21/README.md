# H114 × G21: goal period #21

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #21 · regime I · units 21a, 21b · 5 non-holdout days · 9 authors.

## Why this period
Eligible for the replication layer (≥ 300 agent messages and ≥ 100 DQ2 agent-to-agent parent links in at least one unit).

## Prediction
*Written 2026-10-04 21:51 UTC, before running on this period (after Amendment A1). No H114 statistic seen.*
The card's per-period rule on the random-effects pool of its units: supported if Δh > 0 (CI excluding 0), the period has ≥ 1 strong pair (lower bound of g_ij > 0.5, R_ij ≥ 10) and the strong-pair cut brings Δh′ within CI of 0 and below the 5th percentile of matched random cuts; failed if Δh's CI includes 0 or lies below 0 (tail not heavier than geometric), or if Δh > 0 with no strong pair (the HH's kill); mixed if strong pairs exist but do not carry the excess; descriptive with fewer than 100 links or fewer than 30 messages at depth ≥ 4. The card expects Δh > 0 (credence 0.75) and strong pairs in only about a third of units (0.35); A1: a missing strong pair rules out only pairs with g ≳ 0.7.

## Result
*Run 2026-10-04 ~21:55 UTC (non-holdout units).* Period pool (random effects over usable units): **Δh = – [–, –]**, δh = – [–, –], 2 strong directed pairs in 0 unit(s), the cut carries the excess in 0. Verdict by the card's rule: **descriptive**.

| Unit | msgs in window | g_rep | h(1) | h_tail (d ≥ 4) | Δh [95%] | δh [95%] | h_tail M1 / M2 | strong pairs | strong-link share | Δh′ after cut (random-cut 5th pct) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 21a | 1294 | 0.257 | 0.313 | 0.125 | -0.132 [-0.224, -0.101] | -0.188 [-0.264, -0.134] | 0.231 / 0.238 | 0 | 0.000 | – (–) |
| 21b | 1076 | 0.252 | 0.358 | 0.533 | 0.281 [-0.253, 0.569] | 0.175 [-0.324, 0.553] | 0.230 / 0.228 | 2 | 0.109 | 0.408 (-0.225) |

Data: `data/processed/H114-griffiths-phase-pairs/results/units.parquet`, `pairs.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C (Δh against M0 and M1), H (M1 vs M2 vs thread momentum).

## Notes
