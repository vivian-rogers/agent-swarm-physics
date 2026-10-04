# H27 × G17: Each agent: build your own personal website (2025-10-13 → 2025-10-20)

**Verdict:** descriptive (30-min arm; no evaluable onset)
**Verdict (1b):** descriptive (unchanged)
**Role:** replication (exploratory (transfer / false-alarm period))
**Period:** regime I · mode I · N = 7 · 5 active days in the series · W = 15: 62 windows, q = 8, 27% of windows with ≥ 3 labeled agents (mean 1.6); W = 30: 56%.

## Why this period
Each agent builds its own personal website (own artifacts). Arms: W = 30 only (coverage rule: ≥ 50% of windows with ≥ 3 labeled agents).

## Prediction
*Written 2026-10-04, before running on this period.*
- **P0 (onsets, O1 at W = 15):** 0 herding onsets.
- **P1 (early warning):** if ≥ 2 onsets are evaluable at lead ℓ = 4 (1 h), the composite AUC (τ_AR1 + τ_SD, onset vs placebo segments) is < 0.6, i.e. at chance. If 1 is evaluable, its composite sits inside the placebo bulk (percentile < 0.9).
- **P2:** any apparent signal comes from τ_SD or flickering, and shrinks after binomial standardization (rising mean, R3).
- **P3 (operator alarm, frozen τ*):** hits at most half of the onsets; its false-alarm rate per (project, window) is ≥ the synthetic 5%; the naive level alarm (share ≥ 0.3) gives the same or more lead.
- **Verdict rule:** with ≥ 2 evaluable onsets, **supported** if AUC ≥ 0.7 and the alarm hits ≥ half the onsets; **failed** if AUC < 0.6 and it hits < half; **mixed** otherwise. With 1 evaluable onset: **descriptive** (percentile reported). With none: **descriptive** (false alarms only).
- **What would count against my negative prior:** a supported verdict here, especially with the level alarm giving less lead.

## Result
Arm W = 30 min. τ* = 0.538 (frozen from synthetic S0). Onsets (O1): 0; O1-slow variant: 0. Onsets dropped at ℓ = 4: 0 too early (< 24 windows of history), 0 too sparse, 0 not low at t_e.

| Test | Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- | --- |
| P0 onsets | 0 | 0 | – | as expected |
| P3 EWS alarm | hits ≤ half; FAR ≥ 5% | 0/0 hit (0 watchable); 0 false alarms in 16 watched (project, window) = 0.0%; PPV 0.00 | level alarm 0/0 hit, FAR 0.0% | as predicted |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| G ground truth | 0 | onsets found by the rule: 0 (compare H11's narrative for this period) |

## Notes
- 2026-10-04: prediction written before running this period.
- 2026-10-04: round 1 run (`analysis/explore.py`); data in `data/processed/H27-herding-early-warning/G17/round1_w*.json`.

## Round 1b (improved data, 2026-10-04)
*Replication (templated) on the shared deterministic labels (`scheme/build.py --labels shared`, `analysis/round1b.py replicate`), plus the work-ledger series for #30 onward (`round1b.py work`). Card predictions R1b-1 to R1b-3 were written before the run.*

| Arm | Labels | Onsets | Evaluable | Composite AUC | EWS hits | EWS false alarms / day |
| --- | --- | --- | --- | --- | --- | --- |
| W30 | round 1 (H11 labels) | 0 | 0 | – | 0/0 | 0.0 |
| W30 | round 1b (shared labels) | 0 | 0 | – | 0/0 | 0.0 |
