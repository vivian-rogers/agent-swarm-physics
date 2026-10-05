# H72 × G40: trap aging vs input starvation (2026-05-04 → 2026-05-08)

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · 11 agents with gates · 5 non-holdout days · 205 idle gates. No split: the hazard has agent fixed effects and day-block CIs.

## Why this period
Replication layer: the common two-clock hazard on every period with ≥ 200 idle gates (card, Design). Nothing period-specific is claimed here.

## Prediction
*Written 2026-10-04, before running on this period. Templated (card, "Per-period verdict rule", amended A1 before real data).*
If trap aging is input starvation, the aging slope β_a0 < 0 vanishes once s (time since the last novel read) is controlled, and β_s < 0. Expected here (card P4/P5): aging, where present, survives the control; in regime I, s barely varies.

## Result
Run 2026-10-04 with `analysis/run_period.py` (B = 200 day-block draws); numbers in `data/processed/H72-trap-aging-input-starvation/G40/results.json`. Logit, agent FE, sustained escape, a = a_sus, s = s_novel (min, ln).

| Quantity | Estimate [95% CI] |
| --- | --- |
| gates / sustained escapes | 204 / 171 (0.84) |
| median a, s (min) | 0.7, 1.3 |
| β_a0 (age only) | +1.14 [-0.35, +6.19] |
| β_a (age, s controlled) | +1.07 [-0.33, +8.20] |
| β_s (starvation, a controlled) | +0.21 [-1.45, +0.57] |
| ρ aging absorbed | +0.06 [-0.24, +1.97] |
| starvation-implied aging b_impl (O3b) | +0.06 [-0.69, +0.10] |
| CV gain, s adds / a adds (nats per 1,000 gates) | -14.5 / -18.7 |
| variant s_content: β_a, β_s | +1.02 [-0.39, +7.33], +0.37 [-0.65, +0.80] |
| variant s_dir: β_a, β_s | +1.08 [-0.49, +4.92], -0.00 [-0.84, +0.41] |
| variant s_peer: β_a, β_s | +1.05 [-0.35, +7.44], +0.36 [-0.96, +0.71] |
| in-flight placebo (A2 window), Wald | +0.44 [-0.91, +1.79] |
| robustness β_a / β_s (cloglog; h ≥ 0.25; no first day) | cloglog: +0.27 / +0.23; trim_h025: +0.83 / +0.30; no_first_day: +0.02 / +0.27 |

Verdict: **descriptive (no aging to explain)**.

## Scorecard (period-specific axes)
- C: the two-clock model is scored on held-out days (5 day folds); a adds -18.7 nats per 1,000 gates, s adds -14.5.
- H: the starvation clock is the rival here; see the verdict.

## Round 2 (2026-10-05): chatter hold

**Round-2 verdict (chatter hold, R1):** descriptive (CI includes 0; power 0.23 at −0.25)

*Prediction (written 2026-10-05 before running; card "Round 2", R1 and amendments R2-A1/A2):* escape at a wake falls with ln(1 + undirected items read at the 5 calls before it), β_C < 0, in the full model (agent FE + base + ln a + ln k + ln s_dir + dose + ln(1 − f_call)). Only G51 is powered (synthetic); elsewhere a CI including 0 is descriptive.

*Result* (`analysis/run_r2.py`; `data/processed/H72-trap-aging-input-starvation/r2/results_r2.json`; day-block bootstrap 200):

| Quantity | Estimate [95% CI] |
| --- | --- |
| wakes / sustained escapes (consolidation-start traps dropped) | 197 / 164 |
| synthetic power for β_C = −0.25 | 0.23 |
| β_C, full model | +0.09 [-0.73, +3.76] |
| β_C, B + A + C | -0.13 [-0.58, +1.86] |
| ln k (wake index), full model | +4.47 [-7.14, +11.87] |
| ln s_dir (starvation), full model | -0.03 [-1.54, +0.30] |
| ln(1 − f_call) (urn coefficient), full model | +6.21 [-7.89, +30.48] |
| held-out gain over the base (nats per 1,000 wakes) | clocks -9.7 [-49.2, +45.5], starvation -139.2 [-217.0, -61.5], chatter -7.3 [-19.2, +0.5], self-share +70.6 [+10.2, +160.4] |
| transfer of G51 slopes (held-out gain, nats per 1,000 wakes) | starvation -0.2 [-4.0, +4.5], chatter +7.2 [-0.6, +17.3], self-share +32.5 [+9.3, +69.7] |

