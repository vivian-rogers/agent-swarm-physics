# H33 × G33: Discuss, debate, and act on your views about the recent Pentagon-AI company news (2026-03-02 → 2026-03-05)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout)
**Period:** regime II · mode C (shared objective) · N = 12 at start · 3 non-holdout days with PR10 · 31 agent-days with PR10 (10 agents with ≥ 3 days) · write turns on 97% of those agent-days.

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
Agent-days 31 · agents 11 · outcome log(1 + write turns), mean writes/agent-day 27.9.

| Check | Observed | Null / threshold | Holds |
| --- | --- | --- | --- |
| b₁ (PR10 < x_c = 15.97) | -0.076 (p 0.012; n 18) | > 0 | no |
| b₂ (PR10 ≥ x_c) | +0.165 (p 0.360; n 13) | < 0 | no |
| spline (3 df) maximum | PR10 = 7.86 (edge) | interior | no |
| quadratic β₂ | +0.0045 (p 0.688; vertex 24.2) | < 0 | no |
| linear slope (all PR10) | -0.103 (p 0.067) | (rival R1) | – |
| self-repetition slope (T6) | -1.599 (p 0.561) | < 0 | yes |

**Verdict: failed.** spline maximum at the edge of the period's PR10 range (U-shaped signs)

Figure: `figures/G33_curve.pdf` (binned partial residuals and spline).

## Scorecard (period-specific axes)
<!-- SCORECARD -->
- **C (adequacy):** within-period linear vs curved not separately cross-validated (pooled CV in the card).
- **D (unfitted):** self-repetition slope -1.599 (p 0.561).
- **I (transfer):** sign pattern b₁ > 0, b₂ < 0 absent.

## Notes
- 2026-10-04: prediction written before any per-period run (data: `data/processed/H33-diversity-productivity/G33/`).
- 2026-10-04: results filled by `analysis/evaluate.py` + `write_period_folders.py results`.
