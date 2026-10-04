# H39 × NE42: #best and #rest merged (05-04) and split back (05-11)

**Verdict:** mixed
**Role:** exploratory (round 1, non-holdout; spanning test)
**Period:** see Prediction for the windows; non-holdout days only.

## Why this test
Room changes alter who an agent hears: a candidate field toward or away from chat.

## Prediction
*Written 2026-10-04 (UTC), before running this test.* P6 (card): the merge (05-04, kickoff #39 → #40) gives Δπ_chat > 0 and the split (05-11, #40 → #41) gives Δπ_chat < 0 on B4 (more or fewer interlocutors). Both are kickoff-confounded; expected inconclusive: neither step above the regime-III placebo p95 for φ, and neither K outside the placebo band. Compared descriptively with the other regime-III kickoffs (#37 → #38, #38 → #39, #41 → #42).

## Result
**Step K39-40** (kickoff #39 -> #40; pre 2026-04-30, 2026-05-01 → post 2026-05-04, 2026-05-05; 15 agents in the balanced panel; placebo pool: era III-4h, n = 12).

| State family | class | φ (percentile in placebo) | K (percentile) | Δπ |
| --- | --- | --- | --- | --- |
| behavior B4 | **neither** | 0.154 (67) | +0.089 (92) | work -0.020, chat +0.039, idle -0.030, consolidate +0.010 |
| content C6 | **neither** | 1.348 (92) | +0.570 (83) | (clusters) |

Flag: NE42 merge (05-04).

**Step K40-41** (kickoff #40 -> #41; pre 2026-05-07, 2026-05-08 → post 2026-05-11, 2026-05-12; 15 agents in the balanced panel; placebo pool: era III-4h, n = 12).

| State family | class | φ (percentile in placebo) | K (percentile) | Δπ |
| --- | --- | --- | --- | --- |
| behavior B4 | **both** | 0.278 (100) | +0.102 (100) | work -0.107, chat +0.021, idle +0.107, consolidate -0.021 |
| content C6 | **neither** | 1.142 (83) | +1.108 (92) | (clusters) |

Flag: NE42 split (05-11).

P6: merge Δπ_chat +0.039 (predicted > 0: ✓, not beyond placebo); split Δπ_chat +0.021 (predicted < 0: ✗). The split is flagged beyond the regime-III day-boundary placebo (B4 'both'), but so are 4 of the other regime-III kickoffs, so the room change is not separable from the goal change. **Inconclusive**, as predicted for significance; the split's chat sign is wrong.

## Notes
- Run 2026-10-04; placebos are within-goal day boundaries of the same era (regime × hours) and window shape, excluding ±1 day around the tested scaffold steps.
