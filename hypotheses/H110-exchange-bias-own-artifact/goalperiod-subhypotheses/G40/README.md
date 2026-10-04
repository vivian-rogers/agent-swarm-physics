# H110 × G40: #39 → #40 (kickoff 2026-05-04, continuation into the merged room)

**Verdict:** mixed
**Role:** exploratory (native)
**Period:** regime III · 15 eligible, 14 pinned / 1 unpinned.

## Why this period
A continuation boundary (NE34: 78% continuation) with nearly everyone pinned: the own-repo contrast is one-sided, so the native tests the second half of HH340: pinned agents who keep committing to the old own repo after the kickoff vs those who stop. Not blind: H96 reported R₁ 1.43 here.

## Prediction
*Written 2026-10-04 21:31 UTC, before running on this period (card predictions applied).*
- Day-1 group persistence R₁^P (pinned, own repo) vs R₁^U (unpinned) of the field-orthogonal old-state remanence; decay ratio λ_U/λ_P. HH340: ≥ 2. Kill: within [0.8, 1.25].
- Card expectation: no clear pinning effect; per-transition groups are small, so this period's verdict is descriptive evidence and the pooled rule decides.
- Native: continuing pinned agents' mean offset over days 1–3 exceeds the stopping pinned agents' (bootstrap CI > 0) [0.3]; offset measured against the stopping group when no unpinned group exists. Groups (fixed 2026-10-04 21:40 UTC, before running): *continuing* = commits to a pinned own repo on ≥ 2 of days 1–3 after the kickoff; *stopping* = pinned, no commit to a pinned repo on days 1–3. Statistic: mean m over days 1–3, continuing − stopping, agent bootstrap.
- Verdict rule (card): supported if both groups have ≥ 2 agents with identified pre levels and λ_U/λ_P ≥ 2; failed if λ_U/λ_P ∈ [0.8, 1.25] or R₁^P < R₁^U; descriptive if a group has < 2 agents or a pre level is not identified; mixed otherwise.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/report.py`; non-holdout).* Day-1 persistence R₁ = Σ m(day 1) / Σ m(pre) per group; m = field-orthogonal, placebo-corrected old-state remanence (H96 construction).

| Statistic | bge | gte |
| --- | --- | --- |
| pinned (own repo) / unpinned agents | 14 / 1 | 14 / 1 |
| pre level m (pinned, unpinned) | 0.25, 0.34 | 0.33, 0.61 |
| R₁ pinned / unpinned | 1.32 / 1.29 | 1.33 / 1.06 |
| decay ratio λ_U/λ_P (floor R₁ = 0.02) | – | – |
| any-repo variant R₁ pinned / unpinned (n) | 1.32 / 1.29 (14/1) | – |
| transition R₁ (all agents) | 1.32 | 1.30 |

**Native (continuing vs stopping pinned agents, days 1–3):** continuing 4 (agents [12, 14, 20, 22]), stopping 4 (agents [6, 10, 17, 24]). Mean m continuing − stopping: -0.013 [-0.213, 0.180] (bge); -0.080 [-0.297, 0.130] (gte). No offset tied to continued commits.

**Verdict:** mixed (native: continuing − stopping ≈ 0 with a CI on both sides (replication contrast descriptive: 1 unpinned agent)). Per-transition verdicts are descriptive evidence; the pooled rule decides (card).

## Scorecard (period-specific axes)
- **C:** unpinned agents at the same boundary (same kickoff, field projection, old state).
- **D:** the offset-end test is not fitted (card O3; pooled, not per transition).
- **F:** real-skeleton synthetic: the per-transition contrast is underpowered; only the pooled rule is calibrated.

## Notes
- 2026-10-04 21:31 UTC: folder and prediction written before any H110 statistic on this transition.
