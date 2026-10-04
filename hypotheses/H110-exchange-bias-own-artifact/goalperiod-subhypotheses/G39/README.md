# H110 × G39: #38 → #39 (kickoff 2026-04-27, the room reshuffle)

**Verdict:** descriptive
**Role:** exploratory (native)
**Period:** regime III · 13 eligible, 1 pinned (own) / 12; 7 with any commit.

## Why this period
The own-repo contrast is one-sided; the native uses H100's movers and stayers split by whether they kept committing to a #38 repo after 04-27 (H96's own-room domain memory). Not blind: H100 reported GPT-5.4's carry.

## Prediction
*Written 2026-10-04 21:31 UTC, before running on this period (card predictions applied).*
- Day-1 group persistence R₁^P (pinned, own repo) vs R₁^U (unpinned) of the field-orthogonal old-state remanence; decay ratio λ_U/λ_P. HH340: ≥ 2. Kill: within [0.8, 1.25].
- Card expectation: no clear pinning effect; per-transition groups are small, so this period's verdict is descriptive evidence and the pooled rule decides.
- Native: agents who kept committing to a #38 repo after 04-27 keep a larger own-room memory (Δ_1 own − other room) than agents who did not, in both models [0.35]. Descriptive if a group has < 2 agents.
- Verdict rule (card): supported if both groups have ≥ 2 agents with identified pre levels and λ_U/λ_P ≥ 2; failed if λ_U/λ_P ∈ [0.8, 1.25] or R₁^P < R₁^U; descriptive if a group has < 2 agents or a pre level is not identified; mixed otherwise.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/report.py`; non-holdout).* Day-1 persistence R₁ = Σ m(day 1) / Σ m(pre) per group; m = field-orthogonal, placebo-corrected old-state remanence (H96 construction).

| Statistic | bge | gte |
| --- | --- | --- |
| pinned (own repo) / unpinned agents | 1 / 12 | 1 / 12 |
| pre level m (pinned, unpinned) | 0.15, 0.28 | 0.30, 0.34 |
| R₁ pinned / unpinned | -3.79 / -0.30 | 0.39 / 0.09 |
| decay ratio λ_U/λ_P (floor R₁ = 0.02) | 1.00 | 2.56 |
| any-repo variant R₁ pinned / unpinned (n) | -0.45 / -0.44 (7/6) | – |
| transition R₁ (all agents) | -0.44 | 0.11 |

**Native (own-room memory by continued #38-repo commits):** only 1 veteran kept committing to a #38 repo on days 1–3 (12 did not). Descriptive.

**Verdict:** descriptive (native: < 2 agents kept committing to a #38 repo). Per-transition verdicts are descriptive evidence; the pooled rule decides (card).

## Scorecard (period-specific axes)
- **C:** unpinned agents at the same boundary (same kickoff, field projection, old state).
- **D:** the offset-end test is not fitted (card O3; pooled, not per transition).
- **F:** real-skeleton synthetic: the per-transition contrast is underpowered; only the pooled rule is calibrated.

## Notes
- 2026-10-04 21:31 UTC: folder and prediction written before any H110 statistic on this transition.
