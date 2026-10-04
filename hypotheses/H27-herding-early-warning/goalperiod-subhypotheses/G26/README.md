# H27 × G26: Elect a village leader. They choose this week’s goal! (2026-01-05 → 2026-01-12)

**Verdict:** descriptive (30-min arm; no evaluable onset)
**Verdict (1b):** descriptive (unchanged)
**Role:** replication (exploratory (transfer / false-alarm period))
**Period:** regime I · mode C · N = 10 · 5 active days in the series · W = 15: 67 windows, q = 8, 45% of windows with ≥ 3 labeled agents (mean 3.0); W = 30: 67%.

## Why this period
The runoff jump lives in the votes, not in project labels. Arms: W = 30 only (coverage rule: ≥ 50% of windows with ≥ 3 labeled agents).

## Prediction
*Written 2026-10-04, before running on this period.*
- **P0 (onsets, O1 at W = 15):** 0–1 herding onsets.
- **P1 (early warning):** if ≥ 2 onsets are evaluable at lead ℓ = 4 (1 h), the composite AUC (τ_AR1 + τ_SD, onset vs placebo segments) is < 0.6, i.e. at chance. If 1 is evaluable, its composite sits inside the placebo bulk (percentile < 0.9).
- **P2:** any apparent signal comes from τ_SD or flickering, and shrinks after binomial standardization (rising mean, R3).
- **P3 (operator alarm, frozen τ*):** hits at most half of the onsets; its false-alarm rate per (project, window) is ≥ the synthetic 5%; the naive level alarm (share ≥ 0.3) gives the same or more lead.
- **Verdict rule:** with ≥ 2 evaluable onsets, **supported** if AUC ≥ 0.7 and the alarm hits ≥ half the onsets; **failed** if AUC < 0.6 and it hits < half; **mixed** otherwise. With 1 evaluable onset: **descriptive** (percentile reported). With none: **descriptive** (false alarms only).
- **What would count against my negative prior:** a supported verdict here, especially with the level alarm giving less lead.

## Result
Arm W = 30 min. τ* = 0.538 (frozen from synthetic S0). Onsets (O1): 1; O1-slow variant: 1. Onsets dropped at ℓ = 4: 0 too early (< 24 windows of history), 1 too sparse, 0 not low at t_e.

| Onset | Project | Share at onset (k/n) | Baseline → persistence | Evaluable at ℓ = 4 | EWS alarm | Level alarm | Momentum alarm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| w27 (day start) (last day) | `Google doc #6` | 1.00 (4/4) | 0.00 → 0.49 | no | not watchable | not watchable | not watchable |

| Test | Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- | --- |
| P0 onsets | 0–1 | 1 | – | as expected |
| P3 EWS alarm | hits ≤ half; FAR ≥ 5% | 0/1 hit (0 watchable); 0 false alarms in 15 watched (project, window) = 0.0%; PPV 0.00 | level alarm 0/1 hit, FAR 0.0% | as predicted |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| G ground truth | 1 | onsets found by the rule: 1 (compare H11's narrative for this period) |

## Notes
- 2026-10-04: prediction written before running this period.
- 2026-10-04: round 1 run (`analysis/explore.py`); data in `data/processed/H27-herding-early-warning/G26/round1_w*.json`.

## Round 1b (improved data, 2026-10-04)
*Replication (templated) on the shared deterministic labels (`scheme/build.py --labels shared`, `analysis/round1b.py replicate`), plus the work-ledger series for #30 onward (`round1b.py work`). Card predictions R1b-1 to R1b-3 were written before the run.*

| Arm | Labels | Onsets | Evaluable | Composite AUC | EWS hits | EWS false alarms / day |
| --- | --- | --- | --- | --- | --- | --- |
| W30 | round 1 (H11 labels) | 1 | 0 | – | 0/1 | 0.0 |
| W30 | round 1b (shared labels) | 1 | 0 | – | 0/1 | 0.0 |
