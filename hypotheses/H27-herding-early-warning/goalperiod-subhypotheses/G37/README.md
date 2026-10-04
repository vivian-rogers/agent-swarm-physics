# H27 × G37: Pick your own goal! (2026-03-30 → 2026-04-02)

**Verdict:** descriptive (no evaluable onset)
**Role:** exploratory (candidate)
**Period:** regime III · mode F · N = 13 · 3 active days in the series · W = 15: 85 windows, q = 8, 56% of windows with ≥ 3 labeled agents (mean 3.9); W = 30: 55%.

## Why this period
Candidate; 3 days only, so few onsets have 24 windows of history. Arms: W = 15 (primary) and W = 30 (coverage rule: ≥ 50% of windows with ≥ 3 labeled agents).

## Prediction
*Written 2026-10-04, before running on this period.*
- **P0 (onsets, O1 at W = 15):** 0–2 herding onsets.
- **P1 (early warning):** if ≥ 2 onsets are evaluable at lead ℓ = 4 (1 h), the composite AUC (τ_AR1 + τ_SD, onset vs placebo segments) is < 0.6, i.e. at chance. If 1 is evaluable, its composite sits inside the placebo bulk (percentile < 0.9).
- **P2:** any apparent signal comes from τ_SD or flickering, and shrinks after binomial standardization (rising mean, R3).
- **P3 (operator alarm, frozen τ*):** hits at most half of the onsets; its false-alarm rate per (project, window) is ≥ the synthetic 5%; the naive level alarm (share ≥ 0.3) gives the same or more lead.
- **Verdict rule:** with ≥ 2 evaluable onsets, **supported** if AUC ≥ 0.7 and the alarm hits ≥ half the onsets; **failed** if AUC < 0.6 and it hits < half; **mixed** otherwise. With 1 evaluable onset: **descriptive** (percentile reported). With none: **descriptive** (false alarms only).
- **What would count against my negative prior:** a supported verdict here, especially with the level alarm giving less lead.

## Result
Arm W = 15 min. τ* = 0.538 (frozen from synthetic S0). Onsets (O1): 1; O1-slow variant: 2. Onsets dropped at ℓ = 4: 1 too early (< 24 windows of history), 0 too sparse, 0 not low at t_e.

| Onset | Project | Share at onset (k/n) | Baseline → persistence | Evaluable at ℓ = 4 | EWS alarm | Level alarm | Momentum alarm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| w8 | `cross-agent-lessons` | 0.60 (3/5) | 0.24 → 0.42 | no | not watchable | not watchable | not watchable |

| Test | Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- | --- |
| P0 onsets | 0–2 | 1 | – | as expected |
| P3 EWS alarm | hits ≤ half; FAR ≥ 5% | 0/1 hit (0 watchable); 1 false alarms in 115 watched (project, window) = 0.9%; PPV 0.00 | level alarm 0/1 hit, FAR 3.5% | as predicted |
| W = 30 arm | – | onsets 2; evaluable 0; AUC –; EWS hits 0/2 | – | robustness |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| G ground truth | 1 | onsets found by the rule: 1 (compare H11's narrative for this period) |

## Notes
- 2026-10-04: prediction written before running this period.
- 2026-10-04: round 1 run (`analysis/explore.py`); data in `data/processed/H27-herding-early-warning/G37/round1_w*.json`.
- 2026-10-04 (post hoc): 3 days; the one onset (day 1) has no history.
