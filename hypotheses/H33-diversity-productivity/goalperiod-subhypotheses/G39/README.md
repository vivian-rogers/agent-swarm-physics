# H33 × G39: Build your own interactive world! (2026-04-27 → 2026-05-04)

**Verdict:** n/a
**Role:** native (round 1b native test below) · round 1: exploratory (round 1, non-holdout)
**Verdict (1b):** n/a (< 5 agent-days above the new breakpoint; 2026-10-04)
**Period:** regime III · mode I (individual) · N = 15 at start · 5 non-holdout days with PR10 · 31 agent-days with PR10 (5 agents with ≥ 3 days) · write turns on 100% of those agent-days.

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
Agent-days 31 · agents 11 · outcome log(1 + write turns), mean writes/agent-day 38.9.

| Check | Observed | Null / threshold | Holds |
| --- | --- | --- | --- |
| b₁ (PR10 < x_c = 15.97) | n/a (p n/a; n 28) | > 0 | n/a |
| b₂ (PR10 ≥ x_c) | n/a (p n/a; n 3) | < 0 | n/a |
| spline (3 df) maximum | PR10 = 10.01 (interior) | interior | yes |
| quadratic β₂ | +0.0060 (p 0.218; vertex 17.1) | < 0 | no |
| linear slope (all PR10) | -0.050 (p 0.303) | (rival R1) | – |
| self-repetition slope (T6) | +0.249 (p 0.701) | < 0 | no |

**Verdict: n/a.** fewer than 5 agent-days on one side of the pooled breakpoint

Figure: `figures/G39_curve.pdf` (binned partial residuals and spline).

## Round 1b native test (one world per agent)
*Role of this section: native (round 1b), in addition to the round-1 replication above.*
*Prediction written 2026-10-04, before computing any #39 statistic on the round-1b tables.* In #39 each agent builds its own world, so output is cleanly attributable to the agent (14 agents with `repos_created` / `site_repos_created` rows in DQ4 `work_outcomes`, 2,232 work commits). This is the one week where an agent's diversity and its own artifact's growth can be compared across agents without shared-repo credit problems.
- **N1 (across agents):** Spearman ρ between an agent's #39 mean PR10 and its #39 work commits, and with distinct files: |ρ| < 0.55 (n.s. at N ≈ 14); a quadratic in mean PR10 across agents has an n.s. negative term.
- **N2 (within agent):** the within-agent PR10 slope on log(1 + work commits) in #39 alone is n.s.
- Counts against: ρ ≥ 0.55 with p < 0.05 (a cross-agent diversity–output link that day-level FE hide).

**Result (round 1b native, run 2026-10-04; `native.json` → `G39`).** 10 agents with ≥ 2 PR10 days.
- **N1 holds:** Spearman ρ(mean PR10, work commits) +0.10 (p 0.78), with distinct files +0.19 (p 0.60); across-agent quadratic +0.23 (p 0.15, positive: no inverted U).
- **N2 holds:** within-agent slope −0.028 (p 0.83).
- When each agent builds its own world, the agents with more varied chat do not build more. Verdict for the native test: **supported** (H33's null reading; the hypothesis itself is not supported here).

## Scorecard (period-specific axes)
<!-- SCORECARD -->
- **C (adequacy):** within-period linear vs curved not separately cross-validated (pooled CV in the card).
- **D (unfitted):** self-repetition slope +0.249 (p 0.701).
- **I (transfer):** sign pattern b₁ > 0, b₂ < 0 not estimable.

## Notes
- 2026-10-04: prediction written before any per-period run (data: `data/processed/H33-diversity-productivity/G39/`).
- 2026-10-04: results filled by `analysis/evaluate.py` + `write_period_folders.py results`.
