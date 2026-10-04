# H27 × G33: Discuss, debate, and act on your views about the recent Pentagon-AI company news (2026-03-02 → 2026-03-05)

**Verdict:** descriptive (1 evaluable onset, no placebos)
**Verdict (1b):** descriptive (unchanged)
**Role:** exploratory (transfer / false-alarm period)
**Period:** regime II · mode C · N = 12 · 3 active days in the series · W = 15: 48 windows, q = 2, 100% of windows with ≥ 3 labeled agents (mean 8.9); W = 30: 100%.

## Why this period
3 days only; few evaluable. Arms: W = 15 (primary) and W = 30 (coverage rule: ≥ 50% of windows with ≥ 3 labeled agents).

## Prediction
*Written 2026-10-04, before running on this period.*
- **P0 (onsets, O1 at W = 15):** 0–2 herding onsets.
- **P1 (early warning):** if ≥ 2 onsets are evaluable at lead ℓ = 4 (1 h), the composite AUC (τ_AR1 + τ_SD, onset vs placebo segments) is < 0.6, i.e. at chance. If 1 is evaluable, its composite sits inside the placebo bulk (percentile < 0.9).
- **P2:** any apparent signal comes from τ_SD or flickering, and shrinks after binomial standardization (rising mean, R3).
- **P3 (operator alarm, frozen τ*):** hits at most half of the onsets; its false-alarm rate per (project, window) is ≥ the synthetic 5%; the naive level alarm (share ≥ 0.3) gives the same or more lead.
- **Verdict rule:** with ≥ 2 evaluable onsets, **supported** if AUC ≥ 0.7 and the alarm hits ≥ half the onsets; **failed** if AUC < 0.6 and it hits < half; **mixed** otherwise. With 1 evaluable onset: **descriptive** (percentile reported). With none: **descriptive** (false alarms only).
- **What would count against my negative prior:** a supported verdict here, especially with the level alarm giving less lead.

## Result
Arm W = 15 min. τ* = 0.538 (frozen from synthetic S0). Onsets (O1): 2; O1-slow variant: 2. Onsets dropped at ℓ = 4: 0 too early (< 24 windows of history), 0 too sparse, 1 not low at t_e.

| Onset | Project | Share at onset (k/n) | Baseline → persistence | Evaluable at ℓ = 4 | EWS alarm | Level alarm | Momentum alarm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| w41 (last day) | `pentagon-ai-research` | 0.55 (6/11) | 0.12 → 0.81 | no | hit, lead 0.75 h | miss | hit, lead 0.50 h |
| w35 (last day) | `ai-governance-gap-proposal` | 0.73 (8/11) | 0.03 → 0.88 | yes | hit, lead 0.25 h | miss | miss |

| Test | Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- | --- |
| P0 onsets | 0–2 | 2 | – | as expected |
| P1 composite percentile among placebos | < 0.9 | no placebo segments (both projects alternate dominance) | – | untestable |
| P3 EWS alarm | hits ≤ half; FAR ≥ 5% | 2/2 hit (2 watchable); 1 false alarms in 6 watched (project, window) = 16.7%; PPV 0.80 | level alarm 0/2 hit, FAR 33.3% | against my prior |
| W = 30 arm | – | onsets 2; evaluable 0; AUC –; EWS hits 0/2 | – | robustness |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| G ground truth | 1 | onsets found by the rule: 2 (compare H11's narrative for this period) |

## Notes
- 2026-10-04: prediction written before running this period.
- 2026-10-04: round 1 run (`analysis/explore.py`); data in `data/processed/H27-herding-early-warning/G33/round1_w*.json`.
- 2026-10-04 (post hoc): q = 2; both onsets are a last-day handover between the two projects. The low-state matching condition never holds for placebo segments, so the period informs only the operator alarm.

## Round 1b (improved data, 2026-10-04)
*Replication (templated) on the shared deterministic labels (`scheme/build.py --labels shared`, `analysis/round1b.py replicate`), plus the work-ledger series for #30 onward (`round1b.py work`). Card predictions R1b-1 to R1b-3 were written before the run.*

| Arm | Labels | Onsets | Evaluable | Composite AUC | EWS hits | EWS false alarms / day |
| --- | --- | --- | --- | --- | --- | --- |
| W15 | round 1 (H11 labels) | 2 | 1 | – | 2/2 | 0.5 |
| W15 | round 1b (shared labels) | 2 | 1 | – | 2/2 | 0.5 |
| W15 | round 1b, work commits | 2 | 1 | 0.73 | 1/2 | 0.5 |
| W30 | round 1 (H11 labels) | 2 | 0 | – | 0/2 | 0.5 |
| W30 | round 1b (shared labels) | 2 | 0 | – | 0/2 | 0.5 |
| W30 | round 1b, work commits | 1 | 0 | – | 0/1 | 0.0 |
