# H08 × NE41: forced context erasure at the 41-turn consolidation cap (regime III, #36 from 03-24 → #51)

**Verdict:** mixed
**Role:** exploratory
**Period:** spans #36 (from 2026-03-24), #37–#42, #44, #51 (non-holdout days only). Natural experiment NE41 (found by H15).

## Why this test
H15 found that a forced context erasure (memory kept) cuts write output 33–53% for ~10 turns. If context is the
coupling, the same erasure should cut the coupling to whatever was only in the context: messages read before it.

## Prediction
*Written 2026-10-04 (~02:40 UTC), before running C3 on any period.*

NE41 is the forced consolidation at the 41-turn cap (regime III): the context window is erased and memory kept, at a time
set by the scaffold, not the agent. Each erasure is a transition object (exception (c)); per-period estimates (G cards)
are combined by DerSimonian–Laird random effects.
- **E1:** pooled β_F < 0 with the 95% CI excluding 0 and a relative drop ≥ 30% of the in-context rate at the same age:
  an old sender read before a forced erasure is addressed less than an old sender read after it, in the same
  post-consolidation talk turns.
- **E2:** pooled β_V within ±50% of β_F.
- **E3:** voluntary segments are shorter when inflow per turn is higher (ρ < 0 in ≥ 2/3 of periods).
- **Rivals:** memory-mediated coupling (β_F ≈ 0: what matters is written to memory and read back); restart overhead only
  (absorbed by PC(τ) and the new-sender contrast).

**Verdict rule (fixed now):** supported if E1 holds; failed if the pooled β_F CI includes 0 or is positive; mixed if E1
holds in sign but the relative drop is < 30%.

## Result
*Run 2026-10-04 (`analysis/erasure.py`). Linear probability model with agent×day effects, 5 age bins, engaged flag, post-consolidation turn and new-sender indicators; day-bootstrap CIs; random-effects pooling.*

| Period | forced-erased units | β_F (pp) | relative | β_V (pp) | ρ E3 |
| --- | --- | --- | --- | --- | --- |
| G36 | 759 | -2.95 [-6.46, +0.03] | -0.12 [-0.26, 0.00] | -2.93 [-7.53, +1.68] | +0.36 |
| G37 | 357 | -10.86 [-13.65, -3.78] | -0.38 [-0.48, -0.13] | -7.27 [-9.81, -3.82] | +0.14 |
| G38 | 3028 | -0.98 [-2.39, +1.22] | -0.07 [-0.16, 0.08] | +3.33 [+1.44, +5.43] | +0.02 |
| G39 | 1399 | -2.22 [-9.76, -0.11] | -0.31 [-1.35, -0.02] | +0.14 [-7.47, +6.11] | -0.10 |
| G40 | 3182 | -1.04 [-2.09, -0.02] | -0.10 [-0.21, -0.00] | -2.28 [-3.17, -1.14] | -0.34 |
| G41 | 1825 | -1.27 [-4.60, +2.25] | -0.07 [-0.26, 0.13] | -1.21 [-4.65, +2.17] | +0.06 |
| G42 | 1216 | -4.45 [-8.12, -1.63] | -0.22 [-0.41, -0.08] | -1.79 [-5.05, +0.18] | -0.08 |
| G44 | 1087 | -4.92 [-7.12, -2.38] | -0.23 [-0.33, -0.11] | -6.61 [-9.85, -3.04] | -0.10 |
| G51 | 62966 | -1.74 [-2.00, -1.50] | -0.21 [-0.25, -0.18] | -1.94 [-2.26, -1.62] | -0.11 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| E1 pooled β_F < 0, relative drop ≥ 30% | β_F = -2.53 pp [-3.65, -1.42] (k = 9, I² = 0.69); relative -18% ± 6%; CI excludes 0 in 6/9 periods | sign only |
| E2 β_V within ±50% of β_F | β_V = -2.18 ± 1.51 pp | pass |
| E3 ρ < 0 in ≥ 2/3 of periods | 5/9 | fail |

**Verdict: mixed** (rule fixed in Prediction). Figure: `figures/ne41.pdf`.

## Scorecard (test-specific axes)
| Axis | |
| --- | --- |
| E interventional | forced erasures at the scaffold's 41-turn cap: exogenous timing; pooled β_F -2.53 pp |
| H comparative | memory-mediated coupling (β_F ≈ 0) rejected; restart overhead absorbed by PC and the new-sender contrast |

## Notes
- Card: [`../../README.md`](../../README.md). Data: `data/processed/H08-context-is-the-coupling/ne41_pooled.json`, `G<NN>/c3.json`.
- Forced / voluntary labels come from H15's catalog (`data/processed/H15-semantic-information-scrambles/consolidations.parquet`).
