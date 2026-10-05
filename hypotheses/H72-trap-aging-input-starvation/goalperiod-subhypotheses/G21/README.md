# H72 × G21: trap aging vs input starvation (2025-12-01 → 2025-12-05)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · 8 agents with gates · 5 non-holdout days · 604 idle gates. No split: the hazard has agent fixed effects and day-block CIs.

## Why this period
Replication layer: the common two-clock hazard on every period with ≥ 200 idle gates (card, Design). Nothing period-specific is claimed here.

## Prediction
*Written 2026-10-04, before running on this period. Templated (card, "Per-period verdict rule", amended A1 before real data).*
If trap aging is input starvation, the aging slope β_a0 < 0 vanishes once s (time since the last novel read) is controlled, and β_s < 0. Expected here (card P4/P5): aging, where present, survives the control; in regime I, s barely varies.

## Result
Run 2026-10-04 with `analysis/run_period.py` (B = 200 day-block draws); numbers in `data/processed/H72-trap-aging-input-starvation/G21/results.json`. Logit, agent FE, sustained escape, a = a_sus, s = s_novel (min, ln).

| Quantity | Estimate [95% CI] |
| --- | --- |
| gates / sustained escapes | 603 / 109 (0.18) |
| median a, s (min) | 15.5, 1.3 |
| β_a0 (age only) | -0.62 [-0.87, +0.17] |
| β_a (age, s controlled) | -0.65 [-1.01, +0.10] |
| β_s (starvation, a controlled) | +0.29 [-0.17, +1.68] |
| ρ aging absorbed | -0.05 [-0.29, +0.84] |
| starvation-implied aging b_impl (O3b) | +0.01 [-0.01, +0.08] |
| CV gain, s adds / a adds (nats per 1,000 gates) | -26.1 / +96.0 |
| variant s_content: β_a, β_s | -0.64 [-1.01, +0.36], +0.18 [-0.39, +0.79] |
| variant s_dir: β_a, β_s | -0.60 [-0.91, +0.39], -0.05 [-0.41, +0.20] |
| variant s_peer: β_a, β_s | -0.65 [-0.96, +0.23], +0.29 [-0.16, +1.32] |
| any escape (a_any): β_a0, β_a, β_s | -0.84, -0.90 [-0.97, +0.03], +0.55 [+0.15, +1.47] |
| in-flight placebo (A2 window), Wald | -0.33 [-0.96, +0.30] |
| robustness β_a / β_s (cloglog; h ≥ 0.25; no first day) | cloglog: -0.59 / +0.21; trim_h025: -0.65 / +0.29; no_first_day: -0.64 / +0.30 |

Verdict: **descriptive (no aging to explain)**.

## Scorecard (period-specific axes)
- C: the two-clock model is scored on held-out days (5 day folds); a adds +96.0 nats per 1,000 gates, s adds -26.1.
- H: the starvation clock is the rival here; see the verdict.

## Round 2 (2026-10-05): chatter hold

**Round-2 verdict (chatter hold, R1):** descriptive (CI includes 0; power 0.12 at −0.25)

*Prediction (written 2026-10-05 before running; card "Round 2", R1 and amendments R2-A1/A2):* escape at a wake falls with ln(1 + undirected items read at the 5 calls before it), β_C < 0, in the full model (agent FE + base + ln a + ln k + ln s_dir + dose). Only G51 is powered (synthetic); elsewhere a CI including 0 is descriptive.

*Result* (`analysis/run_r2.py`; `data/processed/H72-trap-aging-input-starvation/r2/results_r2.json`; day-block bootstrap 200):

| Quantity | Estimate [95% CI] |
| --- | --- |
| wakes / sustained escapes (consolidation-start traps dropped) | 520 / 99 |
| synthetic power for β_C = −0.25 | 0.12 |
| β_C, full model | +0.58 [-0.01, +1.47] |
| β_C, B + A + C | +0.58 [+0.04, +1.30] |
| ln k (wake index), full model | -1.27 [-2.80, +0.22] |
| ln s_dir (starvation), full model | -0.01 [-0.48, +0.36] |
| held-out gain over the base (nats per 1,000 wakes) | clocks +72.2 [+20.8, +152.4], starvation -26.4 [-93.2, +14.4], chatter +3.5 [-15.2, +26.3] |

