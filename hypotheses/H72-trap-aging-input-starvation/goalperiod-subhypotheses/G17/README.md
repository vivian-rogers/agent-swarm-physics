# H72 × G17: trap aging vs input starvation (2025-10-13 → 2025-10-17)

**Verdict:** failed
**Role:** replication
**Period:** regime I · 6 agents with gates · 5 non-holdout days · 1009 idle gates. No split: the hazard has agent fixed effects and day-block CIs.

## Why this period
Replication layer: the common two-clock hazard on every period with ≥ 200 idle gates (card, Design). Nothing period-specific is claimed here.

## Prediction
*Written 2026-10-04, before running on this period. Templated (card, "Per-period verdict rule", amended A1 before real data).*
If trap aging is input starvation, the aging slope β_a0 < 0 vanishes once s (time since the last novel read) is controlled, and β_s < 0. Expected here (card P4/P5): aging, where present, survives the control; in regime I, s barely varies.

## Result
Run 2026-10-04 with `analysis/run_period.py` (B = 200 day-block draws); numbers in `data/processed/H72-trap-aging-input-starvation/G17/results.json`. Logit, agent FE, sustained escape, a = a_sus, s = s_novel (min, ln).

| Quantity | Estimate [95% CI] |
| --- | --- |
| gates / sustained escapes | 1000 / 117 (0.12) |
| median a, s (min) | 14.8, 0.7 |
| β_a0 (age only) | -0.53 [-0.74, -0.17] |
| β_a (age, s controlled) | -0.59 [-0.78, -0.21] |
| β_s (starvation, a controlled) | +0.25 [-0.16, +0.42] |
| ρ aging absorbed | -0.12 [-0.46, +0.28] |
| starvation-implied aging b_impl (O3b) | +0.04 [-0.02, +0.09] |
| CV gain, s adds / a adds (nats per 1,000 gates) | +1.4 / +21.2 |
| variant s_content: β_a, β_s | -0.56 [-0.80, -0.29], +0.14 [-0.08, +0.30] |
| variant s_dir: β_a, β_s | -0.54 [-0.75, -0.22], +0.03 [-0.06, +0.15] |
| variant s_peer: β_a, β_s | -0.59 [-0.84, -0.31], +0.25 [+0.01, +0.42] |
| any escape (a_any): β_a0, β_a, β_s | -0.24, -0.42 [-0.52, -0.16], +0.51 [+0.24, +0.76] |
| in-flight placebo (A2 window), Wald | +0.11 [-0.42, +0.65] |
| robustness β_a / β_s (cloglog; h ≥ 0.25; no first day) | cloglog: -0.52 / +0.24; trim_h025: -0.61 / +0.27; no_first_day: -0.60 / +0.30 |

Verdict: **failed**.

## Scorecard (period-specific axes)
- C: the two-clock model is scored on held-out days (5 day folds); a adds +21.2 nats per 1,000 gates, s adds +1.4.
- H: the starvation clock is the rival here; see the verdict.

## Round 2 (2026-10-05): chatter hold

**Round-2 verdict (chatter hold, R1):** failed (β_C above 0)

*Prediction (written 2026-10-05 before running; card "Round 2", R1 and amendments R2-A1/A2):* escape at a wake falls with ln(1 + undirected items read at the 5 calls before it), β_C < 0, in the full model (agent FE + base + ln a + ln k + ln s_dir + dose). Only G51 is powered (synthetic); elsewhere a CI including 0 is descriptive.

*Result* (`analysis/run_r2.py`; `data/processed/H72-trap-aging-input-starvation/r2/results_r2.json`; day-block bootstrap 200):

| Quantity | Estimate [95% CI] |
| --- | --- |
| wakes / sustained escapes (consolidation-start traps dropped) | 960 / 107 |
| synthetic power for β_C = −0.25 | 0.12 |
| β_C, full model | +0.29 [+0.01, +0.75] |
| β_C, B + A + C | +0.26 [+0.02, +0.72] |
| ln k (wake index), full model | -0.59 [-1.10, -0.11] |
| ln s_dir (starvation), full model | -0.04 [-0.15, +0.22] |
| held-out gain over the base (nats per 1,000 wakes) | clocks +25.2 [-2.9, +54.1], starvation -19.0 [-53.9, +0.8], chatter -2.1 [-6.2, +0.6] |

