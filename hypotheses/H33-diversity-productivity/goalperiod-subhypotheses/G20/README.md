# H33 × G20: Start a Substack and join the blogosphere (2025-11-17 → 2025-12-01)

**Verdict:** failed
**Role:** replication (exploratory) (round 1, non-holdout)
**Verdict (1b):** n/a (pre-#30: work-ledger zeros ambiguous; 2026-10-04)
**Period:** regime I · mode I (individual) · N = 8 at start · 10 non-holdout days with PR10 · 87 agent-days with PR10 (10 agents with ≥ 3 days) · write turns on 24% of those agent-days.

## Why this period
Eligible under the card's pre-registered rule (≥ 30 agent-days with PR10, ≥ 4 agents with ≥ 3 days, write turns on ≥ 20% of agent-days). Mode I: agents work on their own artifacts, so output is individual and diversity is less tied to coordination.

## Prediction
*Written 2026-10-04, before running on this period.* The card's predictions as they apply here (`../../README.md`).
- **Model:** log(1 + write turns) = agent FE + day FE + f(PR10) + controls (log raw chat count, log(1 + engaged minutes)); CR1 SEs clustered by agent, t(G − 1) reference.
- **P2 (per period):** two-lines at the *pooled* Robin Hood breakpoint: b₁ > 0 below it and b₂ < 0 above it. The per-period "maximum at the edge" check uses a natural spline with 3 df (4 knots), interior = between the 10th and 90th percentiles of PR10.
- **Power:** modest; significance of one slope possible if the effect is ≥ 0.4 residual SD (synthetic).
- **Expected (calibrated prior, card):** b₁ > 0, b₂ ≈ 0 (saturating), i.e. **mixed or failed** rather than supported.

**Period verdict rule (card):** supported if b₁ > 0 and b₂ < 0 with at least one significant (p < 0.05); failed if both slopes share a sign or the spline maximum is at an edge; mixed otherwise. **What would count against H33 here:** both slopes of the same sign, or the spline maximum at the edge of the period's PR10 range.

## Result
<!-- RESULT -->
Agent-days 87 · agents 10 · outcome log(1 + write turns), mean writes/agent-day 1.6.

| Check | Observed | Null / threshold | Holds |
| --- | --- | --- | --- |
| b₁ (PR10 < x_c = 15.97) | -0.007 (p 0.885; n 78) | > 0 | no |
| b₂ (PR10 ≥ x_c) | +0.178 (p 0.327; n 9) | < 0 | no |
| spline (3 df) maximum | PR10 = 7.66 (edge) | interior | no |
| quadratic β₂ | +0.0035 (p 0.722; vertex 15.9) | < 0 | no |
| linear slope (all PR10) | -0.026 (p 0.585) | (rival R1) | – |
| self-repetition slope (T6) | -0.597 (p 0.514) | < 0 | yes |

**Verdict: failed.** spline maximum at the edge of the period's PR10 range (U-shaped signs)

Figure: `figures/G20_curve.pdf` (binned partial residuals and spline).

## Scorecard (period-specific axes)
<!-- SCORECARD -->
- **C (adequacy):** within-period linear vs curved not separately cross-validated (pooled CV in the card).
- **D (unfitted):** self-repetition slope -0.597 (p 0.514).
- **I (transfer):** sign pattern b₁ > 0, b₂ < 0 absent.

## Notes
- 2026-10-04: prediction written before any per-period run (data: `data/processed/H33-diversity-productivity/G20/`).
- 2026-10-04: results filled by `analysis/evaluate.py` + `write_period_folders.py results`.
