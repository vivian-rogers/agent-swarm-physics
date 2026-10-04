# H90 × G51: Private assigned goals, head (51a–51l) (2026-07-06 → 09-04)

**Verdict:** supported (native N2 in this folder: failed)
**Role:** replication + native (exploratory)
**Period:** regime III · 32 agents over the period (mean 26.5 day-present) · 43 trimmed talk days (17586 trimmed minutes), 34 behavior days (2415 trimmed 5-min steps) · 40774 agent messages naming a peer, 746 named ordered pairs.

## Why this period
- 45 non-holdout days, N 21 → 32, one room most of the time: the only unit at the synthetic S51 size. Hosts native N2 (full pairwise talk).

## Prediction
*Written 2026-10-04 ~20:15 UTC (card), with amendments A1 (synthetic, before real data) and A2/A3 (dated on the card), before running on this period.*
- P1: ρ_coll < 0.1 in behavior and activity where Σ̂₁₊all's CI excludes 0.
- P2 (read after A1 as lead–lag): σ_coll(talk) over the block-shift null.
- P3 (after A1 the coupling test): Δ_addr(talk) = σ_nam − σ_un > 0 against the shift null.
- Synthetic size class: S51 (N 27 × 33 days); Δ_addr power at J = 1 is 1.00, at G51's effect size (J ≈ 0.28) 1.00 (A3, post hoc).

## Result
*Run 2026-10-04 ~21:45 UTC (`analysis/run.py`; data `data/processed/H90-collective-entropy-production/G51/results.json`; figure `../../figures/summary_obs.pdf`).* Units: 10⁻³ nats per system step (1 min for talk/activity, 5 min for behavior); 95% day-bootstrap CIs; p against 100 (talk) / 50 block shifts.

| Quantity | Talk | Behavior | Activity |
| --- | --- | --- | --- |
| Σ̂₁ single-agent | -0.00 [-0.02, +0.01] | +77.90 [+51.16, +100.83] | +0.07 [+0.02, +0.12] |
| Σσ_i (marginals fitted alone) | -0.00 | +79.00 | +0.07 |
| σ_coll (all partners) | +0.97 [+0.24, +1.70], p 0.01 | +0.22 [-1.51, +1.04], p 0.10 | -0.01 [-0.09, +0.05], p 0.35 |
| σ_nam (named partners) | +7.63 [+4.29, +11.22], p 0.01 | -0.51 [-3.60, +1.81], p 0.47 | -0.08 [-0.32, +0.12], p 0.63 |
| σ_un (unnamed partners) | -0.37 [-1.73, +0.46], p 0.56 | -0.32 [-3.56, +2.23], p 0.33 | -0.23 [-0.53, -0.01], p 0.98 |
| Δ_addr = σ_nam − σ_un | +8.00 [+5.09, +12.13], p 0.01 | -0.18 [-4.33, +4.39], p 0.65 | +0.15 [-0.20, +0.53], p 0.12 |
| ρ_coll | 1.001 | 0.003 | -0.124 |
| exact-dual companion σ_nam | +7.69 | -0.50 | -0.08 |
| block-flip floor of Σ̂₁ (mean) | -0.00 | -3.98 | +0.03 |
| size-matched (12 agents) σ_nam | -0.05 | -0.09 | -0.03 |
| σ_nam without the kickoff day | +7.95 | -0.61 | -0.10 |

H50's J₁ for this period: 0.016. Talk σ_nam per agent-hour: +0.0173 nats.

## Scorecard (period-specific axes)
- C: Δ_addr beats the block-shift null (p 0.01, the minimum for 100 shifts); σ_un is inside it.
- D: the predicted signature (named > unnamed, talk only, ρ_coll ≈ 0 in behavior) appears unfitted.
- F: S51 is the size where the synthetic gives power 1.00 at this effect.
- H: R0 (independent) and R2 (ungated broadcast) rejected in talk; R1 (lagged field) rejected by the address contrast (size 0.03 under the field).

## Native N2: full pairwise talk asymmetry
*Prediction (card):* sign agreement of θ_ij with the naming direction ≥ 0.6 over pairs with |w_ji − w_ij| ≥ 3, above the shift-null 95th percentile; Spearman(|θ_ij|, w_ij + w_ji) > 0.1. Credence 0.4.

- 378 pairs (agents on ≥ 5 days), 235 with a naming imbalance ≥ 3.
- Σ̂(single + pairs) − Σ̂(single) = +6.85×10⁻³ (shift p 0.048, 20 shifts; q95 -0.46).
- Sign agreement 0.52 (shift null mean 0.51, q95 0.55); Spearman(|θ|, naming volume) 0.078 (null q95 0.165).
- **Verdict: failed.** The pairwise model carries the same collective EP as the named mean field, but per-pair asymmetries do not point along the naming direction. Reading: naming is mostly reciprocal (conversations), so the direction of a pair's net naming does not set who follows whom; the gated response shows up as "i follows the agents who name it" summed over partners, not as a stable per-pair hierarchy.
