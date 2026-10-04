# H27 × G18: Reduce global poverty as much as you can (2025-10-20 → 2025-11-03)

**Verdict:** descriptive (1 evaluable onset, percentile 0.46)
**Role:** exploratory (candidate)
**Period:** regime I · mode C · N = 7 · 10 active days in the series · W = 15: 153 windows, q = 8, 59% of windows with ≥ 3 labeled agents (mean 3.1); W = 30: 79%.

## Why this period
Candidate; sparse labels (≈ 3 per window) and the last-day convergence may fail the coverage or baseline condition. Arms: W = 15 (primary) and W = 30 (coverage rule: ≥ 50% of windows with ≥ 3 labeled agents).

## Prediction
*Written 2026-10-04, before running on this period.*
- **P0 (onsets, O1 at W = 15):** 0–1 herding onsets.
- **P1 (early warning):** if ≥ 2 onsets are evaluable at lead ℓ = 4 (1 h), the composite AUC (τ_AR1 + τ_SD, onset vs placebo segments) is < 0.6, i.e. at chance. If 1 is evaluable, its composite sits inside the placebo bulk (percentile < 0.9).
- **P2:** any apparent signal comes from τ_SD or flickering, and shrinks after binomial standardization (rising mean, R3).
- **P3 (operator alarm, frozen τ*):** hits at most half of the onsets; its false-alarm rate per (project, window) is ≥ the synthetic 5%; the naive level alarm (share ≥ 0.3) gives the same or more lead.
- **Verdict rule:** with ≥ 2 evaluable onsets, **supported** if AUC ≥ 0.7 and the alarm hits ≥ half the onsets; **failed** if AUC < 0.6 and it hits < half; **mixed** otherwise. With 1 evaluable onset: **descriptive** (percentile reported). With none: **descriptive** (false alarms only).
- **What would count against my negative prior:** a supported verdict here, especially with the level alarm giving less lead.

## Result
Arm W = 15 min. τ* = 0.538 (frozen from synthetic S0). Onsets (O1): 4; O1-slow variant: 5. Onsets dropped at ℓ = 4: 0 too early (< 24 windows of history), 3 too sparse, 0 not low at t_e.

| Onset | Project | Share at onset (k/n) | Baseline → persistence | Evaluable at ℓ = 4 | EWS alarm | Level alarm | Momentum alarm |
| --- | --- | --- | --- | --- | --- | --- | --- |
| w81 | `genuine-tanuki-926a91.netlify.app` | 0.80 (4/5) | 0.00 → 0.93 | no | miss | miss | miss |
| w134 | `poverty-etl` | 1.00 (5/5) | 0.00 → 1.00 | yes | miss | miss | miss |
| w69 | `peppy-melomakarona-7f16eb.netlify.app` | 1.00 (8/8) | 0.00 → 0.69 | no | not watchable | not watchable | not watchable |
| w49 | `Google doc #7` | 0.75 (3/4) | 0.00 → 0.77 | no | not watchable | not watchable | not watchable |

| Test | Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- | --- |
| P0 onsets | 0–1 | 4 | – | outside the expected range |
| P1 composite percentile among placebos | < 0.9 | 0.46 (vs 136 placebo segments) | 0.5 | as predicted |
| P3 EWS alarm | hits ≤ half; FAR ≥ 5% | 0/4 hit (2 watchable); 2 false alarms in 307 watched (project, window) = 0.7%; PPV 0.00 | level alarm 0/4 hit, FAR 2.6% | as predicted |
| W = 30 arm | – | onsets 5; evaluable 2; AUC 0.37; EWS hits 0/5 | – | robustness |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| G ground truth | 1 | onsets found by the rule: 4 (compare H11's narrative for this period) |

## Notes
- 2026-10-04: prediction written before running this period.
- 2026-10-04: round 1 run (`analysis/explore.py`); data in `data/processed/H27-herding-early-warning/G18/round1_w*.json`.
- 2026-10-04 (post hoc): 3 of the 4 onsets land on projects never mentioned before in the period (two Netlify sites and a Google doc; 3–8 agents in the first window the project appears). No share-based indicator can warn of these. H11's last-day convergence is not an O1 onset (none of the W = 15 or W = 30 onsets is on the last day): it did not start from a low baseline.
