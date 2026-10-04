# H10 × G17: Each agent: build your own personal website (2025-10-13 → 2025-10-17)

**Verdict:** failed (pair test #16 → #17; NE34)
**Verdict (1b):** failed (both models)
**Role:** exploratory
**Period:** regime I · mode I · 7 agents · #general only · 5 active days; no step change. Segment A = days 2+ (10-14 … 10-17, ~24 windows).

## Why this period
Individual-objective week after free week #16. Every agent gets the same instruction about its own site, so ĝ is shared while coordination is not required: the closest the village comes to a pure external field. The H10 test (free #16 → this week) is in [`../NE34/`](../NE34/README.md); this folder's verdict mirrors that pair's verdict, since the tilt predictions are statements about this week.

## Prediction
*Written 2026-10-03, before running on this period.* Card P1–P4 for the pair #16 → #17 (see the card for the rules), plus:
- **A1, the push exists.** Δ̄ > 0 along ĝ, and the swarm's daily mean alignment on every day of A is above the free week's mean.
- **A2, stationarity (axis B).** No trend across the days of A in daily mean δm along ĝ (CI contains 0); day 1 (excluded from A) differs from days 2+ (kickoff transient).
- **A3, weak coupling.** g_A < 0.5.
- **Verdict rule:** the pair's combined verdict from P1–P4 (`supported` / `failed` / `mixed`), with A1–A3 reported alongside.

## Result
Run 2026-10-03. Pair #16 → #17, A = 10-14 … 10-17 (24 windows), N = 7.

| Prediction | Observed (90% CI) | Null / rival | Verdict |
| --- | --- | --- | --- |
| A1 push exists | Δ̄ = 0.134 [0.056, 0.211]; every day of A above the free-week mean (0.029), the lowest only just | R0 | ✓ |
| P1 Δᵢ ∝ κ2ᵢ^F | r = −0.69 (perm p = 0.97); cross-split r = −0.68; tilt LOAO error 2.1× translation's | R1, R2 | ✗ (robust: r < 0 in 6/6 robustness variants) |
| P2 variance by the tilt | ε = 1.42 (non-perturbative): **n/a**. Descriptive: ρ = 1.73 [0.55, 3.26] vs the first-order tilt; ×2.8 vs the free week (ρ_Gauss = 1.03); transverse ρ⊥ = −0.12 | synthetic H at ε ≈ 1.5: ρ ≈ −0.25 | n/a; descriptively opposite (field-specific dispersal) |
| P3 (descriptive) | g 0.51 → 0.70, Δg = 0.20 [−0.13, 0.72] | R5 predicted a *fall* (individual objectives) | not counted; sign against R5's expectation |
| P4 (descriptive) | D = −0.20 [−0.38, 0.02] | | not counted |
| A2 stationarity | no trend over days 2+ (slope CI [−0.018, 0.045]); day 1 − rest = +0.02 (no distinct transient) | | ✓ trend / ✗ transient |
| A3 g_A < 0.5 | g_A = 0.70 [0.44, 0.76] | | ✗ |

Data: `data/processed/H10-goals-are-legendre-pushes/G17/period.json` and `NE34/pairs.json`. Figures: [`figures/shape_and_drift.pdf`](figures/shape_and_drift.pdf) (whole first unit, day 1 included) and the pair figure [`../NE34/figures/pair_16-17.pdf`](../NE34/figures/pair_16-17.pdf). Card: [`../../README.md`](../../README.md).

## Scorecard (period-specific axes)
- **C:** beats R0 only. **D:** P1 fails robustly. **E:** the tilt fails to predict the goal step. This was the predicted cleanest case for P1, and it is the clearest failure.

## Notes
- 2026-10-03: the agent with the largest free-week fluctuation along ĝ₁₇ barely moved (Δ ≈ 0.01), and the agent that moved most (Δ ≈ 0.31) was one of the two quietest. Mean pairwise signal correlation along ĝ rose 0.17 → 0.40.

## Round 1b (improved data, 2026-10-04)
*Inputs: shared goal fields (`goal_fields`; H10's own goal and kickoff vectors already matched them to cos ≥ 0.9999999, so bge numbers are unchanged), the second embedding model gte-modernbert, DQ5 restatement dedupe and style-residualized vectors. Data: `data/processed/H10-goals-are-legendre-pushes/r1b/<config>/`. Role: replication (the round-1 estimator, unchanged).*

bge identical (Δ̄ 0.134, ε 1.42, r −0.69, variance along ĝ ×2.8). gte: Δ̄ 0.131 [0.068, 0.198], ε 2.03, r −0.49, ρ +1.26 vs ρ⊥ −0.20, g_A 0.57 [−0.02, 0.68]. Deduped / style: r −0.40 to −0.81.
