# H33 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-20)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout)
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

## Scorecard (period-specific axes)
<!-- SCORECARD -->
- **C (adequacy):** within-period linear vs curved not separately cross-validated (pooled CV in the card).
- **D (unfitted):** self-repetition slope +2.065 (p 0.066).
- **I (transfer):** sign pattern b₁ > 0, b₂ < 0 present.

## Notes
- 2026-10-04: prediction written before any per-period run (data: `data/processed/H33-diversity-productivity/G51/`).
- 2026-10-04: results filled by `analysis/evaluate.py` + `write_period_folders.py results`.
