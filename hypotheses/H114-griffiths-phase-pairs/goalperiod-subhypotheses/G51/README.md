# H114 × G51: maximize your private assigned goal (2026-07-06 → 09-04, non-holdout units 51a–51l)

**Verdict:** mixed
**Role:** replication + native (exploratory)
**Period:** regime III · N 21 → 32 · one room (two in 51g) · 12 non-holdout units. The #51 tail (09-07 → 09-21) is held out.

## Why this period
The only period with assigned pair structure in DQ6: 9 rival pairs and 2 opposed pairs (ground truth). If strong reply pairs are real pair couplings, the detector should find assigned pairs more often than chance (axis G). The period also has the most messages, so the depth tail is best resolved here.

## Prediction
*Written 2026-10-04 21:30 UTC, before running on this period. Seen: DQ6's pair counts. No H114 statistic.*
- **Replication:** the card's per-period rule, on the random-effects pool of units 51a–51l.
- **G51a (ground truth):** assigned pairs (rival or opposed, either direction) are enriched among strong directed pairs relative to other directed pairs with R_ij ≥ 10: odds ratio ≥ 2. [0.3]
- **G51b:** assigned pairs have higher pair gains than other pairs with R_ij ≥ 10 (Mann–Whitney p < 0.05, pooled over units). [0.35]

## Result
*Run 2026-10-04 ~21:55 UTC (non-holdout units).* Period pool (random effects over usable units): **Δh = 0.215 [0.173, 0.257]**, δh = 0.067 [0.030, 0.104], 21 strong directed pairs in 7 unit(s), the cut carries the excess in 1. Verdict by the card's rule: **mixed**.

| Unit | msgs in window | g_rep | h(1) | h_tail (d ≥ 4) | Δh [95%] | δh [95%] | h_tail M1 / M2 | strong pairs | strong-link share | Δh′ after cut (random-cut 5th pct) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | 2828 | 0.524 | 0.677 | 0.691 | 0.167 [0.050, 0.241] | 0.015 [-0.060, 0.056] | 0.606 / 0.596 | 0 | 0.000 | – (–) |
| 51b | 0 | – | – | – | – [–, –] | – [–, –] | – / – | 2 | 0.110 | – (–) |
| 51c | 3440 | 0.524 | 0.667 | 0.773 | 0.249 [0.180, 0.302] | 0.106 [0.036, 0.153] | 0.560 / 0.579 | 0 | 0.000 | – (–) |
| 51d | 3364 | 0.587 | 0.723 | 0.733 | 0.146 [0.098, 0.192] | 0.010 [-0.024, 0.042] | 0.611 / 0.615 | 0 | 0.000 | – (–) |
| 51e | 2185 | 0.595 | 0.670 | 0.742 | 0.148 [0.069, 0.228] | 0.072 [-0.006, 0.145] | 0.620 / 0.634 | 1 | 0.059 | 0.180 (0.080) |
| 51f | 3393 | 0.586 | 0.703 | 0.824 | 0.238 [0.157, 0.290] | 0.121 [0.042, 0.172] | 0.624 / 0.623 | 5 | 0.288 | 0.098 (0.109) |
| 51g | 10068 | 0.573 | 0.710 | 0.823 | 0.249 [0.204, 0.298] | 0.112 [0.079, 0.143] | 0.614 / 0.617 | 4 | 0.377 | 0.376 (0.476) |
| 51h | 2191 | 0.538 | 0.762 | 0.837 | 0.299 [0.228, 0.358] | 0.074 [0.018, 0.115] | 0.610 / 0.627 | 3 | 0.184 | 0.285 (0.195) |
| 51i | 784 | 0.463 | 0.716 | 0.774 | 0.311 [0.227, 0.391] | 0.058 [-0.045, 0.134] | 0.565 / 0.626 | 1 | 0.115 | 0.310 (0.212) |
| 51j | 789 | 0.458 | 0.493 | 0.688 | 0.230 [0.011, 0.333] | 0.194 [-0.001, 0.241] | 0.462 / 0.482 | 1 | 0.072 | 0.270 (0.070) |
| 51k | 555 | 0.566 | 0.736 | 0.672 | 0.106 [0.050, 0.195] | -0.064 [-0.107, 0.045] | 0.594 / 0.607 | 0 | 0.000 | – (–) |
| 51l | 438 | 0.546 | 0.690 | 0.775 | 0.230 [0.030, 0.324] | 0.085 [-0.080, 0.131] | 0.646 / 0.666 | 4 | 0.226 | 0.277 (0.284) |

Data: `data/processed/H114-griffiths-phase-pairs/results/units.parquet`, `pairs.parquet`, `periods.parquet`.

### Native G51 (assigned pairs, ground truth)
- Directed pair-unit rows with R_ij ≥ 10 in 51a–51l: 6586; assigned (rival or opposed) 176.
- **G51a** (assigned pairs enriched among strong pairs, OR ≥ 2): strong among assigned 0 of 176, among others 21 of 6410; OR 0 (Fisher p 1.00). **Failed.**
- **G51b** (assigned pairs have higher pair gains): Mann–Whitney one-sided p = 0.0003 (both medians 0; assigned pairs reply to each other more often but never at g > 0.5). **Supported.**
- **Reading:** assigned rivals answer each other a little more than other pairs, but none forms a strong ping-pong pair. The 21 strong pairs of #51 are mostly readers answering a few hub authors.

## Scorecard (period-specific axes)
C, G.

## Notes
