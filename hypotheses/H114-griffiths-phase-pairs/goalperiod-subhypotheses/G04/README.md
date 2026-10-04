# H114 × G04: goal period #4

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** goal #4 · regime I · units 4a, 4b, 4c, 4d · 26 non-holdout days · 4 authors.

## Why this period
Eligible for the replication layer (≥ 300 agent messages and ≥ 100 DQ2 agent-to-agent parent links in at least one unit).

## Prediction
*Written 2026-10-04 21:51 UTC, before running on this period (after Amendment A1). No H114 statistic seen.*
The card's per-period rule on the random-effects pool of its units: supported if Δh > 0 (CI excluding 0), the period has ≥ 1 strong pair (lower bound of g_ij > 0.5, R_ij ≥ 10) and the strong-pair cut brings Δh′ within CI of 0 and below the 5th percentile of matched random cuts; failed if Δh's CI includes 0 or lies below 0 (tail not heavier than geometric), or if Δh > 0 with no strong pair (the HH's kill); mixed if strong pairs exist but do not carry the excess; descriptive with fewer than 100 links or fewer than 30 messages at depth ≥ 4. The card expects Δh > 0 (credence 0.75) and strong pairs in only about a third of units (0.35); A1: a missing strong pair rules out only pairs with g ≳ 0.7.

## Result
*Run 2026-10-04 ~21:55 UTC (non-holdout units).* Period pool (random effects over usable units): **Δh = 0.291 [0.236, 0.346]**, δh = 0.038 [-0.053, 0.128], 2 strong directed pairs in 1 unit(s), the cut carries the excess in 0. Verdict by the card's rule: **mixed**.

| Unit | msgs in window | g_rep | h(1) | h_tail (d ≥ 4) | Δh [95%] | δh [95%] | h_tail M1 / M2 | strong pairs | strong-link share | Δh′ after cut (random-cut 5th pct) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4a | 1583 | 0.495 | 0.663 | 0.734 | 0.238 [0.090, 0.291] | 0.070 [-0.114, 0.173] | 0.446 / 0.441 | 2 | 0.419 | 0.445 (-0.290) |
| 4b | 309 | 0.369 | 0.711 | 0.679 | 0.310 [0.212, 0.367] | -0.031 [-0.131, 0.029] | 0.429 / 0.428 | 0 | 0.000 | – (–) |
| 4c | 3634 | 0.400 | 0.618 | 0.719 | 0.319 [0.159, 0.398] | 0.102 [-0.047, 0.170] | 0.405 / 0.405 | 0 | 0.000 | – (–) |
| 4d | 84 | 0.321 | 0.407 | – | – [–, –] | – [–, –] | 0.343 / 0.342 | 0 | 0.000 | – (–) |

Data: `data/processed/H114-griffiths-phase-pairs/results/units.parquet`, `pairs.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C (Δh against M0 and M1), H (M1 vs M2 vs thread momentum).

## Notes
