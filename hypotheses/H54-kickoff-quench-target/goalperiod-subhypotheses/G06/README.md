# H54 × G06: Create your own merch store. Whichever agent's store makes the most profit wins! (2025-06-26 → 2025-07-15)

**Verdict:** supported
**Role:** replication
**Period:** regime I · mode K · 4 agents with ≥ 3 day-1 statements · #general · 15 non-holdout active days. Day 1 = statements after the first kickoff message.

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
| P1 own-kickoff percentile π (32 decoys, genericness-corrected) | 0.91 (rank 4 of 33; raw 0.94) | ≥ 0.90 |
| P1 own kickoff ranked first | no | top-1 |
| P1 within-regime percentile | 0.86 | ≥ 0.90 |
| P1b beats both neighbouring kickoffs | no | yes |
| P1c displacement percentile (move vs previous last day) | 0.62 | ≥ 0.85 |
| P1c jump toward the kickoff J_p | -0.11 | > 0 |
| P1d goal-text percentile | 1.00 | (kickoff vs goal text) |
| raw centroid–kickoff cosine | 0.36 | – |
| quench depth D_p (excess over decoys) | 0.19 | – |
| day-1 residual spread σ_p (rarefied) | 0.48 | – |
| kickoff specificity S_text / S_count / S_emb | -0.29 / 0.28 / 0.59 | – |
**Remanence (HH182):** kickoff excess 0.19 on day 1 → 0.08 on the last day (15 days); exponential-plateau fit τ = 2.1 active days, A∞ = 0.08 (ΔBIC vs constant 1.0).
**First concrete plan (HH181):** posted 13.8 min after the kickoff; centrality excess over 89 day-1 decoy messages Δ_P = 0.34 (percentile 1.00).
**Human messages (HH180):** 12 mid-period messages scored; median re-quench excess -0.01.

Data: `data/processed/H54-kickoff-quench-target/G06/results.json`; cross-kickoff tables `data/processed/H54-kickoff-quench-target/NE34/`.

## Scorecard (period-specific axes)
- **C:** own kickoff vs 32 decoy kickoffs (swap null): π = 0.91.
- **G:** H31's frozen projects (where present) checked against the goal text and kickoff.

## Notes
- 2026-10-04: folder written by `analysis/period_folders.py` after the round-1 run; the prediction above was dated in the card before the run.
