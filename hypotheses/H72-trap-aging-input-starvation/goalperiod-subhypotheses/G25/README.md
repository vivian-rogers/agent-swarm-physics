# H72 × G25: trap aging vs input starvation (2025-12-29 → 2026-01-02)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · 8 agents with gates · 5 non-holdout days · 221 idle gates. No split: the hazard has agent fixed effects and day-block CIs.

## Why this period
Replication layer: the common two-clock hazard on every period with ≥ 200 idle gates (card, Design). Nothing period-specific is claimed here.

## Prediction
*Written 2026-10-04, before running on this period. Templated (card, "Per-period verdict rule", amended A1 before real data).*
If trap aging is input starvation, the aging slope β_a0 < 0 vanishes once s (time since the last novel read) is controlled, and β_s < 0. Expected here (card P4/P5): aging, where present, survives the control; in regime I, s barely varies.

## Result
Run 2026-10-04 with `analysis/run_period.py` (B = 200 day-block draws); numbers in `data/processed/H72-trap-aging-input-starvation/G25/results.json`. Logit, agent FE, sustained escape, a = a_sus, s = s_novel (min, ln).

| Quantity | Estimate [95% CI] |
| --- | --- |
| gates / sustained escapes | 219 / 66 (0.30) |
| median a, s (min) | 5.9, 1.2 |
| β_a0 (age only) | -0.25 [-0.43, +23.95] |
| β_a (age, s controlled) | -0.22 [-0.39, +25.84] |
| β_s (starvation, a controlled) | +1.28 [+0.26, +2.63] |
| ρ aging absorbed | +0.13 [-1.50, +1.76] |
| starvation-implied aging b_impl (O3b) | -0.05 [-0.18, +0.95] |
| CV gain, s adds / a adds (nats per 1,000 gates) | +3.0 / -42.9 |
| variant s_content: β_a, β_s | -0.25 [-0.42, +2.26], -0.06 [-0.41, +1.44] |
| variant s_dir: β_a, β_s | -0.40 [-0.61, +2.60], +0.42 [+0.28, +0.97] |
| variant s_peer: β_a, β_s | -0.22 [-0.41, +2.05], +1.28 [+0.45, +2.09] |
| any escape (a_any): β_a0, β_a, β_s | +0.01, +0.04 [-0.17, +4.84], +1.38 [+0.53, +5.66] |
| in-flight placebo (A2 window), Wald | -0.13 [-0.96, +0.70] |
| robustness β_a / β_s (cloglog; h ≥ 0.25; no first day) | cloglog: -0.20 / +0.94; trim_h025: -0.28 / +1.29; no_first_day: +0.17 / +1.59 |

Verdict: **descriptive (no aging to explain)**.

## Scorecard (period-specific axes)
- C: the two-clock model is scored on held-out days (5 day folds); a adds -42.9 nats per 1,000 gates, s adds +3.0.
- H: the starvation clock is the rival here; see the verdict.

## Round 2 (2026-10-05): chatter hold

**Round-2 verdict (chatter hold, R1):** supported

*Prediction (written 2026-10-05 before running; card "Round 2", R1 and amendments R2-A1/A2):* escape at a wake falls with ln(1 + undirected items read at the 5 calls before it), β_C < 0, in the full model (agent FE + base + ln a + ln k + ln s_dir + dose). Only G51 is powered (synthetic); elsewhere a CI including 0 is descriptive.

*Result* (`analysis/run_r2.py`; `data/processed/H72-trap-aging-input-starvation/r2/results_r2.json`; day-block bootstrap 200):

| Quantity | Estimate [95% CI] |
| --- | --- |
| wakes / sustained escapes (consolidation-start traps dropped) | 192 / 60 |
| synthetic power for β_C = −0.25 | 0.07 |
| β_C, full model | -0.75 [-103.13, -0.31] |
| β_C, B + A + C | -0.47 [-96.07, -0.08] |
| ln k (wake index), full model | -2.02 [-4.10, +45.34] |
| ln s_dir (starvation), full model | +0.63 [+0.41, +25.18] |
| held-out gain over the base (nats per 1,000 wakes) | clocks +68.2 [+10.1, +157.3], starvation -103.8 [-299.8, -1.5], chatter -7.0 [-37.1, +14.0] |

