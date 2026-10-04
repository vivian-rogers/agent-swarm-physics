# H27 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-27)

**Verdict:** descriptive (1 evaluable onset, percentile 0.86)
**Verdict (1b):** descriptive (unchanged)
**Role:** exploratory (transfer / false-alarm period)
**Period:** regime III · mode C · N = 12 · 17 active days in the series · W = 15: 302 windows, q = 7, 90% of windows with ≥ 3 labeled agents (mean 6.5); W = 30: 87%.

## Why this period
17 days of shared charity campaign work; dense labels. Arms: W = 15 (primary) and W = 30 (coverage rule: ≥ 50% of windows with ≥ 3 labeled agents).

## Prediction
*Written 2026-10-04, before running on this period.*
- **P0 (onsets, O1 at W = 15):** 2–5 herding onsets.
- **P1 (early warning):** if ≥ 2 onsets are evaluable at lead ℓ = 4 (1 h), the composite AUC (τ_AR1 + τ_SD, onset vs placebo segments) is < 0.6, i.e. at chance. If 1 is evaluable, its composite sits inside the placebo bulk (percentile < 0.9).
- **P2:** any apparent signal comes from τ_SD or flickering, and shrinks after binomial standardization (rising mean, R3).
- **P3 (operator alarm, frozen τ*):** hits at most half of the onsets; its false-alarm rate per (project, window) is ≥ the synthetic 5%; the naive level alarm (share ≥ 0.3) gives the same or more lead.
- **Verdict rule:** with ≥ 2 evaluable onsets, **supported** if AUC ≥ 0.7 and the alarm hits ≥ half the onsets; **failed** if AUC < 0.6 and it hits < half; **mixed** otherwise. With 1 evaluable onset: **descriptive** (percentile reported). With none: **descriptive** (false alarms only).
- **What would count against my negative prior:** a supported verdict here, especially with the level alarm giving less lead.

## Result
Arm W = 15 min. τ* = 0.538 (frozen from synthetic S0). Onsets (O1): 3; O1-slow variant: 1. Onsets dropped at ℓ = 4: 0 too early (< 24 windows of history), 1 too sparse, 1 not low at t_e.

| Onset | Project | Share at onset (k/n) | Baseline → persistence | Evaluable at ℓ = 4 | EWS alarm | Level alarm | Momentum alarm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| w78 | `rest-collaboration-showcase` | 0.50 (3/6) | 0.25 → 0.43 | yes | miss | hit, lead 2.50 h | hit, lead 2.50 h |
| w164 | `rest-collaboration-showcase` | 0.50 (3/6) | 0.25 → 0.43 | no | miss | hit, lead 0.50 h | hit, lead 0.50 h |
| w200 (day start) | `ai-village-charity-2026` | 0.56 (5/9) | 0.19 → 0.48 | no | not watchable | not watchable | not watchable |

| Test | Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- | --- |
| P0 onsets | 2–5 | 3 | – | as expected |
| P1 composite percentile among placebos | < 0.9 | 0.86 (vs 700 placebo segments) | 0.5 | as predicted |
| P3 EWS alarm | hits ≤ half; FAR ≥ 5% | 0/3 hit (2 watchable); 27 false alarms in 1402 watched (project, window) = 1.9%; PPV 0.00 | level alarm 2/3 hit, FAR 3.4% | as predicted |
| W = 30 arm | – | onsets 0; evaluable 0; AUC –; EWS hits 0/0 | – | robustness |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| G ground truth | 1 | onsets found by the rule: 3 (compare H11's narrative for this period) |

## Notes
- 2026-10-04: prediction written before running this period.
- 2026-10-04: round 1 run (`analysis/explore.py`); data in `data/processed/H27-herding-early-warning/G38/round1_w*.json`.
- 2026-10-04 (post hoc): 3 onsets in 17 days on the two shared campaign repos; the evaluable one shows rising variance and flickering with falling AR1.

## Round 1b (improved data, 2026-10-04)
*Replication (templated) on the shared deterministic labels (`scheme/build.py --labels shared`, `analysis/round1b.py replicate`), plus the work-ledger series for #30 onward (`round1b.py work`). Card predictions R1b-1 to R1b-3 were written before the run.*

| Arm | Labels | Onsets | Evaluable | Composite AUC | EWS hits | EWS false alarms / day |
| --- | --- | --- | --- | --- | --- | --- |
| W15 | round 1 (H11 labels) | 3 | 1 | 0.86 | 0/3 | 1.7 |
| W15 | round 1b (shared labels) | 3 | 1 | 0.86 | 0/3 | 1.4 |
| W30 | round 1 (H11 labels) | 0 | 0 | – | 0/0 | 0.1 |
| W30 | round 1b (shared labels) | 0 | 0 | – | 0/0 | 0.1 |
| W30 | round 1b, work commits | 1 | 0 | – | 0/1 | 0.0 |
