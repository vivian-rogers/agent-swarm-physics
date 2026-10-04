# H114 × G38: goal period #38

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** goal #38 · regime III · units 38a, 38b, 38d, 38e · 16 non-holdout days · 13 authors.

## Why this period
Eligible for the replication layer (≥ 300 agent messages and ≥ 100 DQ2 agent-to-agent parent links in at least one unit).

## Prediction
*Written 2026-10-04 21:51 UTC, before running on this period (after Amendment A1). No H114 statistic seen.*
The card's per-period rule on the random-effects pool of its units: supported if Δh > 0 (CI excluding 0), the period has ≥ 1 strong pair (lower bound of g_ij > 0.5, R_ij ≥ 10) and the strong-pair cut brings Δh′ within CI of 0 and below the 5th percentile of matched random cuts; failed if Δh's CI includes 0 or lies below 0 (tail not heavier than geometric), or if Δh > 0 with no strong pair (the HH's kill); mixed if strong pairs exist but do not carry the excess; descriptive with fewer than 100 links or fewer than 30 messages at depth ≥ 4. The card expects Δh > 0 (credence 0.75) and strong pairs in only about a third of units (0.35); A1: a missing strong pair rules out only pairs with g ≳ 0.7.

## Result
*Run 2026-10-04 ~21:55 UTC (non-holdout units).* Period pool (random effects over usable units): **Δh = 0.175 [0.111, 0.240]**, δh = 0.024 [-0.036, 0.084], 2 strong directed pairs in 1 unit(s), the cut carries the excess in 0. Verdict by the card's rule: **mixed**.

| Unit | msgs in window | g_rep | h(1) | h_tail (d ≥ 4) | Δh [95%] | δh [95%] | h_tail M1 / M2 | strong pairs | strong-link share | Δh′ after cut (random-cut 5th pct) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 38a | 2209 | 0.472 | 0.618 | 0.638 | 0.166 [0.080, 0.239] | 0.020 [-0.051, 0.083] | 0.507 / 0.504 | 2 | 0.209 | 0.289 (-0.042) |
| 38b | 597 | 0.533 | 0.648 | 0.669 | 0.136 [-0.090, 0.223] | 0.021 [-0.192, 0.134] | 0.564 / 0.569 | 0 | 0.000 | – (–) |
| 38d | 231 | 0.511 | 0.585 | 0.641 | 0.130 [-0.210, 0.184] | 0.056 [-0.292, 0.086] | 0.563 / 0.589 | 0 | 0.000 | – (–) |
| 38e | 452 | 0.321 | 0.483 | 0.569 | 0.249 [0.096, 0.406] | 0.087 [-0.120, 0.380] | 0.313 / 0.296 | 0 | 0.000 | – (–) |

Data: `data/processed/H114-griffiths-phase-pairs/results/units.parquet`, `pairs.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C (Δh against M0 and M1), H (M1 vs M2 vs thread momentum).

## Notes
