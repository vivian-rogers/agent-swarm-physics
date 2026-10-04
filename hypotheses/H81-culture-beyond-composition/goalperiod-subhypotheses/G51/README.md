# H81 × G51: Private roles (2026-07-06 → 2026-09-04 non-holdout; tail held out)

**Verdict:** failed
**Role:** native
**Period:** regime III · private goals (NE26) · 21 → 32 agents · rooms #general (+ #focus from 08-05; isolated onboarding rooms 07-09/10) · about 40 active non-holdout days. Splits inside: roster joins (51b–51l), NE38 (07-29), NE43 (08-05, 08-21), rooms (08-05, 08-24). The #51 tail (09-07 →) is held out.

## Why this period
The longest goal period (two months) and the only one where each agent has its own exogenous field (its `agent_goal`), which can be projected out per agent. A village-level slow mode inside one goal period is the cleanest culture test: the period kickoff is fixed for weeks, and the population grows by 11 agents.

## Prediction
*Written 2026-10-04 20:05 UTC (card), copied here 2026-10-04 20:18 UTC, before running on this period.*
- Statistic: cross-agent lagged residual alignment L_slow = mean L(k), k = 5–15 active days, with residuals r_{i,d} = Π_{51,i}(v_{i,d} − m_i) (period kickoff, room kickoffs, human centroid and the agent's own goal removed; m_i the agent's #51 mean).
- **Prediction (HH293):** L_slow above the 95th percentile of the per-agent circular-shift null (offset ≥ 5 days), in both models and without Gemini 2.5 Pro.
- **Against:** L_slow inside the null band. Prior 0.3.
- Equal-time L(0) is reported but is not a culture statistic (day fields and contemporaneous convergence).

## Result
*Run 2026-10-04 20:27 UTC (`analysis/natives.py`); post hoc power check in `analysis/posthoc.py`.*

| Quantity | bge | gte | Null (circular shift, 1,000 draws) |
| --- | --- | --- | --- |
| L_slow (k = 5–15 active days) | −0.0051 | −0.0035 | 5–95%: [−0.0018, +0.0012] |
| L(0) equal time | 0.046 | 0.053 | — |
| L(1), L(2), L(3), L(4) | 0.025, 0.016, 0.012, 0.007 | 0.029, 0.017, 0.009, 0.004 | ≈ 0 |
| L_slow without Gemini 2.5 Pro | −0.0050 | −0.0030 | [−0.0019, +0.0014] |

45 active days, 29 agents. **N1 failed:** there is no positive cross-agent alignment at lags of 5–15 active days. A common mode exists but is short: the cross-agent lagged alignment falls from 0.046 at equal time to ≈ 0 at 5 days (correlation time ≈ 2 active days). The negative long-lag values are the within-period demeaning constraint (each agent's series sums to zero), not anti-alignment. The post hoc power check (card, PH3) reads what this native could have seen.

Replication (κ, equal time): see the card's Results; #51 is one of the 9 regime-III points.

## Scorecard (period-specific axes)
- C: L_slow inside/below the circular-shift band (no slow mode at 5–15 days).
- D: the short common mode (τ ≈ 2 active days) is an unfitted signature of day-scale fields, not of culture.

## Notes
- Within-period demeaning removes each agent's level, not its own drift; the circular-shift null keeps each agent's drift and destroys cross-agent timing.
