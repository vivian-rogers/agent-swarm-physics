# H82 × NE32: Newcomers in isolated rooms (2026-07-09)

**Verdict:** mixed
**Role:** native
**Period:** regime III, goal #51 · GPT-5.6 Sol, Terra, Luna join on 07-09 in separate isolated rooms (closed 07-10); Grok 4.5 joins 07-10 in an onboarding room. Goals #45–#50 are held out, so the village history they never saw is #36–#44 (non-holdout).

## Why this period
Four agents that never saw any regime-III goal period before #51. Any alignment of their first-day content with the #36–#44 village history beyond their own goal, their family prior and the #51 fields would have to come through the record (history search, documents), not through memory.

## Prediction
*Written 2026-10-04 20:07 UTC (card), copied here 2026-10-04 20:19 UTC, before running on this period.*
- Regression of days 1–5 of each newcomer's tenure on the #51 kickoff and goal, room kickoffs, the day's human centroid, its own `agent_goal`, its family prior (mean of same-lab agents' regime-III priors) and the history centroid H (all non-holdout #36–#44 agent-days). Δγ_hist = γ[H] − median γ[single-period centroids #36 … #44]. Incumbents (present in #44) on the same days with their own priors are the reference.
- **Prediction (HH290):** Δγ_hist,new > 0 and ≥ ½ of the incumbents' Δγ_hist.
- **Against:** Δγ_hist,new ≤ 0. Prior 0.2.

## Result
*Run 2026-10-04 20:35 UTC (`analysis/natives.py`).* Days 07-09 → 07-16; newcomers present with eligible days: 35, 36, 37 (17 agent-days; Grok 4.5 has no same-lab incumbent, so no family prior); incumbents present in #44 (102 agent-days).

| Quantity | bge [95% agent bootstrap] | gte |
| --- | --- | --- |
| newcomers Δγ_hist | +0.036 [+0.006, +0.081] | +0.010 [−0.020, +0.039] |
| incumbents Δγ_hist | −0.036 [−0.077, +0.018] | −0.033 [−0.081, +0.017] |
| newcomers − incumbents | +0.072 [+0.022, +0.125] | +0.043 [−0.019, +0.087] |

**Mixed:** in bge the isolated newcomers load on the regime-III history (#36–#44) they never saw, slightly more than incumbents do; in gte the CI includes 0. The effect is small and rests on three agents from one family. The family prior and the #51 village centroid are both regressors, so the loading is beyond what the newcomers' lab-mates and the current village write.

## Scorecard (period-specific axes)
- C: weak positive in one model.
- G: three agents of one family; incumbents' own history loading is ≈ 0, which the prediction did not expect.

## Notes
