# H54 × G07: Holiday: do whatever you prefer! Next goal will begin soon (2025-07-16 → 2025-07-17)

**Verdict:** supported
**Role:** replication
**Period:** regime I · mode F · 4 agents with ≥ 3 day-1 statements · #general · 2 non-holdout active days. Day 1 = statements after the first kickoff message. Free-choice week: the kickoff names no shared object, so the card's prior was weakest here.

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
| P1 own-kickoff percentile π (32 decoys, genericness-corrected) | 1.00 (rank 1 of 33; raw 1.00) | ≥ 0.90 |
| P1 own kickoff ranked first | yes | top-1 |
| P1 within-regime percentile | 1.00 | ≥ 0.90 |
| P1b beats both neighbouring kickoffs | yes | yes |
| P1c displacement percentile (move vs previous last day) | 0.81 | ≥ 0.85 |
| P1c jump toward the kickoff J_p | 0.04 | > 0 |
| P1d goal-text percentile | 0.47 | (kickoff vs goal text) |
| raw centroid–kickoff cosine | 0.68 | – |
| quench depth D_p (excess over decoys) | 0.45 | – |
| day-1 residual spread σ_p (rarefied) | 0.57 | – |
| kickoff specificity S_text / S_count / S_emb | 0.63 / 0.96 / 0.68 | – |
**First concrete plan (HH181):** posted 12.6 min after the kickoff; centrality excess over 165 day-1 decoy messages Δ_P = 0.25 (percentile 0.82).
**Human messages (HH180):** 9 mid-period messages scored; median re-quench excess 0.04.

Data: `data/processed/H54-kickoff-quench-target/G07/results.json`; cross-kickoff tables `data/processed/H54-kickoff-quench-target/NE34/`.

## Scorecard (period-specific axes)
- **C:** own kickoff vs 32 decoy kickoffs (swap null): π = 1.00.
- **G:** H31's frozen projects (where present) checked against the goal text and kickoff.

## Notes
- 2026-10-04: folder written by `analysis/period_folders.py` after the round-1 run; the prediction above was dated in the card before the run.
