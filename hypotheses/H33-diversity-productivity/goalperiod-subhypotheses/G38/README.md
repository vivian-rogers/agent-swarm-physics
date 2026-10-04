# H33 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-27)

**Verdict:** mixed
**Role:** replication (exploratory) (round 1, non-holdout)
**Verdict (1b):** supported (work commits: b₁ +0.050, b₂ -0.166 (p < 0.001); 2026-10-04)
**Period:** regime III · mode C (shared objective) · N = 12 at start · 17 non-holdout days with PR10 · 98 agent-days with PR10 (10 agents with ≥ 3 days) · write turns on 86% of those agent-days.

## Why this period
Eligible under the card's pre-registered rule (≥ 30 agent-days with PR10, ≥ 4 agents with ≥ 3 days, write turns on ≥ 20% of agent-days). Mode C: agents ship artifacts toward one shared objective, so output and talk are both about the same project.

## Prediction
*Written 2026-10-04, before running on this period.* The card's predictions as they apply here (`../../README.md`).
- **Model:** log(1 + write turns) = agent FE + day FE + f(PR10) + controls (log raw chat count, log(1 + engaged minutes)); CR1 SEs clustered by agent, t(G − 1) reference.
- **P2 (per period):** two-lines at the *pooled* Robin Hood breakpoint: b₁ > 0 below it and b₂ < 0 above it. The per-period "maximum at the edge" check uses a natural spline with 3 df (4 knots), interior = between the 10th and 90th percentiles of PR10.
- **Power:** modest; significance of one slope possible if the effect is ≥ 0.4 residual SD (synthetic).
- **Expected (calibrated prior, card):** b₁ > 0, b₂ ≈ 0 (saturating), i.e. **mixed or failed** rather than supported.

**Period verdict rule (card):** supported if b₁ > 0 and b₂ < 0 with at least one significant (p < 0.05); failed if both slopes share a sign or the spline maximum is at an edge; mixed otherwise. **What would count against H33 here:** both slopes of the same sign, or the spline maximum at the edge of the period's PR10 range.

## Result
<!-- RESULT -->
Agent-days 98 · agents 12 · outcome log(1 + write turns), mean writes/agent-day 13.4.

| Check | Observed | Null / threshold | Holds |
| --- | --- | --- | --- |
| b₁ (PR10 < x_c = 15.97) | +0.122 (p 0.275; n 79) | > 0 | yes |
| b₂ (PR10 ≥ x_c) | -0.059 (p 0.258; n 19) | < 0 | yes |
| spline (3 df) maximum | PR10 = 15.50 (interior) | interior | yes |
| quadratic β₂ | -0.0079 (p 0.143; vertex 18.2) | < 0 | yes |
| linear slope (all PR10) | +0.039 (p 0.537) | (rival R1) | – |
| self-repetition slope (T6) | -2.640 (p 0.388) | < 0 | yes |

**Verdict: mixed.** inverted-U signs, neither slope significant

Figure: `figures/G38_curve.pdf` (binned partial residuals and spline).

## Scorecard (period-specific axes)
<!-- SCORECARD -->
- **C (adequacy):** within-period linear vs curved not separately cross-validated (pooled CV in the card).
- **D (unfitted):** self-repetition slope -2.640 (p 0.388).
- **I (transfer):** sign pattern b₁ > 0, b₂ < 0 present.

## Notes
- 2026-10-04: prediction written before any per-period run (data: `data/processed/H33-diversity-productivity/G38/`).
- 2026-10-04: results filled by `analysis/evaluate.py` + `write_period_folders.py results`.
