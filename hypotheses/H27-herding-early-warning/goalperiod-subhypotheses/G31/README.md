# H27 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-23)

**Verdict:** mixed (AUC 0.91, 1/4 hit)
**Role:** exploratory (candidate)
**Period:** regime I · mode F · N = 12 · 5 active days in the series · W = 15: 82 windows, q = 8, 98% of windows with ≥ 3 labeled agents (mean 8.9); W = 30: 95%.

## Why this period
Candidate; H11 saw successive herding waves (time-capsule repo peaked at 11 agents in one window). Arms: W = 15 (primary) and W = 30 (coverage rule: ≥ 50% of windows with ≥ 3 labeled agents).

## Prediction
*Written 2026-10-04, before running on this period.*
- **P0 (onsets, O1 at W = 15):** ≥ 3 herding onsets.
- **P1 (early warning):** if ≥ 2 onsets are evaluable at lead ℓ = 4 (1 h), the composite AUC (τ_AR1 + τ_SD, onset vs placebo segments) is < 0.6, i.e. at chance. If 1 is evaluable, its composite sits inside the placebo bulk (percentile < 0.9).
- **P2:** any apparent signal comes from τ_SD or flickering, and shrinks after binomial standardization (rising mean, R3).
- **P3 (operator alarm, frozen τ*):** hits at most half of the onsets; its false-alarm rate per (project, window) is ≥ the synthetic 5%; the naive level alarm (share ≥ 0.3) gives the same or more lead.
- **Verdict rule:** with ≥ 2 evaluable onsets, **supported** if AUC ≥ 0.7 and the alarm hits ≥ half the onsets; **failed** if AUC < 0.6 and it hits < half; **mixed** otherwise. With 1 evaluable onset: **descriptive** (percentile reported). With none: **descriptive** (false alarms only).
- **What would count against my negative prior:** a supported verdict here, especially with the level alarm giving less lead.

## Result
Arm W = 15 min. τ* = 0.538 (frozen from synthetic S0). Onsets (O1): 4; O1-slow variant: 4. Onsets dropped at ℓ = 4: 2 too early (< 24 windows of history), 0 too sparse, 0 not low at t_e.

| Onset | Project | Share at onset (k/n) | Baseline → persistence | Evaluable at ℓ = 4 | EWS alarm | Level alarm | Momentum alarm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| w23 | `village-time-capsule` | 0.50 (5/10) | 0.07 → 0.47 | no | not watchable | not watchable | not watchable |
| w60 | `village-event-log` | 0.50 (3/6) | 0.11 → 0.71 | yes | miss | miss | miss |
| w16 (day start) | `civic-safety-guardrails` | 0.70 (7/10) | 0.10 → 0.44 | no | not watchable | not watchable | not watchable |
| w43 | `village-operations-handbook` | 0.50 (4/8) | 0.18 → 0.43 | yes | hit, lead 2.50 h | hit, lead 0.50 h | hit, lead 2.25 h |

| Test | Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- | --- |
| P0 onsets | ≥ 3 | 4 | – | as expected |
| P1 composite AUC (ℓ = 4) | < 0.6 | 0.91 (2 onset vs 183 placebo segments) | 0.5 | against my prior |
| P2 τ_AR1 / τ_SD / τ_SD binomial / τ_flicker / flicker level / mean share last 4 | signal only in SD or flicker, gone after standardization | 0.29 / 0.98 / 0.98 / 0.54 / 0.25 / 0.88 | 0.5 | descriptive |
| P3 EWS alarm | hits ≤ half; FAR ≥ 5% | 1/4 hit (2 watchable); 10 false alarms in 414 watched (project, window) = 2.4%; PPV 0.17 | level alarm 1/4 hit, FAR 3.9% | as predicted |
| W = 30 arm | – | onsets 2; evaluable 1; AUC –; EWS hits 0/2 | – | robustness |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 1 | composite AUC 0.91 vs placebo segments |
| G ground truth | 1 | onsets found by the rule: 4 (compare H11's narrative for this period) |

## Notes
- 2026-10-04: prediction written before running this period.
- 2026-10-04: round 1 run (`analysis/explore.py`); data in `data/processed/H27-herding-early-warning/G31/round1_w*.json`.
- 2026-10-04 (post hoc): matches H11's waves. Onsets on the guardrails repo (day 2 start), the time-capsule repo, the operations handbook and the event log (H11's final-day dominant repo). The first two come within the first 1.5 days, so only 2 are evaluable; for those, τ_SD rises while τ_AR1 falls (not critical slowing down).
