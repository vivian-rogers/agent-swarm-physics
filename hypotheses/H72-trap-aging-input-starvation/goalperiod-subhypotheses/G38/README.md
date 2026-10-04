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

