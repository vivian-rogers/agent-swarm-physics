# H54 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-04)

**Verdict:** supported (N1 and N1b; the shared-kickoff replication fails here, as private goals predict)
**Role:** native
**Period:** regime III · mode I/K · 21 agents with ≥ 3 day-1 statements · rooms · 45 non-holdout active days. Day 1 = statements after the first kickoff message.

## Why this period
The only period where every agent has its **own** written target (`agent_goal`, 33 rows; DQ6 roles, 7 rival pairs). If the kickoff text is the quench target, each agent should land on its own private goal, not on the shared kickoff. NE38 (07-29 16:51 UTC: a human reassigns Claude Opus 5 from a game-dev goal to a mathematics goal) is a single-agent re-quench inside it.

## Prediction
*Written 2026-10-04 in the card (N1, N1b) before running on this period.*
- N1: role-swap pair accuracy ≥ 0.75 (pairs with different roles; permutation p < 0.01); centered alignment cos(v_i − m, ĝ_i − mean ĝ) > 0 on average; accuracy ≥ 0.65 in the last pre-tail week. Credence 0.75 / 0.6.
- N1b: Opus 5's alignment with its new goal rises after 07-29 by more than the other agents' alignment with that goal (difference in differences > 0, day-bootstrap CI excluding 0). Credence 0.6.
- Counts against: accuracy ≤ 0.6; no rise.

## Result
| Test | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| N1 role-swap accuracy (first day per agent) | 0.95 (32 agents, 25 roles, 489 pairs), p = 0.0002 | synthetic no-private-field 0.47–0.50 | supported |
| own-goal percentile among other roles' goals | median 1.00, top-1 0.56 | 0.5 | supported |
| centered alignment | mean 0.36, positive in 0.91, p = 0.0002 | 0 | supported |
| own goal vs shared kickoff (excess over decoys) | own goal 0.30 vs shared kickoff -0.03; own wins for 0.84 of agents | – | agents land on their own target |
| persistence: weekly accuracy, weeks 1–9 of the head | 0.93, 0.92, 0.96, 0.93, 0.90, 0.91, 0.92, 0.92, 0.95 | ≥ 0.65 in the last week | supported (no decay) |
| robustness (post hoc): chat only / style-residualized / both | 0.95 / 0.91 / 0.90 | – | holds |
| N1b NE38 DiD, alignment with the new goal | 0.61 [0.57, 0.66] (Opus 5 +0.63, others +0.02) | 0 | supported |
| NE38 DiD, alignment with the old (game-dev) goal | -0.29 [-0.38, -0.22] | 0 | moves off the old target |

The shared #51 kickoff itself is *not* identified by the day-1 centroid (replication π below): with private targets, the swarm centroid points at no one's goal. This is the replication failure the private-goal reading predicts.

Figure: [`../../figures/summary_obs_b.pdf`](../../figures/summary_obs_b.pdf) (weekly accuracy; NE38 series).

## Scorecard (period-specific axes)
- **C:** role-swap permutation null and synthetic no-field band beaten at p = 0.0002.
- **E:** NE38 is an intervention on one agent's field: predicted sign and a large size, CI excluding 0 (4 pre days, 8 post days).
- **G:** ground truth = the assigned goal texts and DQ6 roles; agents' positions recover them.
- **Caveat:** goal restatement is part of the mechanism. Excluding intentions (where agents restate their role) leaves the accuracy unchanged, but chat can quote the goal too.

## Replication layer (templated, same as every eligible kickoff)

| Statistic | Observed | Predicted |
| --- | --- | --- |
| P1 own-kickoff percentile π (32 decoys, genericness-corrected) | 0.25 (rank 25 of 33; raw 0.25) | ≥ 0.90 |
| P1 own kickoff ranked first | no | top-1 |
| P1 within-regime percentile | 0.29 | ≥ 0.90 |
| P1b beats both neighbouring kickoffs | no | yes |
| P1c displacement percentile (move vs previous last day) | – | ≥ 0.85 |
| P1c jump toward the kickoff J_p | – | > 0 |
| P1d goal-text percentile | 0.12 | (kickoff vs goal text) |
| raw centroid–kickoff cosine | 0.17 | – |
| quench depth D_p (excess over decoys) | -0.03 | – |
| day-1 residual spread σ_p (rarefied) | 0.91 | – |
| kickoff specificity S_text / S_count / S_emb | 0.08 / 0.79 / 0.44 | – |
**Remanence (HH182):** kickoff excess -0.03 on day 1 → 0.02 on the last day (45 days); exponential-plateau fit τ = 0.9 active days, A∞ = -0.00 (ΔBIC vs constant -5.2).
**First concrete plan (HH181):** posted 4.1 min after the kickoff; centrality excess over 1752 day-1 decoy messages Δ_P = -0.00 (percentile 0.41).
**Human messages (HH180):** 22 mid-period messages scored; median re-quench excess 0.10.

Data: `data/processed/H54-kickoff-quench-target/G51/results.json`; cross-kickoff tables `data/processed/H54-kickoff-quench-target/NE34/`.

## Notes
- 2026-10-04: folder written by `analysis/period_folders.py` after the round-1 run; the prediction above was dated in the card before the run.
