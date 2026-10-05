# H72 × G38: trap aging vs input starvation (2026-04-02 → 2026-04-24)

**Verdict:** failed
**Role:** replication
**Period:** regime III · 11 agents with gates · 17 non-holdout days · 1628 idle gates. No split: the hazard has agent fixed effects and day-block CIs.

## Why this period
Replication layer: the common two-clock hazard on every period with ≥ 200 idle gates (card, Design). Nothing period-specific is claimed here.

## Prediction
*Written 2026-10-04, before running on this period. Templated (card, "Per-period verdict rule", amended A1 before real data).*
If trap aging is input starvation, the aging slope β_a0 < 0 vanishes once s (time since the last novel read) is controlled, and β_s < 0. Expected here (card P4/P5): aging, where present, survives the control; in regime I, s barely varies.

## Result
Run 2026-10-04 with `analysis/run_period.py` (B = 200 day-block draws); numbers in `data/processed/H72-trap-aging-input-starvation/G38/results.json`. Logit, agent FE, sustained escape, a = a_sus, s = s_novel (min, ln).

| Quantity | Estimate [95% CI] |
| --- | --- |
| gates / sustained escapes | 1616 / 860 (0.53) |
| median a, s (min) | 2.7, 2.9 |
| β_a0 (age only) | -0.38 [-0.53, -0.16] |
| β_a (age, s controlled) | -0.39 [-0.56, -0.12] |
| β_s (starvation, a controlled) | +0.03 [-0.21, +0.32] |
| ρ aging absorbed | -0.02 [-0.15, +0.24] |
| starvation-implied aging b_impl (O3b) | +0.01 [-0.05, +0.06] |
| CV gain, s adds / a adds (nats per 1,000 gates) | -1.4 / +9.3 |
| variant s_content: β_a, β_s | -0.39 [-0.55, -0.11], +0.08 [-0.15, +0.25] |
| variant s_dir: β_a, β_s | -0.38 [-0.51, -0.14], -0.02 [-0.09, +0.05] |
| variant s_peer: β_a, β_s | -0.39 [-0.57, -0.12], +0.04 [-0.25, +0.27] |
| any escape (a_any): β_a0, β_a, β_s | -0.74, -0.84 [-1.20, -0.16], +0.43 [-0.06, +0.80] |
| in-flight placebo (A2 window), Wald | -0.12 [-0.74, +0.50] |
| robustness β_a / β_s (cloglog; h ≥ 0.25; no first day) | cloglog: -0.29 / +0.01; trim_h025: -0.39 / +0.04; no_first_day: -0.37 / +0.01 |

Verdict: **failed**.

## Scorecard (period-specific axes)
- C: the two-clock model is scored on held-out days (5 day folds); a adds +9.3 nats per 1,000 gates, s adds -1.4.
- H: the starvation clock is the rival here; see the verdict.

## Round 2 (2026-10-05): chatter hold

**Round-2 verdict (chatter hold, R1):** descriptive (CI includes 0; power 0.33 at −0.25)

*Prediction (written 2026-10-05 before running; card "Round 2", R1 and amendments R2-A1/A2):* escape at a wake falls with ln(1 + undirected items read at the 5 calls before it), β_C < 0, in the full model (agent FE + base + ln a + ln k + ln s_dir + dose + ln(1 − f_call)). Only G51 is powered (synthetic); elsewhere a CI including 0 is descriptive.

*Result* (`analysis/run_r2.py`; `data/processed/H72-trap-aging-input-starvation/r2/results_r2.json`; day-block bootstrap 200):

| Quantity | Estimate [95% CI] |
| --- | --- |
| wakes / sustained escapes (consolidation-start traps dropped) | 1598 / 845 |
| synthetic power for β_C = −0.25 | 0.33 |
| β_C, full model | +0.09 [-0.23, +0.38] |
| β_C, B + A + C | +0.05 [-0.24, +0.31] |
| ln k (wake index), full model | -0.09 [-0.35, +0.20] |
| ln s_dir (starvation), full model | -0.04 [-0.13, +0.02] |
| ln(1 − f_call) (urn coefficient), full model | +1.91 [+0.85, +3.32] |
| held-out gain over the base (nats per 1,000 wakes) | clocks +7.4 [+1.1, +13.6], starvation -0.5 [-5.2, +3.2], chatter -1.7 [-4.0, +0.5], self-share +9.0 [-2.8, +20.4] |
| aging share explained ε (held out) | starvation +0.04 [-0.33, +0.31], chatter -0.06 [-0.23, +0.01], self-share +0.72 [+0.41, +1.32] |
| transfer of G51 slopes (held-out gain, nats per 1,000 wakes) | starvation -1.1 [-1.9, -0.3], chatter -2.2 [-7.1, +2.6], self-share +10.2 [+0.2, +19.9] |

Reading: not powered for R1 or the reconcile (A2, A3); the direction agrees with G51 for self-share (ε 0.72) and not for chatter.

