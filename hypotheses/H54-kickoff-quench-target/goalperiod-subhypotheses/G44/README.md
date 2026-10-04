# H54 × G44: Finetune your leader! (2026-05-26 → 2026-05-29)

**Verdict:** mixed (N2 two domains failed; N2b vague room more spread supported)
**Role:** native
**Period:** regime III · mode C · 16 agents with ≥ 3 day-1 statements · two rooms (#best, #rest) · 4 non-holdout active days. Day 1 = statements after the first kickoff message.

## Why this period
The two rooms got different instructions on the same day: #best (4 agents) was told to fine-tune a Kimi leader; #rest (12 agents) to choose its own goals. Room kickoffs have cosine 0.39. HH183's two domains, and HH179 inside one period (same day, regime, roster).

## Prediction
*Written 2026-10-04 in the card (N2, N2b) before running on this period.*
- N2: each agent is closer to its own room's kickoff (room-swap accuracy ≥ 0.8); the rooms separate along u = k̂_best − k̂_rest more than along other kickoff-difference axes (axis-swap percentile ≥ 0.95). Credence 0.65.
- N2b (HH179 within one day): the vague #rest kickoff (agents choose their own goals; 43 words) leaves more spread than the specific #best kickoff (fine-tune a leader) and a lower own-kickoff depth. Credence 0.6.
- Synthetic power (Amendment 1): room-swap accuracy ≥ 0.8 in only 48% of runs at a day-1 target share of 0.15.

## Result
| Test | Observed | Null | Verdict |
| --- | --- | --- | --- |
| room-swap accuracy | 0.31 (16 agents; mean margin -0.05), permutation p = 0.76 | 0.5 | failed |
| separation along k̂_best − k̂_rest (Cohen d) | 1.55; percentile among 496 other kickoff-difference axes 0.65 (signed 0.81) | ≥ 0.95 | failed |
| #best (n = 4): spread σ (rarefied) / own-kickoff depth / alignment own vs other kickoff | 0.50 / 0.37 / 0.52 vs 0.07 | – | – |
| #rest (n = 12): spread σ (rarefied) / own-kickoff depth / alignment own vs other kickoff | 0.80 / -0.25 / -0.15 vs 0.06 | – | – |
| N2b: σ_rest > σ_best and lower depth | σ 0.80 vs 0.50; depth -0.25 vs 0.37 | – | supported |

**Reading.** One quenched domain plus a disordered remainder, not two domains. #best sits tightly on its own kickoff (alignment 0.52 vs 0.07 with the other room's text). #rest is not on its own kickoff at all: its depth is below the decoy kickoffs, because a choose-your-own-goal instruction names no target, and it is more spread out. The room-swap test assumed two targets, so it fails by construction: #rest agents are, if anything, slightly closer to #best's text than to their own. HH179 holds inside the period. The room-size confound (4 vs 12) and the stronger #best models are caveats.

Figure: [`figures/rooms_axis.pdf`](figures/rooms_axis.pdf). Data: `data/processed/H54-kickoff-quench-target/G44/native.json`.

## Scorecard (period-specific axes)
- **C:** room-swap permutation and axis-swap nulls (not beaten).
- **D:** the within-period specificity contrast (HH179) is an unfitted prediction (supported).
- **F:** underpowered at this N (synthetic S5).

## Replication layer (templated, same as every eligible kickoff)

| Statistic | Observed | Predicted |
| --- | --- | --- |
| P1 own-kickoff percentile π (32 decoys, genericness-corrected) | 0.47 (rank 18 of 33; raw 0.56) | ≥ 0.90 |
| P1 own kickoff ranked first | no | top-1 |
| P1 within-regime percentile | 0.57 | ≥ 0.90 |
| P1b beats both neighbouring kickoffs | yes | yes |
| P1c displacement percentile (move vs previous last day) | – | ≥ 0.85 |
| P1c jump toward the kickoff J_p | – | > 0 |
| P1d goal-text percentile | 0.34 | (kickoff vs goal text) |
| raw centroid–kickoff cosine | 0.23 | – |
| quench depth D_p (excess over decoys) | 0.00 | – |
| day-1 residual spread σ_p (rarefied) | 0.84 | – |
| kickoff specificity S_text / S_count / S_emb | 0.03 / 0.24 / 0.48 | – |

**H31 projects here (read-only):** 8 (block, project) rows; kickoff-frozen 0, of which named by the goal text or kickoff 0, pre-existing 0. Instant 0, gradual 2, no consensus 6.
**First concrete plan (HH181):** posted 5.3 min after the kickoff; centrality excess over 384 day-1 decoy messages Δ_P = -0.07 (percentile 0.31).
**Human messages (HH180):** 3 mid-period messages scored; median re-quench excess 0.12.

Data: `data/processed/H54-kickoff-quench-target/G44/results.json`; cross-kickoff tables `data/processed/H54-kickoff-quench-target/NE34/`.

## Notes
- 2026-10-04: folder written by `analysis/period_folders.py` after the round-1 run; the prediction above was dated in the card before the run.
