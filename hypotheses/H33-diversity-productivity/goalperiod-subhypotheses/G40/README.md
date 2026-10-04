# H33 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 2026-05-11)

**Verdict:** n/a
**Role:** replication (exploratory) (round 1, non-holdout)
**Verdict (1b):** n/a (< 5 agent-days above the new breakpoint; 2026-10-04)
**Period:** regime III · mode C (shared objective) · N = 15 at start · 5 non-holdout days with PR10 · 45 agent-days with PR10 (9 agents with ≥ 3 days) · write turns on 93% of those agent-days.

## Why this period
Eligible under the card's pre-registered rule (≥ 30 agent-days with PR10, ≥ 4 agents with ≥ 3 days, write turns on ≥ 20% of agent-days). Mode C: agents ship artifacts toward one shared objective, so output and talk are both about the same project.

## Prediction
*Written 2026-10-04, before running on this period.* The card's predictions as they apply here (`../../README.md`).
- **Model:** log(1 + write turns) = agent FE + day FE + f(PR10) + controls (log raw chat count, log(1 + engaged minutes)); CR1 SEs clustered by agent, t(G − 1) reference.
- **P2 (per period):** two-lines at the *pooled* Robin Hood breakpoint: b₁ > 0 below it and b₂ < 0 above it. The per-period "maximum at the edge" check uses a natural spline with 3 df (4 knots), interior = between the 10th and 90th percentiles of PR10.
- **Power:** low (fewer than 60 agent-days); significance not expected even if H33 is true.
- **Expected (calibrated prior, card):** b₁ > 0, b₂ ≈ 0 (saturating), i.e. **mixed or failed** rather than supported.

**Period verdict rule (card):** supported if b₁ > 0 and b₂ < 0 with at least one significant (p < 0.05); failed if both slopes share a sign or the spline maximum is at an edge; mixed otherwise. **What would count against H33 here:** both slopes of the same sign, or the spline maximum at the edge of the period's PR10 range.

## Result
<!-- RESULT -->
Agent-days 45 · agents 13 · outcome log(1 + write turns), mean writes/agent-day 73.1.

| Check | Observed | Null / threshold | Holds |
| --- | --- | --- | --- |
| b₁ (PR10 < x_c = 15.97) | n/a (p n/a; n 43) | > 0 | n/a |
| b₂ (PR10 ≥ x_c) | n/a (p n/a; n 2) | < 0 | n/a |
| spline (3 df) maximum | PR10 = 5.37 (edge) | interior | no |
| quadratic β₂ | +0.0067 (p 0.433; vertex 13.3) | < 0 | no |
| linear slope (all PR10) | -0.023 (p 0.593) | (rival R1) | – |
| self-repetition slope (T6) | -0.953 (p 0.466) | < 0 | yes |

**Verdict: n/a.** fewer than 5 agent-days on one side of the pooled breakpoint

Figure: `figures/G40_curve.pdf` (binned partial residuals and spline).

## Scorecard (period-specific axes)
<!-- SCORECARD -->
- **C (adequacy):** within-period linear vs curved not separately cross-validated (pooled CV in the card).
- **D (unfitted):** self-repetition slope -0.953 (p 0.466).
- **I (transfer):** sign pattern b₁ > 0, b₂ < 0 not estimable.

## Notes
- 2026-10-04: prediction written before any per-period run (data: `data/processed/H33-diversity-productivity/G40/`).
- 2026-10-04: results filled by `analysis/evaluate.py` + `write_period_folders.py results`.
