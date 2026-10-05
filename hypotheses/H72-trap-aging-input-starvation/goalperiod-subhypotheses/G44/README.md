# H72 × G44: trap aging vs input starvation (2026-05-26 → 2026-05-29)

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · 14 agents with gates · 4 non-holdout days · 429 idle gates. No split: the hazard has agent fixed effects and day-block CIs.

## Why this period
Replication layer: the common two-clock hazard on every period with ≥ 200 idle gates (card, Design). Nothing period-specific is claimed here.

## Prediction
*Written 2026-10-04, before running on this period. Templated (card, "Per-period verdict rule", amended A1 before real data).*
If trap aging is input starvation, the aging slope β_a0 < 0 vanishes once s (time since the last novel read) is controlled, and β_s < 0. Expected here (card P4/P5): aging, where present, survives the control; in regime I, s barely varies.

## Result
Run 2026-10-04 with `analysis/run_period.py` (B = 200 day-block draws); numbers in `data/processed/H72-trap-aging-input-starvation/G44/results.json`. Logit, agent FE, sustained escape, a = a_sus, s = s_novel (min, ln).

| Quantity | Estimate [95% CI] |
| --- | --- |
| gates / sustained escapes | 418 / 198 (0.47) |
| median a, s (min) | 3.3, 3.1 |
| β_a0 (age only) | +0.05 [-0.04, +1.61] |
| β_a (age, s controlled) | +0.02 [-0.09, +1.96] |
| β_s (starvation, a controlled) | +0.22 [+0.01, +1.66] |
| ρ aging absorbed | +0.69 [-1.09, +6.88] |
| starvation-implied aging b_impl (O3b) | +0.02 [-0.19, +0.07] |
| CV gain, s adds / a adds (nats per 1,000 gates) | -9.9 / -6.8 |
| variant s_content: β_a, β_s | +0.02 [-0.08, +1.22], +0.18 [-0.05, +1.07] |
| variant s_dir: β_a, β_s | +0.01 [-0.08, +1.10], +0.23 [-0.07, +0.76] |
| variant s_peer: β_a, β_s | +0.02 [-0.08, +1.22], +0.19 [-0.04, +1.07] |
| any escape (a_any): β_a0, β_a, β_s | -0.10, -0.17 [-0.20, +0.38], +0.39 [-0.22, +1.07] |
| in-flight placebo (A2 window), Wald | -0.42 [-1.39, +0.55] |
| robustness β_a / β_s (cloglog; h ≥ 0.25; no first day) | cloglog: -0.00 / +0.14; trim_h025: -0.03 / +0.09; no_first_day: +0.02 / +0.29 |

Verdict: **descriptive (no aging to explain)**.

## Scorecard (period-specific axes)
- C: the two-clock model is scored on held-out days (5 day folds); a adds -6.8 nats per 1,000 gates, s adds -9.9.
- H: the starvation clock is the rival here; see the verdict.

## Round 2 (2026-10-05): chatter hold

**Round-2 verdict (chatter hold, R1):** descriptive (CI includes 0; power 0.23 at −0.25)

*Prediction (written 2026-10-05 before running; card "Round 2", R1 and amendments R2-A1/A2):* escape at a wake falls with ln(1 + undirected items read at the 5 calls before it), β_C < 0, in the full model (agent FE + base + ln a + ln k + ln s_dir + dose + ln(1 − f_call)). Only G51 is powered (synthetic); elsewhere a CI including 0 is descriptive.

*Result* (`analysis/run_r2.py`; `data/processed/H72-trap-aging-input-starvation/r2/results_r2.json`; day-block bootstrap 200):

| Quantity | Estimate [95% CI] |
| --- | --- |
| wakes / sustained escapes (consolidation-start traps dropped) | 414 / 197 |
| synthetic power for β_C = −0.25 | 0.23 |
| β_C, full model | -0.27 [-0.84, +0.02] |
| β_C, B + A + C | -0.25 [-0.94, -0.09] |
| ln k (wake index), full model | +0.44 [-1.32, +2.32] |
| ln s_dir (starvation), full model | +0.27 [-0.07, +1.08] |
| ln(1 − f_call) (urn coefficient), full model | +1.58 [+0.99, +4.77] |
| held-out gain over the base (nats per 1,000 wakes) | clocks -26.1 [-48.2, -4.1], starvation -505.0 [-1461.3, +5.8], chatter -3.6 [-13.8, +3.3], self-share +5.5 [+2.3, +9.8] |
| transfer of G51 slopes (held-out gain, nats per 1,000 wakes) | starvation -0.7 [-3.8, +1.2], chatter +0.2 [-2.9, +5.1], self-share -0.7 [-14.4, +6.6] |

