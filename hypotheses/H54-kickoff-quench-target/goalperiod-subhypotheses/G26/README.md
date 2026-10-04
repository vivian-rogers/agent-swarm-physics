# H54 × G26: Elect a village leader. They choose this week’s goal! (2026-01-05 → 2026-01-09)

**Verdict:** mixed (day-1 target identified; the leader's goal announcement did not re-quench beyond decoys)
**Role:** native
**Period:** regime I · mode C · 10 agents with ≥ 3 day-1 statements · #general · 5 non-holdout active days. Day 1 = statements after the first kickoff message.

## Why this period
The kickoff names a **decision procedure** (elect a leader who picks the week's goal), not an object. The elected leader's goal announcement (DQ6: result 19:35 UTC on 01-05; announcement by DeepSeek-V3.2 41 s later, found by rule, message id in `g26_leader.json`) is an agent-authored second target on day 1. That makes this period HH181 (a concrete plan completes the target) and HH180 (a re-quench) in their cleanest form.

## Prediction
*Written 2026-10-04 in the card (N4) before running on this period.*
- The day-1 centroid identifies the election kickoff (π ≥ 0.9).
- After the leader's announcement, the other agents' centroid moves toward its vector by more than toward decoy agent messages from the same day (excess > 0, decoy percentile ≥ 0.9).
- The frozen or instant projects after it are ones the announcement names. Credence 0.6.

## Result
| Test | Observed | Null | Verdict |
| --- | --- | --- | --- |
| day-1 own-kickoff percentile | see replication table (π = 0.97, rank 2) | 0.5 | supported |
| move toward the announcement, 0-60min | excess over 427 decoys 0.07, decoy percentile 0.48 | ≥ 0.9 | failed |
| move toward the announcement, 60-180min | excess over 427 decoys -0.18, decoy percentile 0.39 | ≥ 0.9 | failed |
| move toward the announcement, rest_of_day1 | excess over 427 decoys -0.10, decoy percentile 0.41 | ≥ 0.9 | failed |
| projects named by the announcement | 0 artifacts named; none of the 8 H31 #26 projects (1 frozen, 6 instant) is named by it | – | failed |

**Daily excess over decoys** (kickoff vs leader announcement as targets): day 1-pre: kickoff 0.54, leader 0.23; day 1: kickoff 0.02, leader 0.04; day 2: kickoff 0.24, leader 0.20; day 3: kickoff -0.06, leader -0.05; day 4: kickoff -0.22, leader -0.17; day 5: kickoff 0.10, leader -0.04.

**Reading.** Before the result, day-1 content sits very close to the election kickoff (excess 0.54, the highest of any segment). After the result, alignment with *both* the kickoff and the announcement collapses toward 0. The swarm leaves the election topic, but not toward the announcement's text as embedded. The six instant project waves later on day 1 are artifacts the announcement never names. An agent-authored plan did not act as a text quench target here; the operational target was whatever the agents then built. n = 1 period.

## Scorecard (period-specific axes)
- **E:** the election result is a dated step: the predicted re-quench toward the leader's text is absent.
- **G:** DQ6 ground truth (phases, winner) used for timing.

## Replication layer (templated, same as every eligible kickoff)

| Statistic | Observed | Predicted |
| --- | --- | --- |
| P1 own-kickoff percentile π (32 decoys, genericness-corrected) | 0.97 (rank 2 of 33; raw 0.97) | ≥ 0.90 |
| P1 own kickoff ranked first | no | top-1 |
| P1 within-regime percentile | 0.95 | ≥ 0.90 |
| P1b beats both neighbouring kickoffs | yes | yes |
| P1c displacement percentile (move vs previous last day) | 1.00 | ≥ 0.85 |
| P1c jump toward the kickoff J_p | 0.82 | > 0 |
| P1d goal-text percentile | 1.00 | (kickoff vs goal text) |
| raw centroid–kickoff cosine | 0.46 | – |
| quench depth D_p (excess over decoys) | 0.33 | – |
| day-1 residual spread σ_p (rarefied) | 0.68 | – |
| kickoff specificity S_text / S_count / S_emb | 0.52 / -0.62 / 0.71 | – |

**H31 projects here (read-only):** 8 (block, project) rows; kickoff-frozen 1, of which named by the goal text or kickoff 0, pre-existing 0. Instant 6, gradual 0, no consensus 1.
**Remanence (HH182):** kickoff excess 0.33 on day 1 → 0.14 on the last day (5 days); exponential-plateau fit τ = 1.2 active days, A∞ = -0.05 (ΔBIC vs constant 0.7).
**First concrete plan (HH181):** posted 1.6 min after the kickoff; centrality excess over 561 day-1 decoy messages Δ_P = 0.15 (percentile 0.74).

Data: `data/processed/H54-kickoff-quench-target/G26/results.json`; cross-kickoff tables `data/processed/H54-kickoff-quench-target/NE34/`.

## Notes
- 2026-10-04: folder written by `analysis/period_folders.py` after the round-1 run; the prediction above was dated in the card before the run.
