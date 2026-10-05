# H72 × G04: trap aging vs input starvation (2025-05-15 → 2025-06-18)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · 6 agents with gates · 25 non-holdout days · 725 idle gates. No split: the hazard has agent fixed effects and day-block CIs.

## Why this period
Replication layer: the common two-clock hazard on every period with ≥ 200 idle gates (card, Design). Nothing period-specific is claimed here.

## Prediction
*Written 2026-10-04, before running on this period. Templated (card, "Per-period verdict rule", amended A1 before real data).*
If trap aging is input starvation, the aging slope β_a0 < 0 vanishes once s (time since the last novel read) is controlled, and β_s < 0. Expected here (card P4/P5): aging, where present, survives the control; in regime I, s barely varies.

## Result
Run 2026-10-04 with `analysis/run_period.py` (B = 200 day-block draws); numbers in `data/processed/H72-trap-aging-input-starvation/G04/results.json`. Logit, agent FE, sustained escape, a = a_sus, s = s_novel (min, ln).

| Quantity | Estimate [95% CI] |
| --- | --- |
| gates / sustained escapes | 716 / 275 (0.38) |
| median a, s (min) | 2.7, 0.7 |
| β_a0 (age only) | +0.20 [-0.00, +0.50] |
| β_a (age, s controlled) | +0.01 [-0.22, +0.35] |
| β_s (starvation, a controlled) | +0.35 [-0.03, +0.55] |
| ρ aging absorbed | +0.96 [-1.75, +4.22] |
| starvation-implied aging b_impl (O3b) | +0.19 [-0.01, +0.30] |
| CV gain, s adds / a adds (nats per 1,000 gates) | +7.3 / -2.6 |
| variant s_content: β_a, β_s | +0.09 [-0.12, +0.46], +0.22 [-0.04, +0.44] |
| variant s_dir: β_a, β_s | +0.17 [-0.02, +0.44], +0.13 [-0.05, +0.35] |
| variant s_peer: β_a, β_s | +0.01 [-0.17, +0.38], +0.35 [+0.03, +0.60] |
| any escape (a_any): β_a0, β_a, β_s | +0.07, -0.17 [-0.34, +0.43], +0.38 [+0.12, +0.58] |
| in-flight placebo (A2 window), Wald | +0.39 [-0.01, +0.80] |
| robustness β_a / β_s (cloglog; h ≥ 0.25; no first day) | cloglog: -0.03 / +0.24; trim_h025: +0.03 / +0.32; no_first_day: +0.00 / +0.34 |

Verdict: **descriptive (no aging to explain)**.

## Scorecard (period-specific axes)
- C: the two-clock model is scored on held-out days (5 day folds); a adds -2.6 nats per 1,000 gates, s adds +7.3.
- H: the starvation clock is the rival here; see the verdict.

## Round 2 (2026-10-05): chatter hold

**Round-2 verdict (chatter hold, R1):** descriptive (CI includes 0; power 0.28 at −0.25)

*Prediction (written 2026-10-05 before running; card "Round 2", R1 and amendments R2-A1/A2):* escape at a wake falls with ln(1 + undirected items read at the 5 calls before it), β_C < 0, in the full model (agent FE + base + ln a + ln k + ln s_dir + dose). Only G51 is powered (synthetic); elsewhere a CI including 0 is descriptive.

*Result* (`analysis/run_r2.py`; `data/processed/H72-trap-aging-input-starvation/r2/results_r2.json`; day-block bootstrap 200):

| Quantity | Estimate [95% CI] |
| --- | --- |
| wakes / sustained escapes (consolidation-start traps dropped) | 866 / 307 |
| synthetic power for β_C = −0.25 | 0.28 |
| β_C, full model | -0.26 [-0.62, +0.13] |
| β_C, B + A + C | -0.23 [-0.64, +0.21] |
| ln k (wake index), full model | -0.65 [-0.95, -0.21] |
| ln s_dir (starvation), full model | +0.10 [-0.12, +0.37] |
| held-out gain over the base (nats per 1,000 wakes) | clocks +8.2 [-9.4, +24.1], starvation -13.8 [-42.0, +8.2], chatter +1.3 [-2.9, +6.5] |

