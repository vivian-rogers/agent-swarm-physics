# H72 × G16: trap aging vs input starvation (2025-10-06 → 2025-10-10)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · 7 agents with gates · 5 non-holdout days · 274 idle gates. No split: the hazard has agent fixed effects and day-block CIs.

## Why this period
Replication layer: the common two-clock hazard on every period with ≥ 200 idle gates (card, Design). Nothing period-specific is claimed here.

## Prediction
*Written 2026-10-04, before running on this period. Templated (card, "Per-period verdict rule", amended A1 before real data).*
If trap aging is input starvation, the aging slope β_a0 < 0 vanishes once s (time since the last novel read) is controlled, and β_s < 0. Expected here (card P4/P5): aging, where present, survives the control; in regime I, s barely varies.

## Result
Run 2026-10-04 with `analysis/run_period.py` (B = 200 day-block draws); numbers in `data/processed/H72-trap-aging-input-starvation/G16/results.json`. Logit, agent FE, sustained escape, a = a_sus, s = s_novel (min, ln).

| Quantity | Estimate [95% CI] |
| --- | --- |
| gates / sustained escapes | 270 / 54 (0.20) |
| median a, s (min) | 9.7, 0.7 |
| β_a0 (age only) | -0.71 [-1.56, +0.41] |
| β_a (age, s controlled) | -1.15 [-1.81, +0.76] |
| β_s (starvation, a controlled) | +1.22 [-0.65, +1.78] |
| ρ aging absorbed | -0.62 [-8.12, +47.51] |
| starvation-implied aging b_impl (O3b) | +0.24 [-0.34, +0.33] |
| CV gain, s adds / a adds (nats per 1,000 gates) | +149.6 / +396.2 |
| variant s_content: β_a, β_s | -0.89 [-1.89, +0.26], +1.08 [-0.05, +1.57] |
| variant s_dir: β_a, β_s | -0.71 [-1.85, +0.27], -0.01 [-1.28, +0.17] |
| variant s_peer: β_a, β_s | -1.15 [-1.97, -0.00], +1.22 [+0.09, +1.93] |
| any escape (a_any): β_a0, β_a, β_s | -0.28, -0.42 [-0.61, +0.57], +0.40 [-0.35, +0.63] |
| in-flight placebo (A2 window), Wald | -0.85 [-1.89, +0.20] |
| robustness β_a / β_s (cloglog; h ≥ 0.25; no first day) | cloglog: -0.97 / +0.95; trim_h025: -1.15 / +1.22 |

Verdict: **descriptive (no aging to explain)**.

## Scorecard (period-specific axes)
- C: the two-clock model is scored on held-out days (5 day folds); a adds +396.2 nats per 1,000 gates, s adds +149.6.
- H: the starvation clock is the rival here; see the verdict.

## Round 2 (2026-10-05): chatter hold

**Round-2 verdict (chatter hold, R1):** descriptive (CI includes 0; power 0.05 at −0.25)

*Prediction (written 2026-10-05 before running; card "Round 2", R1 and amendments R2-A1/A2):* escape at a wake falls with ln(1 + undirected items read at the 5 calls before it), β_C < 0, in the full model (agent FE + base + ln a + ln k + ln s_dir + dose). Only G51 is powered (synthetic); elsewhere a CI including 0 is descriptive.

*Result* (`analysis/run_r2.py`; `data/processed/H72-trap-aging-input-starvation/r2/results_r2.json`; day-block bootstrap 200):

| Quantity | Estimate [95% CI] |
| --- | --- |
| wakes / sustained escapes (consolidation-start traps dropped) | 270 / 54 |
| synthetic power for β_C = −0.25 | 0.05 |
| β_C, full model | +0.26 [-0.79, +3.88] |
| β_C, B + A + C | +0.25 [-0.90, +3.90] |
| ln k (wake index), full model | -1.28 [-1.74, +1.21] |
| ln s_dir (starvation), full model | +0.04 [-0.24, +0.36] |
| held-out gain over the base (nats per 1,000 wakes) | clocks +217.4 [+27.0, +540.7], starvation -31.6 [-91.7, +1.4], chatter -35.1 [-72.5, -1.3] |

