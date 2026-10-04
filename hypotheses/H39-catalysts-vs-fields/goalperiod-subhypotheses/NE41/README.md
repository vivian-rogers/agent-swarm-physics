# H39 × NE41: Forced context erasure at the 41-turn consolidation cap (regime III)

**Verdict:** failed
**Role:** exploratory (round 1, non-holdout; spanning test)
**Period:** see Prediction for the windows; non-holdout days only.

## Why this test
A context erasure removes the session channel at a scaffold-set time (H15): a lever the operator controls through the cap.

## Prediction
*Written 2026-10-04 (UTC), before running this test.* P4 (card), pooled over the regime-III periods G37–G42, G44, G51 (per-period numbers in the G folders):
- B6: after a forced erasure (CF) the agent browses/looks more and types/shells less: pooled Δπ_browse > 0 and Δπ_type + Δπ_shell < 0 with CIs excluding 0 (H15's write dip).
- B4: |K| < 0.10 (no catalysis). The consolidate state is mechanically depleted right after a consolidation and is not interpreted.
- CF and CV (voluntary) give the same class.
- Design: episode = a CF (CV) event with no kick or other consolidation in the 10 min before; s0 = the last non-consolidate state before it; controls = matched minutes ≥ 10 min after the agent's last consolidation; both arms cut at the next kick or consolidation.

## Result
Pooled over the regime-III periods (per-period rows in the G folders). Run 2026-10-04.

| Chain | class (A1 rule) | K pooled [95% CI] | mean φ_exc | Δπ pooled |
| --- | --- | --- | --- | --- |
| CF, B4 full | field | +0.242 [-0.02, +0.50] | 0.390 | work +0.165, chat +0.009, idle +0.018, consolidate -0.194 |
| CF, B4 without consolidate (A2) | both | -0.148 [-0.22, -0.08] | 0.353 | work +0.128, chat -0.003, idle -0.126 |
| CF, B6 full | both | +0.393 [+0.11, +0.67] | 0.379 | browse +0.056, type +0.036, shell +0.059, chat +0.011, idle +0.020, consolidate -0.197 |
| CF, B6 without consolidate (A2) | field | -0.034 [-0.09, +0.02] | 0.406 | browse +0.063, type +0.065, shell -0.002, chat +0.002, idle -0.134 |
| CV, B4 full | both | +0.356 [+0.12, +0.59] | 0.539 | work +0.163, chat +0.025, idle +0.082, consolidate -0.291 |
| CV, B4 without consolidate (A2) | field | -0.029 [-0.14, +0.08] | 0.274 | work +0.097, chat +0.015, idle -0.123 |

P4: browse up ✓ (+0.056 [+0.033, +0.079]); type + shell down ✗ (+0.099 [+0.068, +0.129]: up, not down); |K_B4| < 0.10 ✗ on the point estimate (+0.242, CI spans 0) and ✗ in the no-consolidate chain (-0.148, CI excludes 0); CF and CV same class ✗ (CF both / CV field in the A2 chain).

Reading: right after a forced erasure the agent is *less* idle and works more (browse and type up, idle −0.13 in the A2 chain), and it switches state *more slowly* (work escape down): an anti-catalytic field toward work. The consolidation clock confounds the full chain. This does not contradict H15's write dip directly: H15 counted functional-output turns (git commit/push, deploy), these are activity states.

## Notes
- Run 2026-10-04; placebos are within-goal day boundaries of the same era (regime × hours) and window shape, excluding ±1 day around the tested scaffold steps.
