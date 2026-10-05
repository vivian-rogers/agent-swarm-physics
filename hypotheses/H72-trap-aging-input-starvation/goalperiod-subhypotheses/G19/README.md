# H72 × G19: trap aging vs input starvation (2025-11-03 → 2025-11-14)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · 7 agents with gates · 10 non-holdout days · 778 idle gates. No split: the hazard has agent fixed effects and day-block CIs.

## Why this period
Replication layer: the common two-clock hazard on every period with ≥ 200 idle gates (card, Design). Nothing period-specific is claimed here.

## Prediction
*Written 2026-10-04, before running on this period. Templated (card, "Per-period verdict rule", amended A1 before real data).*
If trap aging is input starvation, the aging slope β_a0 < 0 vanishes once s (time since the last novel read) is controlled, and β_s < 0. Expected here (card P4/P5): aging, where present, survives the control; in regime I, s barely varies.

## Result
Run 2026-10-04 with `analysis/run_period.py` (B = 200 day-block draws); numbers in `data/processed/H72-trap-aging-input-starvation/G19/results.json`. Logit, agent FE, sustained escape, a = a_sus, s = s_novel (min, ln).

| Quantity | Estimate [95% CI] |
| --- | --- |
| gates / sustained escapes | 772 / 219 (0.28) |
| median a, s (min) | 5.1, 0.9 |
| β_a0 (age only) | -0.16 [-0.30, +0.25] |
| β_a (age, s controlled) | -0.39 [-0.55, +0.07] |
| β_s (starvation, a controlled) | +0.73 [+0.33, +1.02] |
| ρ aging absorbed | -1.50 [-17.51, +10.62] |
| starvation-implied aging b_impl (O3b) | +0.17 [+0.05, +0.26] |
| CV gain, s adds / a adds (nats per 1,000 gates) | +13.4 / +18.4 |
| variant s_content: β_a, β_s | -0.26 [-0.54, +0.05], +0.51 [+0.27, +1.07] |
| variant s_dir: β_a, β_s | -0.12 [-0.32, +0.30], -0.05 [-0.24, +0.16] |
| variant s_peer: β_a, β_s | -0.39 [-0.58, -0.02], +0.73 [+0.22, +1.05] |
| any escape (a_any): β_a0, β_a, β_s | -0.11, -0.35 [-0.54, +0.13], +0.73 [+0.33, +1.20] |
| in-flight placebo (A2 window), Wald | +0.12 [-0.31, +0.54] |
| robustness β_a / β_s (cloglog; h ≥ 0.25; no first day) | cloglog: -0.33 / +0.60; trim_h025: -0.39 / +0.76; no_first_day: -0.33 / +0.67 |

Verdict: **descriptive (no aging to explain)**.

## Scorecard (period-specific axes)
- C: the two-clock model is scored on held-out days (5 day folds); a adds +18.4 nats per 1,000 gates, s adds +13.4.
- H: the starvation clock is the rival here; see the verdict.

## Round 2 (2026-10-05): chatter hold

**Round-2 verdict (chatter hold, R1):** supported

*Prediction (written 2026-10-05 before running; card "Round 2", R1 and amendments R2-A1/A2):* escape at a wake falls with ln(1 + undirected items read at the 5 calls before it), β_C < 0, in the full model (agent FE + base + ln a + ln k + ln s_dir + dose). Only G51 is powered (synthetic); elsewhere a CI including 0 is descriptive.

*Result* (`analysis/run_r2.py`; `data/processed/H72-trap-aging-input-starvation/r2/results_r2.json`; day-block bootstrap 200):

| Quantity | Estimate [95% CI] |
| --- | --- |
| wakes / sustained escapes (consolidation-start traps dropped) | 745 / 212 |
| synthetic power for β_C = −0.25 | 0.23 |
| β_C, full model | -0.58 [-0.98, -0.04] |
| β_C, B + A + C | -0.62 [-0.98, -0.11] |
| ln k (wake index), full model | -0.97 [-1.43, -0.17] |
| ln s_dir (starvation), full model | -0.11 [-0.27, +0.15] |
| held-out gain over the base (nats per 1,000 wakes) | clocks +18.2 [-8.0, +46.0], starvation +3.1 [-0.6, +6.5], chatter +11.6 [+0.8, +20.8] |

