# H110 × G31: #30 → #31 (kickoff 2026-02-16)

**Verdict:** descriptive
**Role:** exploratory (replication)
**Period:** regime I · 11 eligible agents, 1 pinned (own repo), 11 with any commit.

## Why this period
The only regime-I transition with dense DQ4 work. With one pinned agent the own-repo contrast is descriptive; the any-repo variant has no unpinned group either.

## Prediction
*Written 2026-10-04 21:31 UTC, before running on this period (card predictions applied).*
- Day-1 group persistence R₁^P (pinned, own repo) vs R₁^U (unpinned) of the field-orthogonal old-state remanence; decay ratio λ_U/λ_P. HH340: ≥ 2. Kill: within [0.8, 1.25].
- Card expectation: no clear pinning effect; per-transition groups are small, so this period's verdict is descriptive evidence and the pooled rule decides.
- Verdict rule (card): supported if both groups have ≥ 2 agents with identified pre levels and λ_U/λ_P ≥ 2; failed if λ_U/λ_P ∈ [0.8, 1.25] or R₁^P < R₁^U; descriptive if a group has < 2 agents or a pre level is not identified; mixed otherwise.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/report.py`; non-holdout).* Day-1 persistence R₁ = Σ m(day 1) / Σ m(pre) per group; m = field-orthogonal, placebo-corrected old-state remanence (H96 construction).

| Statistic | bge | gte |
| --- | --- | --- |
| pinned (own repo) / unpinned agents | 1 / 10 | 1 / 10 |
| pre level m (pinned, unpinned) | 0.67, 0.57 | 0.75, 0.71 |
| R₁ pinned / unpinned | 0.40 / 0.26 | 0.25 / 0.24 |
| decay ratio λ_U/λ_P (floor R₁ = 0.02) | 1.44 | 1.03 |
| any-repo variant R₁ pinned / unpinned (n) | 0.28 / – (11/0) | – |
| transition R₁ (all agents) | 0.28 | 0.24 |


**Verdict:** descriptive (a group has < 2 agents). Per-transition verdicts are descriptive evidence; the pooled rule decides (card).

## Scorecard (period-specific axes)
- **C:** unpinned agents at the same boundary (same kickoff, field projection, old state).
- **D:** the offset-end test is not fitted (card O3; pooled, not per transition).
- **F:** real-skeleton synthetic: the per-transition contrast is underpowered; only the pooled rule is calibrated.

## Notes
- 2026-10-04 21:31 UTC: folder and prediction written before any H110 statistic on this transition.
