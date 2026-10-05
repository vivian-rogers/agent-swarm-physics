# H54 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-24)

**Verdict:** mixed (N3 room swap 0.58 under bge, p 0.57; 0.83 under gte, p 0.03: model-dependent and underpowered)
**Role:** native
**Period:** regime III · mode C · 12 agents with ≥ 3 day-1 statements · two rooms (#best, #rest) · 17 non-holdout active days. Day 1 = statements after the first kickoff message.

## Why this period
The two rooms' kickoff texts differ (cosine 0.60), one of only two periods with room-specific instructions (the other is #44). Uses the shared `goal_fields` room vectors, which fix H01's #38 room swap.

## Prediction
*Written 2026-10-04 in the card (N3) before running on this period.*
- N3: room-swap accuracy ≥ 0.7 along the weaker contrast (room-kickoff cosine 0.60). Credence 0.4.
- Synthetic power is low at this N (4 + 8) unless the room quench is deep.

## Result
| Test | Observed | Null | Verdict |
| --- | --- | --- | --- |
| room-swap accuracy | 0.58 (12 agents; mean margin 0.03), permutation p = 0.57 | 0.5 | failed |
| separation along k̂_best − k̂_rest (Cohen d) | 0.72; percentile among 496 other kickoff-difference axes 0.31 (signed 0.58) | ≥ 0.95 | failed |
| #best (n = 4): spread σ (rarefied) / own-kickoff depth / alignment own vs other kickoff | 0.39 / 0.11 / 0.43 vs 0.38 | – | – |
| #rest (n = 8): spread σ (rarefied) / own-kickoff depth / alignment own vs other kickoff | 0.75 / -0.00 / 0.01 vs -0.01 | – | – |

**Reading.** As in #44, the #best room (4 agents) is tight and near its kickoff, while #rest (8 agents) aligns with neither room's text. The room-swap contrast is too weak (the two texts share most of their content) to separate the rooms. Post hoc: the #best room kickoff is the more specific one (S_text 0.40 vs −0.85), the same direction as #44's HH179 contrast. That makes 2/2 two-instruction periods, with room size and model strength as confounds.

Figure: [`figures/rooms_axis.pdf`](figures/rooms_axis.pdf). Data: `data/processed/H54-kickoff-quench-target/G38/native.json`.

## Scorecard (period-specific axes)
- **C:** room-swap permutation and axis-swap nulls (not beaten).
- **D:** the within-period specificity contrast (HH179) is an unfitted prediction (post hoc here).
- **F:** underpowered at this N (synthetic S5).

## Replication layer (templated, same as every eligible kickoff)

| Statistic | Observed | Predicted |
| --- | --- | --- |
| P1 own-kickoff percentile π (32 decoys, genericness-corrected) | 0.91 (rank 4 of 33; raw 0.88) | ≥ 0.90 |
| P1 own kickoff ranked first | no | top-1 |
| P1 within-regime percentile | 1.00 | ≥ 0.90 |
| P1b beats both neighbouring kickoffs | yes | yes |
| P1c displacement percentile (move vs previous last day) | 0.66 | ≥ 0.85 |
| P1c jump toward the kickoff J_p | 0.13 | > 0 |
| P1d goal-text percentile | 0.97 | (kickoff vs goal text) |
| raw centroid–kickoff cosine | 0.35 | – |
| quench depth D_p (excess over decoys) | 0.07 | – |
| day-1 residual spread σ_p (rarefied) | 0.86 | – |
| kickoff specificity S_text / S_count / S_emb | 0.05 / -0.02 / 0.43 | – |

**H31 projects here (read-only):** 8 (block, project) rows; kickoff-frozen 2, of which named by the goal text or kickoff 1, pre-existing 1. Instant 0, gradual 5, no consensus 1.
**Remanence (HH182):** kickoff excess 0.07 on day 1 → 0.07 on the last day (17 days); exponential-plateau fit τ = 2.0 active days, A∞ = 0.06 (ΔBIC vs constant -5.3).
**First concrete plan (HH181):** posted 1.5 min after the kickoff; centrality excess over 311 day-1 decoy messages Δ_P = -0.05 (percentile 0.32).
**Human messages (HH180):** 2 mid-period messages scored; median re-quench excess 0.14.

Data: `data/processed/H54-kickoff-quench-target/G38/results.json`; cross-kickoff tables `data/processed/H54-kickoff-quench-target/NE34/`.

## Round 2: embedding swap (2026-10-04)
`native.py` rerun unchanged with `H54_MODEL=gte_modernbert` (card R5). Room swap 0.83 (12 agents, p 0.03; bge 0.58, p 0.57); axis percentile 0.61 (bge similar). N3 passes by its rule under gte and fails under bge, so the verdict is "mixed": the weak room contrast (cosine 0.60) is below what one embedding model resolves reliably. Data: `data/processed/H54-kickoff-quench-target/r2_gte/G38/native.json`.

## Notes
- 2026-10-04: folder written by `analysis/period_folders.py` after the round-1 run; the prediction above was dated in the card before the run.
