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

