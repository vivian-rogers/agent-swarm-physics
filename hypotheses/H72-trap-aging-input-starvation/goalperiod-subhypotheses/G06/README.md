# H72 × G06: trap aging vs input starvation (2025-06-26 → 2025-07-15)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · 4 agents with gates · 15 non-holdout days · 232 idle gates. No split: the hazard has agent fixed effects and day-block CIs.

## Why this period
Replication layer: the common two-clock hazard on every period with ≥ 200 idle gates (card, Design). Nothing period-specific is claimed here.

## Prediction
*Written 2026-10-04, before running on this period. Templated (card, "Per-period verdict rule", amended A1 before real data).*
If trap aging is input starvation, the aging slope β_a0 < 0 vanishes once s (time since the last novel read) is controlled, and β_s < 0. Expected here (card P4/P5): aging, where present, survives the control; in regime I, s barely varies.

## Result
Run 2026-10-04 with `analysis/run_period.py` (B = 200 day-block draws); numbers in `data/processed/H72-trap-aging-input-starvation/G06/results.json`. Logit, agent FE, sustained escape, a = a_sus, s = s_novel (min, ln).

| Quantity | Estimate [95% CI] |
| --- | --- |
| gates / sustained escapes | 228 / 68 (0.30) |
| median a, s (min) | 2.7, 1.0 |
| β_a0 (age only) | +0.38 [+0.18, +1.09] |
| β_a (age, s controlled) | +0.44 [+0.29, +1.12] |
| β_s (starvation, a controlled) | -0.23 [-0.83, +0.15] |
| ρ aging absorbed | -0.17 [-0.78, +0.07] |
| starvation-implied aging b_impl (O3b) | -0.06 [-0.17, +0.08] |
| CV gain, s adds / a adds (nats per 1,000 gates) | -17.1 / -136.2 |
| variant s_content: β_a, β_s | +0.41 [+0.22, +1.32], -0.14 [-0.47, +0.12] |
| variant s_dir: β_a, β_s | +0.40 [+0.21, +1.25], +0.04 [-0.43, +0.40] |
| variant s_peer: β_a, β_s | +0.44 [+0.25, +1.28], -0.23 [-0.81, +0.24] |
| any escape (a_any): β_a0, β_a, β_s | +0.06, +0.00 [-0.08, +1.41], +0.18 [-0.26, +0.84] |
| in-flight placebo (A2 window), Wald | +0.36 [-0.57, +1.29] |
| robustness β_a / β_s (cloglog; h ≥ 0.25; no first day) | cloglog: +0.39 / -0.20; trim_h025: +0.40 / -0.22; no_first_day: +0.46 / -0.22 |

Verdict: **descriptive (no aging to explain)**.

## Scorecard (period-specific axes)
- C: the two-clock model is scored on held-out days (5 day folds); a adds -136.2 nats per 1,000 gates, s adds -17.1.
- H: the starvation clock is the rival here; see the verdict.

