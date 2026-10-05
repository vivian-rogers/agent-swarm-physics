# H72 × G03: trap aging vs input starvation (2025-05-12 → 2025-05-14)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · 4 agents with gates · 3 non-holdout days · 304 idle gates. No split: the hazard has agent fixed effects and day-block CIs.

## Why this period
Replication layer: the common two-clock hazard on every period with ≥ 200 idle gates (card, Design). Nothing period-specific is claimed here.

## Prediction
*Written 2026-10-04, before running on this period. Templated (card, "Per-period verdict rule", amended A1 before real data).*
If trap aging is input starvation, the aging slope β_a0 < 0 vanishes once s (time since the last novel read) is controlled, and β_s < 0. Expected here (card P4/P5): aging, where present, survives the control; in regime I, s barely varies.

## Result
Run 2026-10-04 with `analysis/run_period.py` (B = 200 day-block draws); numbers in `data/processed/H72-trap-aging-input-starvation/G03/results.json`. Logit, agent FE, sustained escape, a = a_sus, s = s_novel (min, ln).

| Quantity | Estimate [95% CI] |
| --- | --- |
| gates / sustained escapes | 303 / 50 (0.17) |
| median a, s (min) | 3.4, 0.3 |
| β_a0 (age only) | +0.15 [-0.01, +2.97] |
| β_a (age, s controlled) | -0.13 [-1.48, +3.35] |
| β_s (starvation, a controlled) | +1.02 [-0.41, +2.38] |
| ρ aging absorbed | +1.89 [-642.26, +3.95] |
| starvation-implied aging b_impl (O3b) | +0.21 [+0.14, +0.98] |
| CV gain, s adds / a adds (nats per 1,000 gates) | +91.9 / -18.2 |
| variant s_content: β_a, β_s | -0.10 [-0.92, +1.58], +1.03 [+0.82, +1.58] |
| variant s_dir: β_a, β_s | +0.05 [-0.11, +34.74], +0.35 [-16.15, +1.00] |
| variant s_peer: β_a, β_s | -0.13 [-1.48, +2.15], +1.02 [+0.16, +2.38] |
| any escape (a_any): β_a0, β_a, β_s | +0.02, -0.12 [-1.35, +2.08], +0.33 [-0.97, +2.03] |
| in-flight placebo (A2 window), Wald | +0.50 [-0.50, +1.51] |
| robustness β_a / β_s (cloglog; h ≥ 0.25; no first day) | cloglog: -0.18 / +0.82; trim_h025: -0.20 / +0.83 |

Verdict: **descriptive (no aging to explain)**.

## Scorecard (period-specific axes)
- C: the two-clock model is scored on held-out days (5 day folds); a adds -18.2 nats per 1,000 gates, s adds +91.9.
- H: the starvation clock is the rival here; see the verdict.

## Round 2 (2026-10-05): chatter hold

**Round-2 verdict (chatter hold, R1):** failed (β_C above 0)

*Prediction (written 2026-10-05 before running; card "Round 2", R1 and amendments R2-A1/A2):* escape at a wake falls with ln(1 + undirected items read at the 5 calls before it), β_C < 0, in the full model (agent FE + base + ln a + ln k + ln s_dir + dose). Only G51 is powered (synthetic); elsewhere a CI including 0 is descriptive.

*Result* (`analysis/run_r2.py`; `data/processed/H72-trap-aging-input-starvation/r2/results_r2.json`; day-block bootstrap 200):

| Quantity | Estimate [95% CI] |
| --- | --- |
| wakes / sustained escapes (consolidation-start traps dropped) | 303 / 50 |
| synthetic power for β_C = −0.25 | 0.00 |
| β_C, full model | +1.25 [+1.12, +29.45] |
| β_C, B + A + C | +1.25 [-0.69, +10.10] |
| ln k (wake index), full model | -1.81 [-10.72, +14.53] |
| ln s_dir (starvation), full model | -0.01 [-27.40, +0.68] |
| held-out gain over the base (nats per 1,000 wakes) | clocks +1.8 [-119.4, +116.3], starvation +7.6 [-6.3, +21.5], chatter +17.0 [-17.2, +57.9] |

