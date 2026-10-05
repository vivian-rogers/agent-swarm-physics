# H72 × G18: trap aging vs input starvation (2025-10-20 → 2025-10-31)

**Verdict:** failed
**Role:** replication
**Period:** regime I · 7 agents with gates · 10 non-holdout days · 1425 idle gates. No split: the hazard has agent fixed effects and day-block CIs.

## Why this period
Replication layer: the common two-clock hazard on every period with ≥ 200 idle gates (card, Design). Nothing period-specific is claimed here.

## Prediction
*Written 2026-10-04, before running on this period. Templated (card, "Per-period verdict rule", amended A1 before real data).*
If trap aging is input starvation, the aging slope β_a0 < 0 vanishes once s (time since the last novel read) is controlled, and β_s < 0. Expected here (card P4/P5): aging, where present, survives the control; in regime I, s barely varies.

## Result
Run 2026-10-04 with `analysis/run_period.py` (B = 200 day-block draws); numbers in `data/processed/H72-trap-aging-input-starvation/G18/results.json`. Logit, agent FE, sustained escape, a = a_sus, s = s_novel (min, ln).

| Quantity | Estimate [95% CI] |
| --- | --- |
| gates / sustained escapes | 1418 / 332 (0.23) |
| median a, s (min) | 4.8, 0.5 |
| β_a0 (age only) | -0.44 [-0.67, -0.08] |
| β_a (age, s controlled) | -0.56 [-0.76, -0.19] |
| β_s (starvation, a controlled) | +0.41 [+0.19, +0.58] |
| ρ aging absorbed | -0.27 [-1.60, -0.11] |
| starvation-implied aging b_impl (O3b) | +0.09 [+0.03, +0.13] |
| CV gain, s adds / a adds (nats per 1,000 gates) | +5.3 / +28.1 |
| variant s_content: β_a, β_s | -0.47 [-0.65, -0.11], +0.14 [-0.01, +0.41] |
| variant s_dir: β_a, β_s | -0.47 [-0.63, -0.13], +0.14 [-0.03, +0.36] |
| variant s_peer: β_a, β_s | -0.56 [-0.74, -0.20], +0.41 [+0.21, +0.54] |
| any escape (a_any): β_a0, β_a, β_s | -0.09, -0.36 [-0.52, -0.02], +0.70 [+0.55, +0.87] |
| in-flight placebo (A2 window), Wald | -0.08 [-0.39, +0.22] |
| robustness β_a / β_s (cloglog; h ≥ 0.25; no first day) | cloglog: -0.49 / +0.34; trim_h025: -0.55 / +0.39; no_first_day: -0.48 / +0.47 |

Verdict: **failed**.

## Scorecard (period-specific axes)
- C: the two-clock model is scored on held-out days (5 day folds); a adds +28.1 nats per 1,000 gates, s adds +5.3.
- H: the starvation clock is the rival here; see the verdict.

## Round 2 (2026-10-05): chatter hold

**Round-2 verdict (chatter hold, R1):** descriptive (CI includes 0; power 0.42 at −0.25)

*Prediction (written 2026-10-05 before running; card "Round 2", R1 and amendments R2-A1/A2):* escape at a wake falls with ln(1 + undirected items read at the 5 calls before it), β_C < 0, in the full model (agent FE + base + ln a + ln k + ln s_dir + dose). Only G51 is powered (synthetic); elsewhere a CI including 0 is descriptive.

*Result* (`analysis/run_r2.py`; `data/processed/H72-trap-aging-input-starvation/r2/results_r2.json`; day-block bootstrap 200):

| Quantity | Estimate [95% CI] |
| --- | --- |
| wakes / sustained escapes (consolidation-start traps dropped) | 1236 / 307 |
| synthetic power for β_C = −0.25 | 0.42 |
| β_C, full model | -0.24 [-0.45, +0.00] |
| β_C, B + A + C | -0.17 [-0.37, +0.07] |
| ln k (wake index), full model | -0.47 [-0.81, -0.02] |
| ln s_dir (starvation), full model | +0.13 [-0.03, +0.30] |
| held-out gain over the base (nats per 1,000 wakes) | clocks +32.1 [+6.3, +61.6], starvation -10.2 [-24.3, -0.6], chatter -1.0 [-2.8, +0.7] |

