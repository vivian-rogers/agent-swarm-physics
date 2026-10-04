# H72 × G37: trap aging vs input starvation (2026-03-30 → 2026-04-01)

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · 8 agents with gates · 3 non-holdout days · 250 idle gates. No split: the hazard has agent fixed effects and day-block CIs.

## Why this period
Replication layer: the common two-clock hazard on every period with ≥ 200 idle gates (card, Design). Nothing period-specific is claimed here.

## Prediction
*Written 2026-10-04, before running on this period. Templated (card, "Per-period verdict rule", amended A1 before real data).*
If trap aging is input starvation, the aging slope β_a0 < 0 vanishes once s (time since the last novel read) is controlled, and β_s < 0. Expected here (card P4/P5): aging, where present, survives the control; in regime I, s barely varies.

## Result
Run 2026-10-04 with `analysis/run_period.py` (B = 200 day-block draws); numbers in `data/processed/H72-trap-aging-input-starvation/G37/results.json`. Logit, agent FE, sustained escape, a = a_sus, s = s_novel (min, ln).

| Quantity | Estimate [95% CI] |
| --- | --- |
| gates / sustained escapes | 240 / 163 (0.68) |
| median a, s (min) | 4.4, 10.1 |
| β_a0 (age only) | -0.28 [-0.52, +6.56] |
| β_a (age, s controlled) | -0.23 [-0.23, +9.69] |
| β_s (starvation, a controlled) | -0.09 [-2.34, +0.35] |
| ρ aging absorbed | +0.19 [-0.48, +0.88] |
| starvation-implied aging b_impl (O3b) | -0.05 [-0.94, +0.22] |
| CV gain, s adds / a adds (nats per 1,000 gates) | -30.8 / -5.8 |
| variant s_content: β_a, β_s | -0.23 [-0.23, +0.96], -0.08 [-0.95, +0.57] |
| variant s_dir: β_a, β_s | -0.23 [-0.49, +1.08], -0.04 [-0.21, +0.38] |
| variant s_peer: β_a, β_s | -0.23 [-0.23, +0.96], -0.09 [-0.95, +0.53] |
| in-flight placebo (A2 window), Wald | +0.72 [-1.63, +3.06] |
| robustness β_a / β_s (cloglog; h ≥ 0.25; no first day) | cloglog: -0.23 / -0.02; trim_h025: -0.22 / -0.08; no_first_day: +0.19 / +0.25 |

Verdict: **descriptive (no aging to explain)**.

## Scorecard (period-specific axes)
- C: the two-clock model is scored on held-out days (5 day folds); a adds -5.8 nats per 1,000 gates, s adds -30.8.
- H: the starvation clock is the rival here; see the verdict.

