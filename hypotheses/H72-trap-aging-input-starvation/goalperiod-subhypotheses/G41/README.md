# H72 × G41: trap aging vs input starvation (2026-05-11 → 2026-05-15)

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · 14 agents with gates · 5 non-holdout days · 316 idle gates. No split: the hazard has agent fixed effects and day-block CIs.

## Why this period
Replication layer: the common two-clock hazard on every period with ≥ 200 idle gates (card, Design). Nothing period-specific is claimed here.

## Prediction
*Written 2026-10-04, before running on this period. Templated (card, "Per-period verdict rule", amended A1 before real data).*
If trap aging is input starvation, the aging slope β_a0 < 0 vanishes once s (time since the last novel read) is controlled, and β_s < 0. Expected here (card P4/P5): aging, where present, survives the control; in regime I, s barely varies.

## Result
Run 2026-10-04 with `analysis/run_period.py` (B = 200 day-block draws); numbers in `data/processed/H72-trap-aging-input-starvation/G41/results.json`. Logit, agent FE, sustained escape, a = a_sus, s = s_novel (min, ln).

| Quantity | Estimate [95% CI] |
| --- | --- |
| gates / sustained escapes | 299 / 158 (0.53) |
| median a, s (min) | 4.3, 3.3 |
| β_a0 (age only) | -0.18 [-0.19, +0.77] |
| β_a (age, s controlled) | -0.21 [-0.22, +0.79] |
| β_s (starvation, a controlled) | +0.11 [-0.39, +0.60] |
| ρ aging absorbed | -0.16 [-1.61, +1.91] |
| starvation-implied aging b_impl (O3b) | +0.03 [-0.12, +0.13] |
| CV gain, s adds / a adds (nats per 1,000 gates) | +0.2 / +7.2 |
| variant s_content: β_a, β_s | -0.17 [-0.20, +0.66], -0.04 [-0.60, +0.24] |
| variant s_dir: β_a, β_s | -0.20 [-0.34, +0.84], +0.02 [-0.30, +0.49] |
| variant s_peer: β_a, β_s | -0.20 [-0.21, +0.57], +0.09 [-0.39, +0.43] |
| in-flight placebo (A2 window), Wald | +0.23 [-0.76, +1.21] |
| robustness β_a / β_s (cloglog; h ≥ 0.25; no first day) | cloglog: -0.18 / +0.11; trim_h025: -0.20 / -0.00; no_first_day: -0.03 / +0.09 |

Verdict: **descriptive (no aging to explain)**.

## Scorecard (period-specific axes)
- C: the two-clock model is scored on held-out days (5 day folds); a adds +7.2 nats per 1,000 gates, s adds +0.2.
- H: the starvation clock is the rival here; see the verdict.

## Round 2 (2026-10-05): chatter hold

**Round-2 verdict (chatter hold, R1):** descriptive (CI includes 0; power 0.12 at −0.25)

*Prediction (written 2026-10-05 before running; card "Round 2", R1 and amendments R2-A1/A2):* escape at a wake falls with ln(1 + undirected items read at the 5 calls before it), β_C < 0, in the full model (agent FE + base + ln a + ln k + ln s_dir + dose + ln(1 − f_call)). Only G51 is powered (synthetic); elsewhere a CI including 0 is descriptive.

*Result* (`analysis/run_r2.py`; `data/processed/H72-trap-aging-input-starvation/r2/results_r2.json`; day-block bootstrap 200):

| Quantity | Estimate [95% CI] |
| --- | --- |
| wakes / sustained escapes (consolidation-start traps dropped) | 296 / 155 |
| synthetic power for β_C = −0.25 | 0.12 |
| β_C, full model | -0.39 [-1.92, +0.82] |
| β_C, B + A + C | -0.39 [-1.40, +0.64] |
| ln k (wake index), full model | +0.11 [-1.20, +2.08] |
| ln s_dir (starvation), full model | -0.12 [-0.50, +0.35] |
| ln(1 − f_call) (urn coefficient), full model | +1.56 [-0.12, +4.33] |
| held-out gain over the base (nats per 1,000 wakes) | clocks +0.1 [-3.3, +3.0], starvation -13.4 [-21.7, -6.8], chatter +4.2 [-13.6, +16.5], self-share +10.9 [-11.5, +26.8] |
| transfer of G51 slopes (held-out gain, nats per 1,000 wakes) | starvation -2.1 [-4.3, -0.2], chatter +18.3 [+0.9, +40.4], self-share +16.2 [-4.3, +34.0] |

