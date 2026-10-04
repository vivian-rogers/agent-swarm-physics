# H72 × G40: trap aging vs input starvation (2026-05-04 → 2026-05-08)

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · 11 agents with gates · 5 non-holdout days · 205 idle gates. No split: the hazard has agent fixed effects and day-block CIs.

## Why this period
Replication layer: the common two-clock hazard on every period with ≥ 200 idle gates (card, Design). Nothing period-specific is claimed here.

## Prediction
*Written 2026-10-04, before running on this period. Templated (card, "Per-period verdict rule", amended A1 before real data).*
If trap aging is input starvation, the aging slope β_a0 < 0 vanishes once s (time since the last novel read) is controlled, and β_s < 0. Expected here (card P4/P5): aging, where present, survives the control; in regime I, s barely varies.

## Result
Run 2026-10-04 with `analysis/run_period.py` (B = 200 day-block draws); numbers in `data/processed/H72-trap-aging-input-starvation/G40/results.json`. Logit, agent FE, sustained escape, a = a_sus, s = s_novel (min, ln).

| Quantity | Estimate [95% CI] |
| --- | --- |
| gates / sustained escapes | 204 / 171 (0.84) |
| median a, s (min) | 0.7, 1.3 |
| β_a0 (age only) | +1.14 [-0.35, +6.19] |
| β_a (age, s controlled) | +1.07 [-0.33, +8.20] |
| β_s (starvation, a controlled) | +0.21 [-1.45, +0.57] |
| ρ aging absorbed | +0.06 [-0.24, +1.97] |
| starvation-implied aging b_impl (O3b) | +0.06 [-0.69, +0.10] |
| CV gain, s adds / a adds (nats per 1,000 gates) | -14.5 / -18.7 |
| variant s_content: β_a, β_s | +1.02 [-0.39, +7.33], +0.37 [-0.65, +0.80] |
| variant s_dir: β_a, β_s | +1.08 [-0.49, +4.92], -0.00 [-0.84, +0.41] |
| variant s_peer: β_a, β_s | +1.05 [-0.35, +7.44], +0.36 [-0.96, +0.71] |
| in-flight placebo (A2 window), Wald | +0.44 [-0.91, +1.79] |
| robustness β_a / β_s (cloglog; h ≥ 0.25; no first day) | cloglog: +0.27 / +0.23; trim_h025: +0.83 / +0.30; no_first_day: +0.02 / +0.27 |

Verdict: **descriptive (no aging to explain)**.

## Scorecard (period-specific axes)
- C: the two-clock model is scored on held-out days (5 day folds); a adds -18.7 nats per 1,000 gates, s adds -14.5.
- H: the starvation clock is the rival here; see the verdict.

