# H27 × G19: Create a popular daily puzzle game like Wordle (2025-11-03 → 2025-11-17)

**Verdict:** descriptive (1 evaluable onset, percentile 0.59)
**Role:** exploratory (transfer / false-alarm period)
**Period:** regime I · mode C · N = 7 · 10 active days in the series · W = 15: 163 windows, q = 4, 66% of windows with ≥ 3 labeled agents (mean 3.3); W = 30: 82%.

## Why this period
The build repo held ≈ 0.6 share from the start in H11 (frozen order: no low baseline to step from). Arms: W = 15 (primary) and W = 30 (coverage rule: ≥ 50% of windows with ≥ 3 labeled agents).

## Prediction
*Written 2026-10-04, before running on this period.*
- **P0 (onsets, O1 at W = 15):** 0–1 herding onsets.
- **P1 (early warning):** if ≥ 2 onsets are evaluable at lead ℓ = 4 (1 h), the composite AUC (τ_AR1 + τ_SD, onset vs placebo segments) is < 0.6, i.e. at chance. If 1 is evaluable, its composite sits inside the placebo bulk (percentile < 0.9).
- **P2:** any apparent signal comes from τ_SD or flickering, and shrinks after binomial standardization (rising mean, R3).
- **P3 (operator alarm, frozen τ*):** hits at most half of the onsets; its false-alarm rate per (project, window) is ≥ the synthetic 5%; the naive level alarm (share ≥ 0.3) gives the same or more lead.
- **Verdict rule:** with ≥ 2 evaluable onsets, **supported** if AUC ≥ 0.7 and the alarm hits ≥ half the onsets; **failed** if AUC < 0.6 and it hits < half; **mixed** otherwise. With 1 evaluable onset: **descriptive** (percentile reported). With none: **descriptive** (false alarms only).
- **What would count against my negative prior:** a supported verdict here, especially with the level alarm giving less lead.

## Result
Arm W = 15 min. τ* = 0.538 (frozen from synthetic S0). Onsets (O1): 3; O1-slow variant: 3. Onsets dropped at ℓ = 4: 1 too early (< 24 windows of history), 1 too sparse, 0 not low at t_e.

| Onset | Project | Share at onset (k/n) | Baseline → persistence | Evaluable at ℓ = 4 | EWS alarm | Level alarm | Momentum alarm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| w13 | `daily-puzzle.netlify.app` | 0.71 (5/7) | 0.00 → 0.58 | no | not watchable | not watchable | not watchable |
| w109 | `daily-puzzle-landing` | 0.57 (4/7) | 0.08 → 0.60 | yes | miss | miss | miss |
| w61 | `super-daifuku-bd440b.netlify.app` | 0.50 (3/6) | 0.25 → 0.48 | no | miss | miss | miss |

| Test | Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- | --- |
| P0 onsets | 0–1 | 3 | – | outside the expected range |
| P1 composite percentile among placebos | < 0.9 | 0.59 (vs 52 placebo segments) | 0.5 | as predicted |
| P3 EWS alarm | hits ≤ half; FAR ≥ 5% | 0/3 hit (2 watchable); 0 false alarms in 113 watched (project, window) = 0.0%; PPV 0.00 | level alarm 0/3 hit, FAR 5.3% | as predicted |
| W = 30 arm | – | onsets 4; evaluable 1; AUC –; EWS hits 0/4 | – | robustness |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| G ground truth | 1 | onsets found by the rule: 3 (compare H11's narrative for this period) |

## Notes
- 2026-10-04: prediction written before running this period.
- 2026-10-04: round 1 run (`analysis/explore.py`); data in `data/processed/H27-herding-early-warning/G19/round1_w*.json`.
- 2026-10-04 (post hoc): the build repo dominated from the start (H11: frozen order); the 3 onsets are on the landing repo and sites. One lands on a project with no prior mention.
