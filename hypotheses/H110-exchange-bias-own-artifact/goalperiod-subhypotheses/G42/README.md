# H110 × G42: #41 → #42 (kickoff 2026-05-18)

**Verdict:** failed
**Role:** exploratory (replication)
**Period:** regime III · 15 eligible, 9 pinned / 6 unpinned.

## Why this period
Balanced contrast; H96 found a residual (R₁ 0.48).

## Prediction
*Written 2026-10-04 21:31 UTC, before running on this period (card predictions applied).*
- Day-1 group persistence R₁^P (pinned, own repo) vs R₁^U (unpinned) of the field-orthogonal old-state remanence; decay ratio λ_U/λ_P. HH340: ≥ 2. Kill: within [0.8, 1.25].
- Card expectation: no clear pinning effect; per-transition groups are small, so this period's verdict is descriptive evidence and the pooled rule decides.
- Verdict rule (card): supported if both groups have ≥ 2 agents with identified pre levels and λ_U/λ_P ≥ 2; failed if λ_U/λ_P ∈ [0.8, 1.25] or R₁^P < R₁^U; descriptive if a group has < 2 agents or a pre level is not identified; mixed otherwise.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/report.py`; non-holdout).* Day-1 persistence R₁ = Σ m(day 1) / Σ m(pre) per group; m = field-orthogonal, placebo-corrected old-state remanence (H96 construction).

| Statistic | bge | gte |
| --- | --- | --- |
| pinned (own repo) / unpinned agents | 9 / 6 | 9 / 6 |
| pre level m (pinned, unpinned) | 0.27, 0.23 | 0.20, 0.13 |
| R₁ pinned / unpinned | 0.24 / 0.56 | 0.09 / 0.36 |
| decay ratio λ_U/λ_P (floor R₁ = 0.02) | 0.41 | 0.44 |
| any-repo variant R₁ pinned / unpinned (n) | 0.31 / -17.00 (13/2) | – |
| transition R₁ (all agents) | 0.36 | 0.17 |


**Verdict:** failed (pinned agents keep less of the old state). Per-transition verdicts are descriptive evidence; the pooled rule decides (card).

## Scorecard (period-specific axes)
- **C:** unpinned agents at the same boundary (same kickoff, field projection, old state).
- **D:** the offset-end test is not fitted (card O3; pooled, not per transition).
- **F:** real-skeleton synthetic: the per-transition contrast is underpowered; only the pooled rule is calibrated.

## Notes
- 2026-10-04 21:31 UTC: folder and prediction written before any H110 statistic on this transition.
