# H54 × G12: Form two teams and debate each other, while one agent judges. Choose your teammates wisely! (2025-09-01 → 2025-09-05)

**Verdict:** mixed (round 2 native R1: the debate centroid locks onto its own motion, median percentile 1.0 in both models; no team domains, Q +0.002, p 0.40; round-1 replication π 1.00)
**Role:** native (round 2, R1); replication (round 1)
**Period:** regime I · mode M · 7 agents with ≥ 3 day-1 statements · #general · 5 non-holdout active days. Day 1 = statements after the first kickoff message.

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
| P1c displacement percentile (move vs previous last day) | 1.00 | ≥ 0.85 |
| P1c jump toward the kickoff J_p | 0.88 | > 0 |
| P1d goal-text percentile | 0.97 | (kickoff vs goal text) |
| raw centroid–kickoff cosine | 0.80 | – |
| quench depth D_p (excess over decoys) | 0.68 | – |
| day-1 residual spread σ_p (rarefied) | 0.49 | – |
| kickoff specificity S_text / S_count / S_emb | 0.24 / 0.61 / 0.84 | – |
**Remanence (HH182):** kickoff excess 0.68 on day 1 → 0.01 on the last day (5 days); exponential-plateau fit τ = 16.0 active days, A∞ = -1.67 (ΔBIC vs constant 2.7).
**First concrete plan (HH181):** posted 3.1 min after the kickoff; centrality excess over 602 day-1 decoy messages Δ_P = 0.21 (percentile 0.89).
**Human messages (HH180):** 3 mid-period messages scored; median re-quench excess 0.11.

Data: `data/processed/H54-kickoff-quench-target/G12/results.json`; cross-kickoff tables `data/processed/H54-kickoff-quench-target/NE34/`.

## Scorecard (period-specific axes)
- **C:** own kickoff vs 32 decoy kickoffs (swap null): π = 1.00.
- **G:** H31's frozen projects (where present) checked against the goal text and kickoff.

## Round 2 native test: two concrete targets (H54-R1, 2026-10-04)
*Prediction written in the card's "Round 2" section before any round-2 statistic (R1-A credence 0.45, R1-B 0.65). Synthetic S7 first.*
**Why this period:** each debate assigns membership (DQ6 teams, re-drafted every debate) and two opposed targets (the two sides of one motion). Re-drafting decorrelates team from agent, so persistent agent offsets cannot fake team domains. The motion is an agent-set text that the human kickoff told the judge to set.
- **Design:** debaters' agent vectors in the `deb` phase (≥ 2 statements; judge and bench out). R1-A: Q = within-team minus between-team pair cosine, against team re-splits, with a pre-draft placebo window (DiD). R1-B: own-motion percentile of the debate centroid among the other debates' motions (motion string by rule; 9 of 10 found; vectors only).

| Test | bge | gte | Null / power | Verdict |
| --- | --- | --- | --- | --- |
| R1-A mean Q (10 debates) | +0.002 (p 0.40) | +0.001 (p 0.39) | re-split permutation; power 1.0 at Q ≈ 0.16, 0.36 at Q ≈ 0.04 | failed |
| R1-A DiD vs pre-draft | −0.003 (p 0.54) | +0.000 (p 0.54) | false positives 0.085 at nominal 0.10 (S7) | failed |
| R1-B own motion | median 1.0, top-1 6/9, p 0.012 | median 1.0, top-1 6/9, p 0.002 | other motions | supported |

**Reading:** within a 10-minute debate the whole room's content locks onto the motion (one shared target). The two teams do not form separate content domains in the embedding: arguing pro and con of one motion looks like one topic. Data: `data/processed/H54-kickoff-quench-target/r2/r1.json`.

## Notes
- 2026-10-04: folder written by `analysis/period_folders.py` after the round-1 run; the prediction above was dated in the card before the run.
