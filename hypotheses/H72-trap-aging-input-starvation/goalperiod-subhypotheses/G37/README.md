# H72 × G37: trap aging vs input starvation (2026-03-30 → 2026-04-01)

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · 8 agents with gates · 3 non-holdout days · 250 idle gates. No split: the hazard has agent fixed effects and day-block CIs.

## Why this period
Replication layer: the common two-clock hazard on every period with ≥ 200 idle gates (card, Design). Nothing period-specific is claimed here.

## Prediction
*Written 2026-10-04, before running on this period. Templated (card, "Per-period verdict rule", amended A1 before real data).*
If trap aging is input starvation, the aging slope β_a0 < 0 vanishes once s (time since the last novel read) is controlled, and β_s < 0. Expected here (card P4/P5): aging, where present, survives the control; in regime I, s barely varies.

## Result
Run 2026-10-04 with `analysis/run_period.py` (B = 200 day-block draws); numbers in `data/processed/H72-trap-aging-input-starvation/G37/results.json`. Logit, agent FE, sustained escape, a = a_sus, s = s_novel (min, ln).

| Quantity | Estimate [95% CI] |
| --- | --- |
| gates / sustained escapes | 240 / 163 (0.68) |
| median a, s (min) | 4.4, 10.1 |
| β_a0 (age only) | -0.28 [-0.52, +6.56] |
| β_a (age, s controlled) | -0.23 [-0.23, +9.69] |
| β_s (starvation, a controlled) | -0.09 [-2.34, +0.35] |
| ρ aging absorbed | +0.19 [-0.48, +0.88] |
| starvation-implied aging b_impl (O3b) | -0.05 [-0.94, +0.22] |
| CV gain, s adds / a adds (nats per 1,000 gates) | -30.8 / -5.8 |
| variant s_content: β_a, β_s | -0.23 [-0.23, +0.96], -0.08 [-0.95, +0.57] |
| variant s_dir: β_a, β_s | -0.23 [-0.49, +1.08], -0.04 [-0.21, +0.38] |
| variant s_peer: β_a, β_s | -0.23 [-0.23, +0.96], -0.09 [-0.95, +0.53] |
| in-flight placebo (A2 window), Wald | +0.72 [-1.63, +3.06] |
| robustness β_a / β_s (cloglog; h ≥ 0.25; no first day) | cloglog: -0.23 / -0.02; trim_h025: -0.22 / -0.08; no_first_day: +0.19 / +0.25 |

Verdict: **descriptive (no aging to explain)**.

## Scorecard (period-specific axes)
- C: the two-clock model is scored on held-out days (5 day folds); a adds -5.8 nats per 1,000 gates, s adds -30.8.
- H: the starvation clock is the rival here; see the verdict.

## Round 2 (2026-10-05): chatter hold

**Round-2 verdict (chatter hold, R1):** descriptive (CI includes 0; power 0.10 at −0.25)

*Prediction (written 2026-10-05 before running; card "Round 2", R1 and amendments R2-A1/A2):* escape at a wake falls with ln(1 + undirected items read at the 5 calls before it), β_C < 0, in the full model (agent FE + base + ln a + ln k + ln s_dir + dose + ln(1 − f_call)). Only G51 is powered (synthetic); elsewhere a CI including 0 is descriptive.

*Result* (`analysis/run_r2.py`; `data/processed/H72-trap-aging-input-starvation/r2/results_r2.json`; day-block bootstrap 200):

| Quantity | Estimate [95% CI] |
| --- | --- |
| wakes / sustained escapes (consolidation-start traps dropped) | 238 / 161 |
| synthetic power for β_C = −0.25 | 0.10 |
| β_C, full model | +0.19 [-0.55, +118.06] |
| β_C, B + A + C | +0.29 [-0.40, +174.86] |
| ln k (wake index), full model | +0.43 [-0.15, +100.25] |
| ln s_dir (starvation), full model | +0.08 [-43.84, +0.47] |
| ln(1 − f_call) (urn coefficient), full model | +5.90 [+2.56, +13.28] |
| held-out gain over the base (nats per 1,000 wakes) | clocks +23.7 [-59.5, +166.6], starvation -2.6 [-33.0, +44.9], chatter -111.9 [-321.2, -4.4], self-share +40.6 [-15.3, +133.9] |
| transfer of G51 slopes (held-out gain, nats per 1,000 wakes) | starvation -2.6 [-8.7, +4.1], chatter +4.5 [-20.0, +33.9], self-share +46.3 [+6.6, +120.7] |

