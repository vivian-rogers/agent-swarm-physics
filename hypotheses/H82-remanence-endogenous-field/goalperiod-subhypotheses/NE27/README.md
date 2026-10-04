# H82 × NE27: Batch join at the #10 kickoff (2025-08-18)

**Verdict:** failed
**Role:** native
**Period:** regime I · goal #10 starts 2025-08-18 with three new agents (GPT-5, Grok 4, Claude Opus 4.1; empty memories) joining four veterans · N 4 → 7. The previous goal #9 (08-13 → 08-17) is held out, so the endogenous field is the #8 centroid (older village history, about one week back).

## Why this period
The only boundary in the data where several agents with empty memories start on a goal's day 1 next to veterans. If remanence lives in the record (HH290), newcomers carry it as much as veterans do; if it lives in members, only veterans do.

## Prediction
*Written 2026-10-04 20:07 UTC (card), copied here 2026-10-04 20:19 UTC, before running on this period.*
- Regression of the day-d vectors (d = 1–3 of #10) on the #10 kickoff and goal, the day's human-message centroid, the previous kickoff (#9 is held out, so #8's kickoff), the agent prior (leaving out #8 and #10) and the #8 centroid split by veteran / newcomer. Δγ = γ[#8] − median γ[placebo regime-I centroids].
- **Prediction (HH290):** Δγ_vet > 0 and Δγ_new ≥ ½ Δγ_vet.
- **Against:** Δγ_new ≤ 0 (memory, not the record). Prior 0.2.
- Newcomers have priors only from their later periods (≥ 3 days, leaving #8 and #10 out).

## Result
*Run 2026-10-04 20:35 UTC (`analysis/natives.py`).* Days 1–3 of #10 (2025-08-18 → 08-20), 4 veterans and 3 newcomers each day.

| Term | bge Δγ (days 1–3 mean) | bge RE [95%] | gte Δγ | gte RE [95%] |
| --- | --- | --- | --- | --- |
| veterans (Δγ_vet) | −0.035 | −0.019 [−0.131, +0.093] | +0.025 | +0.021 [−0.058, +0.101] |
| newcomers (Δγ_new) | +0.005 | −0.023 [−0.115, +0.069] | +0.049 | +0.066 [−0.003, +0.135] |

**Failed:** veterans carry no trace of the #8 village centroid across the held-out #9 week (lag about one week), so the newcomer contrast has nothing to compare. Newcomers are not below veterans in either model.

## Scorecard (period-specific axes)
- C: no excess over regime-I placebo centroids for either group.
- E: the empty-memory batch join does not separate record from members here, because the lag-2 trace is absent.

## Notes
