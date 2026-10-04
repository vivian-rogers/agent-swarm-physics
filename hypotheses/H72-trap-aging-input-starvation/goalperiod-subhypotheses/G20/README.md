# H72 × G20: trap aging vs input starvation (2025-11-17 → 2025-11-28)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · 9 agents with gates · 10 non-holdout days · 516 idle gates. No split: the hazard has agent fixed effects and day-block CIs.

## Why this period
Replication layer: the common two-clock hazard on every period with ≥ 200 idle gates (card, Design). Nothing period-specific is claimed here.

## Prediction
*Written 2026-10-04, before running on this period. Templated (card, "Per-period verdict rule", amended A1 before real data).*
If trap aging is input starvation, the aging slope β_a0 < 0 vanishes once s (time since the last novel read) is controlled, and β_s < 0. Expected here (card P4/P5): aging, where present, survives the control; in regime I, s barely varies.

## Result
Run 2026-10-04 with `analysis/run_period.py` (B = 200 day-block draws); numbers in `data/processed/H72-trap-aging-input-starvation/G20/results.json`. Logit, agent FE, sustained escape, a = a_sus, s = s_novel (min, ln).

| Quantity | Estimate [95% CI] |
| --- | --- |
| gates / sustained escapes | 505 / 153 (0.30) |
| median a, s (min) | 4.8, 1.1 |
| β_a0 (age only) | +0.12 [-0.17, +1.01] |
| β_a (age, s controlled) | -0.08 [-0.43, +0.87] |
| β_s (starvation, a controlled) | +0.95 [+0.63, +1.72] |
| ρ aging absorbed | +1.64 [-6.34, +9.93] |
| starvation-implied aging b_impl (O3b) | +0.17 [+0.08, +0.46] |
| CV gain, s adds / a adds (nats per 1,000 gates) | +15.4 / -5.2 |
| variant s_content: β_a, β_s | -0.05 [-0.21, +0.70], +0.99 [+0.53, +1.91] |
| variant s_dir: β_a, β_s | +0.08 [-0.15, +0.81], +0.22 [-0.07, +0.83] |
| variant s_peer: β_a, β_s | -0.08 [-0.26, +0.70], +0.95 [+0.68, +1.50] |
| any escape (a_any): β_a0, β_a, β_s | +0.06, -0.11 [-0.43, +0.25], +0.78 [+0.37, +1.69] |
| in-flight placebo (A2 window), Wald | +0.19 [-0.34, +0.72] |
| robustness β_a / β_s (cloglog; h ≥ 0.25; no first day) | cloglog: -0.11 / +0.70; trim_h025: -0.07 / +0.95; no_first_day: -0.07 / +0.94 |

Verdict: **descriptive (no aging to explain)**.

## Scorecard (period-specific axes)
- C: the two-clock model is scored on held-out days (5 day folds); a adds -5.2 nats per 1,000 gates, s adds +15.4.
- H: the starvation clock is the rival here; see the verdict.

