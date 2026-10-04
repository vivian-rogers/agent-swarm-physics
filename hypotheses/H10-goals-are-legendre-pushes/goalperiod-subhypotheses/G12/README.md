# H10 × G12: Form two teams and debate each other, while one agent judges (2025-09-01 → 2025-09-05)

**Verdict:** failed (pair test #11 → #12a; NE34)
**Verdict (1b):** failed (both models)
**Role:** replication (exploratory)
**Period:** regime I · mode M · 7 agents · #general only · 5 active days. **Split:** scaffold change C (history search + CoT memory) on 2025-09-05, so the analyzed unit is 12a = 09-01 … 09-04; segment A = days 2+ (09-02 … 09-04, ~18 windows).

## Why this period
Assigned week after free week #11. Teams make this a two-block field (ferromagnetic within teams, antiferromagnetic across), so a single ĝ is a coarse description; it is the pair most likely to break P1. The H10 test (free #11 → this week) is in [`../NE34/`](../NE34/README.md); this folder's verdict mirrors that pair's verdict, since the tilt predictions are statements about this week.

## Prediction
*Written 2026-10-03, before running on this period.* Card P1–P4 for the pair #11 → #12 (see the card for the rules), plus:
- **A1, the push exists.** Δ̄ > 0 along ĝ, and the swarm's daily mean alignment on every day of A is above the free week's mean.
- **A2, stationarity (axis B).** No trend across the days of A in daily mean δm along ĝ (CI contains 0); day 1 (excluded from A) differs from days 2+ (kickoff transient).
- **A3, weak coupling.** g_A < 0.5.
- **Verdict rule:** the pair's combined verdict from P1–P4 (`supported` / `failed` / `mixed`), with A1–A3 reported alongside.

## Result
Run 2026-10-03. Pair #11 → #12a, A = 09-02 … 09-04 (18 windows), N = 7.

| Prediction | Observed (90% CI) | Null / rival | Verdict |
| --- | --- | --- | --- |
| A1 push exists | Δ̄ = 0.203 [0.140, 0.264]; every day of 12a above the free-week mean (−0.017) | R0: Δ̄ = 0 | ✓ |
| P1 Δᵢ ∝ κ2ᵢ^F | r = −0.37 (perm p = 0.80); cross-split r = −0.45; tilt LOAO error 2.4× translation's | R1 uniform translation, R2 convergence | ✗ (convergence: slope of Δᵢ on μᵢ^F = −1.41, cross-split) |
| P2 variance by the tilt | push ε = 3.06 SDs (non-perturbative): **n/a**. Descriptive: the first-order prediction is negative (meaningless); variance along ĝ vs free week ×7.7 (ρ_Gauss = 2.04), transverse ρ⊥ = −0.14 | synthetic H at ε ≈ 3: variance *shrinks* (median ρ −0.6 to −1.6) | n/a; descriptively the opposite of the tilt |
| P3 (descriptive) | g 0.55 → 0.79, Δg = 0.25 [0.15, 0.57] | R5: coupling changes | the loop gain along ĝ rose (R5-like); not counted |
| P4 (descriptive) | D = −0.60 [−0.71, −0.34] | | not counted |
| A2 stationarity | day 1 − days 2+ = +0.16 (a kickoff transient); days 2+ still decaying, slope −0.033 [−0.050, −0.012] | | ✗ (non-stationary A) |
| A3 g_A < 0.5 | g_A = 0.79 [0.78, 0.81] | | ✗ |

Data: `data/processed/H10-goals-are-legendre-pushes/G12/period.json` and `NE34/pairs.json`. Figures: [`figures/shape_and_drift.pdf`](figures/shape_and_drift.pdf) (whole first unit, day 1 included) and the pair figure [`../NE34/figures/pair_11-12.pdf`](../NE34/figures/pair_11-12.pdf). Card: [`../../README.md`](../../README.md).

## Scorecard (period-specific axes)
- **C:** beats R0 only. **D:** P1 fails (unfitted). **E:** the goal change is the intervention; the tilt does not predict it. **G:** the team-debate structure (two blocks) was expected to be hardest for a single ĝ.

## Notes
- 2026-10-03: mean pairwise signal correlation along ĝ rose 0.20 → 0.64: in 12a the agents move on and off the goal direction together (debate rounds).

## Round 1b (improved data, 2026-10-04)
*Inputs: shared goal fields (`goal_fields`; H10's own goal and kickoff vectors already matched them to cos ≥ 0.9999999, so bge numbers are unchanged), the second embedding model gte-modernbert, DQ5 restatement dedupe and style-residualized vectors. Data: `data/processed/H10-goals-are-legendre-pushes/r1b/<config>/`. Role: replication (the round-1 estimator, unchanged).*

bge identical to round 1 (Δ̄ 0.203, ε 3.06, r −0.37, convergence slope −1.41, g_A 0.79). gte: Δ̄ 0.235 [0.170, 0.296], ε 3.00, r −0.53, slope −1.25, g_A 0.81 [0.79, 0.82]; day 1 minus days 2+ +0.18 (bge +0.16); the day-2–4 relaxation slope is −0.016/day [−0.038, +0.002] in gte vs −0.033 in bge. Deduped and style-residualized: r −0.32 to −0.66 (bge), −0.05 to −0.56 (gte).
