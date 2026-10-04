# H33 × G17: Each agent: build your own personal website (2025-10-13 → 2025-10-20)

**Verdict:** n/a
**Role:** replication (exploratory) (round 1, non-holdout)
**Verdict (1b):** n/a (pre-#30: work-ledger zeros ambiguous; 2026-10-04)
**Period:** regime I · mode I (individual) · N = 7 at start · 5 non-holdout days with PR10 · 32 agent-days with PR10 (7 agents with ≥ 3 days) · write turns on 66% of those agent-days.

## Why this period
Eligible under the card's pre-registered rule (≥ 30 agent-days with PR10, ≥ 4 agents with ≥ 3 days, write turns on ≥ 20% of agent-days). Mode I: agents work on their own artifacts, so output is individual and diversity is less tied to coordination.

## Prediction
*Written 2026-10-04, before running on this period.* The card's predictions as they apply here (`../../README.md`).
- **Model:** log(1 + write turns) = agent FE + day FE + f(PR10) + controls (log raw chat count, log(1 + engaged minutes)); CR1 SEs clustered by agent, t(G − 1) reference.
- **P2 (per period):** two-lines at the *pooled* Robin Hood breakpoint: b₁ > 0 below it and b₂ < 0 above it. The per-period "maximum at the edge" check uses a natural spline with 3 df (4 knots), interior = between the 10th and 90th percentiles of PR10.
- **Power:** low (fewer than 60 agent-days); significance not expected even if H33 is true.
- **Expected (calibrated prior, card):** b₁ > 0, b₂ ≈ 0 (saturating), i.e. **mixed or failed** rather than supported.

**Period verdict rule (card):** supported if b₁ > 0 and b₂ < 0 with at least one significant (p < 0.05); failed if both slopes share a sign or the spline maximum is at an edge; mixed otherwise. **What would count against H33 here:** both slopes of the same sign, or the spline maximum at the edge of the period's PR10 range.

## Result
<!-- RESULT -->
Agent-days 32 · agents 7 · outcome log(1 + write turns), mean writes/agent-day 3.2.

| Check | Observed | Null / threshold | Holds |
| --- | --- | --- | --- |
| b₁ (PR10 < x_c = 15.97) | n/a (p n/a; n 31) | > 0 | n/a |
| b₂ (PR10 ≥ x_c) | n/a (p n/a; n 1) | < 0 | n/a |
| spline (3 df) maximum | PR10 = 10.12 (interior) | interior | yes |
| quadratic β₂ | -0.0186 (p 0.080; vertex 12.2) | < 0 | yes |
| linear slope (all PR10) | +0.031 (p 0.558) | (rival R1) | – |
| self-repetition slope (T6) | -0.602 (p 0.612) | < 0 | yes |

**Verdict: n/a.** fewer than 5 agent-days on one side of the pooled breakpoint

Figure: `figures/G17_curve.pdf` (binned partial residuals and spline).

## Scorecard (period-specific axes)
<!-- SCORECARD -->
- **C (adequacy):** within-period linear vs curved not separately cross-validated (pooled CV in the card).
- **D (unfitted):** self-repetition slope -0.602 (p 0.612).
- **I (transfer):** sign pattern b₁ > 0, b₂ < 0 not estimable.

## Notes
- 2026-10-04: prediction written before any per-period run (data: `data/processed/H33-diversity-productivity/G17/`).
- 2026-10-04: results filled by `analysis/evaluate.py` + `write_period_folders.py results`.
