# H99 × NE14: regime II → III inside goal #36 (2026-03-23 → 03-27)

**Verdict:** descriptive
**Role:** native (exploratory)
**Period:** goal #36 · 12 agents, two rooms · unit 36a (regime II, 1 day) → 36b, 36c (regime III, perma-computer-use and forced 41-turn resets, NE14 + NE41, then NE16).

## Why this period
H67 found that read-out talk coupling switches on at the regime II → III boundary at roughly fixed call cadence. A coupling delayed by one call reads as Δg₂ > 0 in the synthetic (delayed world: 0.97 at τ₀ = 1 min). The boundary is inside one goal, so the goal field is held fixed.

## Prediction
*Written 2026-10-04 20:42 UTC, before running on these units (Amendment A1 rule).*
- **NE14-a.** In 36b and 36c the talk Δg₂ is ≥ 0, and its point estimate exceeds 36a's. [0.4]
- **NE14-b.** 36a (235 trimmed minutes) has no resolved g_χ (CI includes 0): its verdict is descriptive. [0.5]
- *Against:* Δg₂ in 36b–c below 36a's, or a fast-field call in 36b–c.
- Power is low: one regime-II day.

## Result
Talk channel (data: `natives/ne14.json`).

| Unit | regime | trimmed min | g_χ [95%] | Δρ₁ [95%] | Δρ₂ [95%] | A2 call |
| --- | --- | --- | --- | --- | --- | --- |
| 36a | II | 235 | 0.139 [−0.038, 0.251] | 0.046 [−0.037, 0.078] | 0.060 [−0.007, 0.143] | unresolved |
| 36b | III | 471 | 0.124 [−0.036, 0.264] | 0.011 [−0.051, 0.073] | 0.066 [−0.008, 0.126] | unresolved |
| 36c | III | 478 | 0.226 [0.067, 0.329] | 0.137 [0.017, 0.244] | 0.093 [−0.019, 0.188] | slow |

- **NE14-b supported:** 36a has no resolved gain.
- **NE14-a holds in point estimates only:** Δρ₂ is 0.066 and 0.093 in regime III against 0.060 in regime II; every CI overlaps. 36c, after NE16, carries the first resolved slow call.
- With one regime-II day the boundary is not resolved. Descriptive.

## Scorecard (period-specific axes)
E (scaffold step inside one goal).

## Notes
