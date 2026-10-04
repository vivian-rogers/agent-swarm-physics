# H54 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 2026-03-20)

**Verdict:** supported
**Role:** replication
**Period:** regime II · mode C · 12 agents with ≥ 3 day-1 statements · two rooms (#best, #rest) · 5 non-holdout active days. Day 1 = statements after the first kickoff message.

## Why this period
One of the 33 eligible kickoffs (layer 1, replication): the common estimators give one comparable point per kickoff. The cross-kickoff tests (swap null, specificity, remanence, family susceptibility) are in [`../NE34/README.md`](../NE34/README.md).

## Prediction
*Templated, written 2026-10-04 in the card before any real-data run (card P1, P1b, P1c, P2).*
- The day-1 centroid identifies this period's kickoff: own percentile π ≥ 0.90 among 32 decoy kickoffs, ideally top-1; it beats both neighbouring kickoffs.
- Where a previous period is available, the day-1 move points at the kickoff (displacement percentile ≥ 0.85, jump > 0).
- Projects H31 found frozen at this kickoff are ones the goal text or kickoff names.
- **Per-period verdict rule:** supported if π ≥ 0.90; failed if π < 0.75; mixed otherwise.

## Result
| Statistic | Observed | Predicted |
| --- | --- | --- |
| P1 own-kickoff percentile π (32 decoys, genericness-corrected) | 0.97 (rank 2 of 33; raw 0.97) | ≥ 0.90 |
| P1 own kickoff ranked first | no | top-1 |
| P1 within-regime percentile | 1.00 | ≥ 0.90 |
| P1b beats both neighbouring kickoffs | yes | yes |
| P1c displacement percentile (move vs previous last day) | – | ≥ 0.85 |
| P1c jump toward the kickoff J_p | – | > 0 |
| P1d goal-text percentile | 1.00 | (kickoff vs goal text) |
| raw centroid–kickoff cosine | 0.14 | – |
| quench depth D_p (excess over decoys) | 0.18 | – |
| day-1 residual spread σ_p (rarefied) | 0.83 | – |
| kickoff specificity S_text / S_count / S_emb | 0.32 / 0.63 / 0.58 | – |

**H31 projects here (read-only):** 2 (block, project) rows; kickoff-frozen 2, of which named by the goal text or kickoff 2, pre-existing 0. Instant 0, gradual 0, no consensus 0.
**Remanence (HH182):** kickoff excess 0.18 on day 1 → 0.19 on the last day (5 days); exponential-plateau fit τ = 0.2 active days, A∞ = 0.10 (ΔBIC vs constant -1.8).
**First concrete plan (HH181):** posted 1.4 min after the kickoff; centrality excess over 371 day-1 decoy messages Δ_P = 0.03 (percentile 0.61).

Data: `data/processed/H54-kickoff-quench-target/G35/results.json`; cross-kickoff tables `data/processed/H54-kickoff-quench-target/NE34/`.

## Scorecard (period-specific axes)
- **C:** own kickoff vs 32 decoy kickoffs (swap null): π = 0.97.
- **G:** H31's frozen projects (where present) checked against the goal text and kickoff.

## Notes
- 2026-10-04: folder written by `analysis/period_folders.py` after the round-1 run; the prediction above was dated in the card before the run.
