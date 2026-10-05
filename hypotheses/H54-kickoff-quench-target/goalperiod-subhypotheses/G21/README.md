# H54 × G21: Forecast the abilities and effects of AI (2025-12-01 → 2025-12-05)

**Verdict:** mixed (round 2 native R1: both kickoff options readable; no spontaneous domains, as predicted (percentile 0.87 / 0.86); the predicted A → B sequence is not seen over all days; round-1 replication supported)
**Role:** native (round 2, R1); replication (round 1)
**Period:** regime I · mode I · 8 agents with ≥ 3 day-1 statements · #general · 5 non-holdout active days. Day 1 = statements after the first kickoff message.

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
| P1c jump toward the kickoff J_p | 0.50 | > 0 |
| P1d goal-text percentile | 1.00 | (kickoff vs goal text) |
| raw centroid–kickoff cosine | 0.64 | – |
| quench depth D_p (excess over decoys) | 0.52 | – |
| day-1 residual spread σ_p (rarefied) | 0.55 | – |
| kickoff specificity S_text / S_count / S_emb | -0.46 / -0.04 / 0.70 | – |

**H31 projects here (read-only):** 8 (block, project) rows; kickoff-frozen 0, of which named by the goal text or kickoff 0, pre-existing 0. Instant 1, gradual 2, no consensus 5.
**Remanence (HH182):** kickoff excess 0.52 on day 1 → 0.21 on the last day (5 days); exponential-plateau fit τ = 1.2 active days, A∞ = 0.20 (ΔBIC vs constant 8.4).
**First concrete plan (HH181):** posted 1.4 min after the kickoff; centrality excess over 252 day-1 decoy messages Δ_P = 0.26 (percentile 0.96).

Data: `data/processed/H54-kickoff-quench-target/G21/results.json`; cross-kickoff tables `data/processed/H54-kickoff-quench-target/NE34/`.

## Scorecard (period-specific axes)
- **C:** own kickoff vs 32 decoy kickoffs (swap null): π = 1.00.
- **G:** H31's frozen projects (where present) checked against the goal text and kickoff.

## Round 2 native test: two enumerated options (H54-R1, 2026-10-04)
*Prediction written in the card's "Round 2" section before any round-2 statistic (R1-C 0.6, R1-D 0.65, R1-E 0.4). Synthetic S8 first.*
**Why this period:** the kickoff names two concrete sub-targets, "a) quantitative predictions" vs "b) scenarios", without assigning agents to either. Spontaneous two-domain breaking (HH183) would split agents between them; a single quench would put every agent on a mix.
- **Design:** option clauses embedded locally (both models, vectors only); u = unit(t_A − t_B). R1-C: excess alignment with each option over the other kickoffs, days 1–3. R1-D: reliable between-agent variance along u vs 496 kickoff-difference axes (percentile ≥ 0.9 = domains; 12% under one mixed target; power ≥ 0.8 at an agent-level side gap ≈ 0.25). R1-E: Spearman(day, swarm projection on u) < 0.

| Test | bge / gte | Verdict |
| --- | --- | --- |
| R1-C excess, option A | 0.44 / 0.43 | supported |
| R1-C excess, option B | 0.30 / 0.31 | supported |
| R1-D domain percentile | 0.87 / 0.86 | supported (no domains) |
| R1-E sequence ρ | −0.60 / +0.70 (models disagree) | no verdict |

The two option paragraphs are close in embedding space (cos 0.72 bge, 0.77 gte), so the axis is noisy; 0.86–0.87 sits just below the rule. Data: `data/processed/H54-kickoff-quench-target/r2/r1.json`.

## Notes
- 2026-10-04: folder written by `analysis/period_folders.py` after the round-1 run; the prediction above was dated in the card before the run.
