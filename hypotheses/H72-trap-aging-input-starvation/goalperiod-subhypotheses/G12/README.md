# H72 × G12: trap aging vs input starvation (2025-09-01 → 2025-09-05)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · 7 agents with gates · 5 non-holdout days · 557 idle gates. No split: the hazard has agent fixed effects and day-block CIs.

## Why this period
Replication layer: the common two-clock hazard on every period with ≥ 200 idle gates (card, Design). Nothing period-specific is claimed here.

## Prediction
*Written 2026-10-04, before running on this period. Templated (card, "Per-period verdict rule", amended A1 before real data).*
If trap aging is input starvation, the aging slope β_a0 < 0 vanishes once s (time since the last novel read) is controlled, and β_s < 0. Expected here (card P4/P5): aging, where present, survives the control; in regime I, s barely varies.

## Result
Run 2026-10-04 with `analysis/run_period.py` (B = 200 day-block draws); numbers in `data/processed/H72-trap-aging-input-starvation/G12/results.json`. Logit, agent FE, sustained escape, a = a_sus, s = s_novel (min, ln).

| Quantity | Estimate [95% CI] |
| --- | --- |
| gates / sustained escapes | 552 / 156 (0.28) |
| median a, s (min) | 3.0, 0.4 |
| β_a0 (age only) | +0.01 [-0.18, +0.49] |
| β_a (age, s controlled) | -0.07 [-0.21, +0.36] |
| β_s (starvation, a controlled) | +0.33 [+0.07, +0.62] |
| ρ aging absorbed | +9.87 [-2.33, +9.87] |
| starvation-implied aging b_impl (O3b) | +0.07 [+0.02, +0.13] |
| CV gain, s adds / a adds (nats per 1,000 gates) | +1.2 / -1.4 |
| variant s_content: β_a, β_s | -0.05 [-0.21, +0.41], +0.28 [-0.00, +0.52] |
| variant s_dir: β_a, β_s | -0.00 [-0.20, +0.46], +0.04 [-0.14, +0.19] |
| variant s_peer: β_a, β_s | -0.07 [-0.21, +0.35], +0.33 [+0.07, +0.62] |
| any escape (a_any): β_a0, β_a, β_s | +0.14, +0.07 [-0.02, +0.28], +0.20 [-0.25, +0.65] |
| in-flight placebo (A2 window), Wald | +0.41 [-0.07, +0.90] |
| robustness β_a / β_s (cloglog; h ≥ 0.25; no first day) | cloglog: -0.04 / +0.24; trim_h025: -0.00 / +0.32; no_first_day: +0.05 / +0.34 |

Verdict: **descriptive (no aging to explain)**.

## Scorecard (period-specific axes)
- C: the two-clock model is scored on held-out days (5 day folds); a adds -1.4 nats per 1,000 gates, s adds +1.2.
- H: the starvation clock is the rival here; see the verdict.

