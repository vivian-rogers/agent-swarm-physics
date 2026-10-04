# H27 × G30: Adopt a park and get it cleaned! (2026-02-09 → 2026-02-16)

**Verdict:** mixed (AUC 0.57, 2/4 hit)
**Verdict (1b):** mixed (AUC 0.55, 2/4 hit; unchanged)
**Role:** replication (exploratory (transfer / false-alarm period))
**Period:** regime I · mode C · N = 12 · 5 active days in the series · W = 15: 83 windows, q = 4, 96% of windows with ≥ 3 labeled agents (mean 9.0); W = 30: 93%.

## Why this period
Shared park-cleanup documents; herded in H11; dense labels. Arms: W = 15 (primary) and W = 30 (coverage rule: ≥ 50% of windows with ≥ 3 labeled agents).

## Prediction
*Written 2026-10-04, before running on this period.*
- **P0 (onsets, O1 at W = 15):** 1–3 herding onsets.
- **P1 (early warning):** if ≥ 2 onsets are evaluable at lead ℓ = 4 (1 h), the composite AUC (τ_AR1 + τ_SD, onset vs placebo segments) is < 0.6, i.e. at chance. If 1 is evaluable, its composite sits inside the placebo bulk (percentile < 0.9).
- **P2:** any apparent signal comes from τ_SD or flickering, and shrinks after binomial standardization (rising mean, R3).
- **P3 (operator alarm, frozen τ*):** hits at most half of the onsets; its false-alarm rate per (project, window) is ≥ the synthetic 5%; the naive level alarm (share ≥ 0.3) gives the same or more lead.
- **Verdict rule:** with ≥ 2 evaluable onsets, **supported** if AUC ≥ 0.7 and the alarm hits ≥ half the onsets; **failed** if AUC < 0.6 and it hits < half; **mixed** otherwise. With 1 evaluable onset: **descriptive** (percentile reported). With none: **descriptive** (false alarms only).
- **What would count against my negative prior:** a supported verdict here, especially with the level alarm giving less lead.

## Result
Arm W = 15 min. τ* = 0.538 (frozen from synthetic S0). Onsets (O1): 4; O1-slow variant: 3. Onsets dropped at ℓ = 4: 2 too early (< 24 windows of history), 0 too sparse, 0 not low at t_e.

| Onset | Project | Share at onset (k/n) | Baseline → persistence | Evaluable at ℓ = 4 | EWS alarm | Level alarm | Momentum alarm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| w11 | `park-cleanup-site` | 0.56 (5/9) | 0.15 → 0.44 | no | not watchable | not watchable | not watchable |
| w23 | `park-cleanup-site` | 0.70 (7/10) | 0.22 → 0.56 | no | not watchable | not watchable | not watchable |
| w55 | `park-cleanup-site` | 0.92 (11/12) | 0.14 → 0.56 | yes | hit, lead 1.25 h | hit, lead 2.50 h | hit, lead 2.50 h |
| w73 (last day) | `park-cleanup-site` | 0.50 (6/12) | 0.22 → 0.46 | yes | hit, lead 3.00 h | hit, lead 3.00 h | hit, lead 3.00 h |

| Test | Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- | --- |
| P0 onsets | 1–3 | 4 | – | outside the expected range |
| P1 composite AUC (ℓ = 4) | < 0.6 | 0.57 (2 onset vs 59 placebo segments) | 0.5 | as predicted (chance) |
| P2 τ_AR1 / τ_SD / τ_SD binomial / τ_flicker / flicker level / mean share last 4 | signal only in SD or flicker, gone after standardization | 0.61 / 0.51 / 0.44 / 0.91 / 0.86 / 0.81 | 0.5 | descriptive |
| P3 EWS alarm | hits ≤ half; FAR ≥ 5% | 2/4 hit (2 watchable); 3 false alarms in 139 watched (project, window) = 2.2%; PPV 0.40 | level alarm 2/4 hit, FAR 7.2% | as predicted |
| W = 30 arm | – | onsets 1; evaluable 1; AUC –; EWS hits 0/1 | – | robustness |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | composite AUC 0.57 vs placebo segments |
| G ground truth | 1 | onsets found by the rule: 4 (compare H11's narrative for this period) |

## Notes
- 2026-10-04: prediction written before running this period.
- 2026-10-04: round 1 run (`analysis/explore.py`); data in `data/processed/H27-herding-early-warning/G30/round1_w*.json`.
- 2026-10-04 (post hoc): all 4 onsets are returns of the same shared site repo to majority after dips; the two late ones were warned by the EWS alarm (leads 1.25 h and 3 h) and the level alarm (2.5 h and 3 h); a 3-h lead is the horizon cap, i.e. the alarm was already on. The two early onsets had too little history.

## Round 1b (improved data, 2026-10-04)
*Replication (templated) on the shared deterministic labels (`scheme/build.py --labels shared`, `analysis/round1b.py replicate`), plus the work-ledger series for #30 onward (`round1b.py work`). Card predictions R1b-1 to R1b-3 were written before the run.*

| Arm | Labels | Onsets | Evaluable | Composite AUC | EWS hits | EWS false alarms / day |
| --- | --- | --- | --- | --- | --- | --- |
| W15 | round 1 (H11 labels) | 4 | 2 | 0.57 | 2/4 | 0.8 |
| W15 | round 1b (shared labels) | 4 | 2 | 0.55 | 2/4 | 1.0 |
| W15 | round 1b, work commits | 1 | 0 | – | 0/1 | 0.0 |
| W30 | round 1 (H11 labels) | 1 | 1 | 0.29 | 0/1 | 0.0 |
| W30 | round 1b (shared labels) | 1 | 1 | 0.29 | 0/1 | 0.0 |
| W30 | round 1b, work commits | 0 | 0 | – | 0/0 | 0.0 |
