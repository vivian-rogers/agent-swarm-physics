# H27 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 2026-03-23)

**Verdict:** descriptive (no evaluable onset)
**Verdict (1b):** descriptive (unchanged)
**Role:** replication (exploratory (transfer / false-alarm period))
**Period:** regime II · mode C · N = 13 · 5 active days in the series · W = 15: 80 windows, q = 2, 99% of windows with ≥ 3 labeled agents (mean 7.6); W = 30: 100%.

## Why this period
Game testing after the #best/#rest split; each fork is its own repo. Arms: W = 15 (primary) and W = 30 (coverage rule: ≥ 50% of windows with ≥ 3 labeled agents).

## Prediction
*Written 2026-10-04, before running on this period.*
- **P0 (onsets, O1 at W = 15):** 1–2 herding onsets.
- **P1 (early warning):** if ≥ 2 onsets are evaluable at lead ℓ = 4 (1 h), the composite AUC (τ_AR1 + τ_SD, onset vs placebo segments) is < 0.6, i.e. at chance. If 1 is evaluable, its composite sits inside the placebo bulk (percentile < 0.9).
- **P2:** any apparent signal comes from τ_SD or flickering, and shrinks after binomial standardization (rising mean, R3).
- **P3 (operator alarm, frozen τ*):** hits at most half of the onsets; its false-alarm rate per (project, window) is ≥ the synthetic 5%; the naive level alarm (share ≥ 0.3) gives the same or more lead.
- **Verdict rule:** with ≥ 2 evaluable onsets, **supported** if AUC ≥ 0.7 and the alarm hits ≥ half the onsets; **failed** if AUC < 0.6 and it hits < half; **mixed** otherwise. With 1 evaluable onset: **descriptive** (percentile reported). With none: **descriptive** (false alarms only).
- **What would count against my negative prior:** a supported verdict here, especially with the level alarm giving less lead.

## Result
Arm W = 15 min. τ* = 0.538 (frozen from synthetic S0). Onsets (O1): 0; O1-slow variant: 0. Onsets dropped at ℓ = 4: 0 too early (< 24 windows of history), 0 too sparse, 0 not low at t_e.

| Test | Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- | --- |
| P0 onsets | 1–2 | 0 | – | outside the expected range |
| P3 EWS alarm | hits ≤ half; FAR ≥ 5% | 0/0 hit (0 watchable); 0 false alarms in 31 watched (project, window) = 0.0%; PPV 0.00 | level alarm 0/0 hit, FAR 32.3% | as predicted |
| W = 30 arm | – | onsets 0; evaluable 0; AUC –; EWS hits 0/0 | – | robustness |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| G ground truth | 0 | onsets found by the rule: 0 (compare H11's narrative for this period) |

## Notes
- 2026-10-04: prediction written before running this period.
- 2026-10-04: round 1 run (`analysis/explore.py`); data in `data/processed/H27-herding-early-warning/G35/round1_w*.json`.

## Round 1b (improved data, 2026-10-04)
*Replication (templated) on the shared deterministic labels (`scheme/build.py --labels shared`, `analysis/round1b.py replicate`), plus the work-ledger series for #30 onward (`round1b.py work`). Card predictions R1b-1 to R1b-3 were written before the run.*

| Arm | Labels | Onsets | Evaluable | Composite AUC | EWS hits | EWS false alarms / day |
| --- | --- | --- | --- | --- | --- | --- |
| W15 | round 1 (H11 labels) | 0 | 0 | – | 0/0 | 0.0 |
| W15 | round 1b (shared labels) | 0 | 0 | – | 0/0 | 0.0 |
| W15 | round 1b, work commits | 0 | 0 | – | 0/0 | 0.0 |
| W30 | round 1 (H11 labels) | 0 | 0 | – | 0/0 | 0.7 |
| W30 | round 1b (shared labels) | 0 | 0 | – | 0/0 | 0.7 |
| W30 | round 1b, work commits | 0 | 0 | – | 0/0 | 0.0 |
