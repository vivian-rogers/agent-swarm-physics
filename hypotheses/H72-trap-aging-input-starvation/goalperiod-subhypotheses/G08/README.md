# H72 × G08: trap aging vs input starvation (2025-07-18 → 2025-08-12)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · 4 agents with gates · 15 non-holdout days · 408 idle gates. No split: the hazard has agent fixed effects and day-block CIs.

## Why this period
Replication layer: the common two-clock hazard on every period with ≥ 200 idle gates (card, Design). Nothing period-specific is claimed here.

## Prediction
*Written 2026-10-04, before running on this period. Templated (card, "Per-period verdict rule", amended A1 before real data).*
If trap aging is input starvation, the aging slope β_a0 < 0 vanishes once s (time since the last novel read) is controlled, and β_s < 0. Expected here (card P4/P5): aging, where present, survives the control; in regime I, s barely varies.

## Result
Run 2026-10-04 with `analysis/run_period.py` (B = 200 day-block draws); numbers in `data/processed/H72-trap-aging-input-starvation/G08/results.json`. Logit, agent FE, sustained escape, a = a_sus, s = s_novel (min, ln).

| Quantity | Estimate [95% CI] |
| --- | --- |
| gates / sustained escapes | 400 / 57 (0.14) |
| median a, s (min) | 2.4, 1.1 |
| β_a0 (age only) | +0.03 [-0.47, +0.88] |
| β_a (age, s controlled) | +0.03 [-0.43, +0.88] |
| β_s (starvation, a controlled) | +0.18 [-0.23, +0.55] |
| ρ aging absorbed | +0.13 [-0.40, +0.71] |
| starvation-implied aging b_impl (O3b) | -0.01 [-0.06, +0.03] |
| CV gain, s adds / a adds (nats per 1,000 gates) | -6.1 / -2.9 |
| variant s_content: β_a, β_s | +0.03 [-0.45, +0.90], +0.20 [-0.29, +0.53] |
| variant s_dir: β_a, β_s | +0.06 [-0.39, +0.90], +0.20 [+0.00, +0.43] |
| variant s_peer: β_a, β_s | +0.03 [-0.46, +0.88], +0.18 [-0.30, +0.56] |
| any escape (a_any): β_a0, β_a, β_s | -0.20, -0.21 [-0.76, +0.69], +0.09 [-0.55, +0.53] |
| in-flight placebo (A2 window), Wald | +1.70 [+0.72, +2.67] |
| robustness β_a / β_s (cloglog; h ≥ 0.25; no first day) | cloglog: +0.02 / +0.13; trim_h025: +0.02 / +0.21; no_first_day: +0.01 / +0.17 |

Verdict: **descriptive (no aging to explain)**.

## Scorecard (period-specific axes)
- C: the two-clock model is scored on held-out days (5 day folds); a adds -2.9 nats per 1,000 gates, s adds -6.1.
- H: the starvation clock is the rival here; see the verdict.

## Round 2 (2026-10-05): chatter hold

**Round-2 verdict (chatter hold, R1):** descriptive (CI includes 0; power 0.17 at −0.25)

*Prediction (written 2026-10-05 before running; card "Round 2", R1 and amendments R2-A1/A2):* escape at a wake falls with ln(1 + undirected items read at the 5 calls before it), β_C < 0, in the full model (agent FE + base + ln a + ln k + ln s_dir + dose). Only G51 is powered (synthetic); elsewhere a CI including 0 is descriptive.

*Result* (`analysis/run_r2.py`; `data/processed/H72-trap-aging-input-starvation/r2/results_r2.json`; day-block bootstrap 200):

| Quantity | Estimate [95% CI] |
| --- | --- |
| wakes / sustained escapes (consolidation-start traps dropped) | 396 / 54 |
| synthetic power for β_C = −0.25 | 0.17 |
| β_C, full model | -0.15 [-0.79, +0.39] |
| β_C, B + A + C | -0.11 [-0.71, +0.42] |
| ln k (wake index), full model | -0.68 [-1.55, +1.08] |
| ln s_dir (starvation), full model | +0.18 [-0.00, +0.65] |
| held-out gain over the base (nats per 1,000 wakes) | clocks +4.9 [-4.4, +13.4], starvation -9.3 [-19.0, -1.0], chatter -1.4 [-3.3, +0.7] |

