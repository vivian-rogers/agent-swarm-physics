# H33 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-20)

**Verdict:** mixed
**Role:** native (round 1b native test below) · round 1: exploratory (round 1, non-holdout)
**Verdict (1b):** mixed (work commits: b₁ +0.037, b₂ -0.061 (p 0.321); 2026-10-04)
**Period:** regime III · mode I/K (individual/competitive) · N = 21 at start · 45 non-holdout days with PR10 · 746 agent-days with PR10 (27 agents with ≥ 3 days) · write turns on 85% of those agent-days.

## Why this period
Eligible under the card's pre-registered rule (≥ 30 agent-days with PR10, ≥ 4 agents with ≥ 3 days, write turns on ≥ 20% of agent-days). Mode I/K: agents work on their own artifacts, so output is individual and diversity is less tied to coordination.

## Prediction
*Written 2026-10-04, before running on this period.* The card's predictions as they apply here (`../../README.md`).
- **Model:** log(1 + write turns) = agent FE + day FE + f(PR10) + controls (log raw chat count, log(1 + engaged minutes)); CR1 SEs clustered by agent, t(G − 1) reference.
- **P2 (per period):** two-lines at the *pooled* Robin Hood breakpoint: b₁ > 0 below it and b₂ < 0 above it. The per-period "maximum at the edge" check uses a natural spline with 3 df (4 knots), interior = between the 10th and 90th percentiles of PR10.
- **Power:** modest; significance of one slope possible if the effect is ≥ 0.4 residual SD (synthetic).
- **Expected (calibrated prior, card):** b₁ > 0, b₂ ≈ 0 (saturating), i.e. **mixed or failed** rather than supported.

**Period verdict rule (card):** supported if b₁ > 0 and b₂ < 0 with at least one significant (p < 0.05); failed if both slopes share a sign or the spline maximum is at an edge; mixed otherwise. **What would count against H33 here:** both slopes of the same sign, or the spline maximum at the edge of the period's PR10 range.

## Result
<!-- RESULT -->
Agent-days 746 · agents 32 · outcome log(1 + write turns), mean writes/agent-day 43.3.

| Check | Observed | Null / threshold | Holds |
| --- | --- | --- | --- |
| b₁ (PR10 < x_c = 15.97) | +0.052 (p 0.300; n 573) | > 0 | yes |
| b₂ (PR10 ≥ x_c) | -0.097 (p 0.076; n 173) | < 0 | yes |
| spline (3 df) maximum | PR10 = 15.92 (interior) | interior | yes |
| quadratic β₂ | -0.0041 (p 0.250; vertex 17.9) | < 0 | yes |
| linear slope (all PR10) | +0.036 (p 0.191) | (rival R1) | – |
| self-repetition slope (T6) | +2.065 (p 0.066) | < 0 | no |

**Verdict: mixed.** inverted-U signs, neither slope significant

Figure: `figures/G51_curve.pdf` (binned partial residuals and spline).

## Round 1b native test (rival pairs and role classes; DQ6)
*Role of this section: native (round 1b), in addition to the round-1 replication above.*
*Prediction written 2026-10-04, before computing any #51 statistic on the round-1b tables.* #51 gives every agent a private role (DQ6 `ground_truth_labels`, `preferred & ~holdout`); seven roles are held by two or three agents at once (rival pairs: game dev, twitterati, merch baron, youtuber, forecaster, diplomat, reporter). Two agents with the same role on the same day face the same task demands, so the within-pair, same-day difference removes role and day at once.
- **N1 (rival pairs):** regress the same-day pair difference in log(1 + work commits) on the difference in PR10 (and its square), pair fixed effects, CR1 by pair. Prediction: linear and quadratic terms both n.s. (p > 0.05); no inverted U.
- **N2 (role classes):** the within-agent PR10 slope on log(1 + work commits) (agent and day FE, round-1 controls) is n.s. in each of DQ6's role classes (media, support, other) and the classes do not differ (interaction p > 0.05).
- Counts against H33's null reading: a significant concave within-pair relation (quadratic < 0 with p < 0.05 and an interior vertex).

**Result (round 1b native, run 2026-10-04; `data/processed/H33-diversity-productivity/r1b/native.json`).**
- **N1 rival pairs: holds.** 87 same-day pair observations from 8 same-role pairs: linear +0.065 ± 0.047 (p 0.21); with the difference of squares, quadratic −0.0032 ± 0.0055 (p 0.58), vertex 24.3 (outside most of the range). Same role, same day: the more diverse agent does not commit more or less.
- **N2 role classes: fails.** Media (8 agents, 180 agent-days): slope −0.025 (p 0.56); other (20 agents, 481): +0.057 (p 0.074); **support (4 agents, 85 agent-days): concave, linear +0.118 (p 0.002), quadratic −0.0047 (p 0.0005), vertex PR10 ≈ 12.5**; media × PR10 interaction −0.059 (p 0.09). The support-class inverted U rests on 4 agents with a t(3) reference and was one of three classes tested: a lead, not a result.
- Verdict for the native test: **mixed** (N1 holds, N2 fails in the smallest class).

## Scorecard (period-specific axes)
<!-- SCORECARD -->
- **C (adequacy):** within-period linear vs curved not separately cross-validated (pooled CV in the card).
- **D (unfitted):** self-repetition slope +2.065 (p 0.066).
- **I (transfer):** sign pattern b₁ > 0, b₂ < 0 present.

## Notes
- 2026-10-04: prediction written before any per-period run (data: `data/processed/H33-diversity-productivity/G51/`).
- 2026-10-04: results filled by `analysis/evaluate.py` + `write_period_folders.py results`.
