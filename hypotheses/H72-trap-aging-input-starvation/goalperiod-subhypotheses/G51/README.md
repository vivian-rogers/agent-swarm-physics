# H72 × G51: trap aging vs input starvation (2026-07-06 → 2026-09-04)

**Verdict:** failed
**Role:** replication
**Period:** regime III · 32 agents with gates · 45 non-holdout days · 25477 idle gates. No split: the hazard has agent fixed effects and day-block CIs.

## Why this period
Replication layer: the common two-clock hazard on every period with ≥ 200 idle gates (card, Design). Nothing period-specific is claimed here.

## Prediction
*Written 2026-10-04, before running on this period. Templated (card, "Per-period verdict rule", amended A1 before real data).*
If trap aging is input starvation, the aging slope β_a0 < 0 vanishes once s (time since the last novel read) is controlled, and β_s < 0. Expected here (card P4/P5): aging, where present, survives the control; in regime I, s barely varies.

## Result
Run 2026-10-04 with `analysis/run_period.py` (B = 200 day-block draws); numbers in `data/processed/H72-trap-aging-input-starvation/G51/results.json`. Logit, agent FE, sustained escape, a = a_sus, s = s_novel (min, ln).

| Quantity | Estimate [95% CI] |
| --- | --- |
| gates / sustained escapes | 22797 / 10627 (0.47) |
| median a, s (min) | 6.0, 3.9 |
| β_a0 (age only) | -0.48 [-0.54, -0.41] |
| β_a (age, s controlled) | -0.53 [-0.59, -0.44] |
| β_s (starvation, a controlled) | +0.23 [+0.11, +0.33] |
| ρ aging absorbed | -0.09 [-0.14, -0.05] |
| starvation-implied aging b_impl (O3b) | +0.03 [+0.01, +0.04] |
| CV gain, s adds / a adds (nats per 1,000 gates) | +1.3 / +14.9 |
| variant s_content: β_a, β_s | -0.52 [-0.58, -0.43], +0.23 [+0.12, +0.33] |
| variant s_dir: β_a, β_s | -0.50 [-0.54, -0.41], +0.09 [+0.06, +0.11] |
| variant s_peer: β_a, β_s | -0.52 [-0.58, -0.43], +0.23 [+0.12, +0.33] |
| any escape (a_any): β_a0, β_a, β_s | -0.79, -0.88 [-0.98, -0.74], +0.55 [+0.34, +0.68] |
| in-flight placebo (A2 window), Wald | +0.16 [+0.08, +0.25] |
| robustness β_a / β_s (cloglog; h ≥ 0.25; no first day) | cloglog: -0.37 / +0.15; trim_h025: -0.53 / +0.24; no_first_day: -0.52 / +0.23 |

Verdict: **failed**.

## Scorecard (period-specific axes)
- C: the two-clock model is scored on held-out days (5 day folds); a adds +14.9 nats per 1,000 gates, s adds +1.3.
- H: the starvation clock is the rival here; see the verdict.

