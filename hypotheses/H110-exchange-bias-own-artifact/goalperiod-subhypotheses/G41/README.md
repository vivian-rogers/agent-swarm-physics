# H110 × G41: #40 → #41 (kickoff 2026-05-11, the NE42 split)

**Verdict:** failed
**Role:** exploratory (replication)
**Period:** regime III · 15 eligible, 4 pinned / 11 unpinned.

## Why this period
Balanced enough; H96 found a full quench here (R₁ −0.28).

## Prediction
*Written 2026-10-04 21:31 UTC, before running on this period (card predictions applied).*
- Day-1 group persistence R₁^P (pinned, own repo) vs R₁^U (unpinned) of the field-orthogonal old-state remanence; decay ratio λ_U/λ_P. HH340: ≥ 2. Kill: within [0.8, 1.25].
- Card expectation: no clear pinning effect; per-transition groups are small, so this period's verdict is descriptive evidence and the pooled rule decides.
- Verdict rule (card): supported if both groups have ≥ 2 agents with identified pre levels and λ_U/λ_P ≥ 2; failed if λ_U/λ_P ∈ [0.8, 1.25] or R₁^P < R₁^U; descriptive if a group has < 2 agents or a pre level is not identified; mixed otherwise.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/report.py`; non-holdout).* Day-1 persistence R₁ = Σ m(day 1) / Σ m(pre) per group; m = field-orthogonal, placebo-corrected old-state remanence (H96 construction).

| Statistic | bge | gte |
| --- | --- | --- |
| pinned (own repo) / unpinned agents | 4 / 11 | 4 / 11 |
| pre level m (pinned, unpinned) | 0.41, 0.57 | 0.48, 0.59 |
| R₁ pinned / unpinned | -0.60 / -0.23 | -0.47 / -0.18 |
| decay ratio λ_U/λ_P (floor R₁ = 0.02) | 1.00 | 1.00 |
| any-repo variant R₁ pinned / unpinned (n) | -0.44 / 0.43 (12/3) | – |
| transition R₁ (all agents) | -0.30 | -0.24 |


**Verdict:** failed (pinned agents keep less of the old state). Per-transition verdicts are descriptive evidence; the pooled rule decides (card).

## Scorecard (period-specific axes)
- **C:** unpinned agents at the same boundary (same kickoff, field projection, old state).
- **D:** the offset-end test is not fitted (card O3; pooled, not per transition).
- **F:** real-skeleton synthetic: the per-transition contrast is underpowered; only the pooled rule is calibrated.

## Notes
- 2026-10-04 21:31 UTC: folder and prediction written before any H110 statistic on this transition.
