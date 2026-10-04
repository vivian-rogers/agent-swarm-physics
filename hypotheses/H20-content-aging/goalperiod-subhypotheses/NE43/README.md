# H20 × NE43: the operator's drives are withdrawn in two steps inside #51 (bookends stop 2026-08-05, nudges stop 2026-08-21)

**Verdict:** mixed (round 1b native; dip inside placebo band)
**Role:** native (round 1b, 2026-10-04; transition exception c)
**Period:** #51 head, non-holdout days 2026-07-06 → 2026-09-04 (d = 1–45). Regime III, one room (plus #focus from 08-05), private per-agent goals, roster 21 → 32. Step 1: daily pause/resume bookends end after 08-04 PT (none from 08-05). Step 2: nudges end after 08-20 (none from 08-21). Both are undocumented in the CHANGELOG (found by H39 / H35 / DQ9).

## Why this period
Aging and its rival "settle quickly, then stationary" both say what should happen when an external drive is withdrawn at fixed goal, room and hours. Glassy aging predicts rejuvenation only if the perturbation resets the content state; a field-pinned stationary state (round 1; H54: private goals pin content with no decay over nine weeks) predicts no break in content correlation when drives that act on *activity* (when agents run) stop. Round 1 pooled four #51 step dates into one rejuvenation statistic (none found); NE43's two drive steps were not separated.

## Design (round 1b)
- Agent-day states and C(d, d′) as in round 1 (n = 32, ≥ 8 statements per agent-day), both models, shared goal vectors.
- **Step statistic** R_k: mean residual from the period's fitted stationary M0 of pairs straddling step k (d < k ≤ d′) minus non-straddling pairs at the same lags (lag-weighted). Negative R_k = correlation broken across the step (rejuvenation / regime change).
- **Null:** the Amendment-2 stationary swarm model (estimated latent shapes, real counts), 500 draws, the same R_k; one-sided p_lower = P(R_null ≤ R_obs). **Placebo:** R at every other #51 day boundary with ≥ 5 days on each side (its distribution shows how often ordinary boundaries look like steps).
- Also on V-c (swarm-common removed).

## Prediction
*Written 2026-10-04 07:25 UTC, before computing any per-step statistic. Seen before: round 1's pooled S5 for #51 (straddling-pair M1 residual +0.007, p_lower 0.81) and G51's lag-1 correlations by t_w (one dip at t_w = 10, 0.73).*
- **N3a (bookends, 08-05).** No break: R inside the null's 5–95% band (p_lower ≥ 0.05) in both models. Credence 0.7.
- **N3b (nudges, 08-21).** No break, same rule. Credence 0.7.
- **Verdict rule (native, read for H20's aging claim):** **failed** (no rejuvenation when the drives stop; content order is not drive-held, consistent with round 1's field-pinned stationary state) if N3a and N3b hold in both models; **mixed** (a rejuvenation-like break, which aging allows but a regime change explains as well) if either step breaks correlation (p_lower < 0.05 in both models and R below the placebo's 5th percentile); otherwise **mixed** (model-dependent).

## Result
*Run 2026-10-04 after the prediction. Data: `data/processed/H20-content-aging/r1b/natives_<model>.json` (NE43). Script: `analysis/natives_r1b.py`.*

| Step | R, bge / gte | stationary null (Amendment 2): p_lower, bge / gte | null 5–95% | placebo (33 ordinary #51 boundaries): q05, share at least as low |
| --- | --- | --- | --- | --- |
| bookends end (08-05) | −0.022 / −0.022 | 0.016 / 0.008 | −0.016 to +0.017 | −0.029 / −0.031; 21% / 24% |
| nudges end (08-21) | +0.021 / +0.019 | 0.95 / 0.94 | −0.021 to +0.022 | 79–82% |
| swarm-common removed, bookends | −0.022 / −0.020 | 0.020 / 0.010 | | 21% |

- **N3a fails** in both models (p_lower < 0.05 at the bookend step), but the break criterion also fails: R sits inside the placebo distribution of ordinary #51 day boundaries (about one in five looks at least as broken). **N3b holds** (no break when the nudger stops).
- **Reading.** Content correlation across 08-05 dips by about 0.02 (3% of C), which the fitted stationary null calls significant, but ordinary #51 days produce dips of this size routinely: the stationary null is too narrow for boundary statistics (it has no day-specific events such as joins, the #focus room opening on 08-05 itself, or human messages). Withdrawing the nudger leaves content correlation unchanged. Neither step rejuvenates content in a way aging would need; drives that act on *when* agents run do not hold content order.
- **Verdict (pre-registered rule): mixed** (the "otherwise" branch: N3a fails without meeting the break criterion).

## Notes
- 2026-10-04: native folder created in round 1b. `period_units` has no split at NE43 (51g spans both steps); the steps are taken from DQ9 / `kicks_classified`.
