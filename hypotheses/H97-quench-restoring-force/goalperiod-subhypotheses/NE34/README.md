# H97 × NE34: the restoring-force law across all eligible kickoffs (cross-kickoff tests)

**Verdict:** supported
**Role:** replication
**Period:** every eligible kickoff transition (exception (c): the boundary is the object). 18 same-regime transitions with N ≥ 5 and placebo boundaries (#11–#13, #17–#21, #25–#27, #31, #36, #38–#42); 5 more with N = 4 (#4–#8) enter the per-agent analysis only; #37 (cross-regime) is a variant. Regimes I, II, III, never pooled into one fit: per-transition estimates are combined by random-effects meta-analysis.

## Why this period
The card's primary tests (P1–P4) are statements about many kickoffs, and agent constancy (P4) needs agents seen at several kickoffs.

## Prediction
*Written 2026-10-04 ~20:25 UTC in the card (P1–P8), amended ~20:48 UTC (Amendment 1) before any real-data statistic along a kickoff direction.* Verdict rule: the law is supported if P1 holds, P3's slope (Δρ∥ after Amendment 1) holds and P2 does not fail; failed if P1 fails; mixed otherwise. P4 has its own verdict line.

## Result
| Test | Observed (meta-analysis over 18 transitions, 90% CI = ±1.645 SE) | Verdict |
| --- | --- | --- |
| P1 extra forgetting Δρ | +0.26 ± 0.04 (bge); ρ_kick median 0.42 vs ρ0 0.68; Δρ > 0 in 16/18 (sign p 0.0007). gte +0.26, style +0.25, dedupe +0.28, centered +0.26 | supported |
| P2 isotropy β∥ − β⊥ | −0.17 ± 0.16 (passes the rule); style −0.37 (fails), dedupe −0.28, centered −0.20 (neither); scale-free: Δρ∥ +0.63 ± 0.27 vs Δρ⊥ +0.25 ± 0.04 in bge, larger along k̂ in all 7 configurations | passes by rule; fragile |
| P3 slope (Δρ∥ > 0) | +0.63 ± 0.27 | supported |
| P3 intercept (centered) | a = +0.12 ± 0.02 (gte +0.17 ± 0.03): day 1 lands beyond the settled level (R5 overshoot / R6 common-mode jump) | failed (credence 0.3 given) |
| P4 agent constant (χ^mem split-half r) | bge r 0.30 (p 0.14; null 95% 0.43); gte r 0.48 (p 0.027); centered −0.06; style 0.19; HH form χ^∥: r −0.19. Power 0.30 | inconclusive |
| P5 named vs free | non-free median Δρ 0.27 vs free 0.19 (n = 2; p 0.27); named frozen projects 0.42 vs 0.27 (p 0.22) | not supported (underpowered) |
| P6 lab effect | permutation p 0.49 | supported (no lab effect) |
| P7 variants | P1's sign holds in all 7 configurations | supported |
| P8 weekend gap | placebo ρ0 0.73 (≥ 2-day gaps, n 12) vs 0.69 (1 day, n 149) | supported |

Data: `data/processed/H97-quench-restoring-force/NE34/{summary.json, transitions_all_configs.parquet, chi_agents.parquet, placebo_gaps.parquet}`. Figure: `../../figures/summary_obs.pdf`.

## Scorecard (period-specific axes)
- C: P1 beats the kickoff-matched placebo (ordinary day boundaries of the same agents) in 16/18 transitions.
- D: the intercept is an unfitted prediction; it fails (overshoot).
- F: synthetic recovery at real counts; P1 calibrated (R0 false-positive rate 0.025–0.05) only after switching to ρ.
- H: rival R0 (translation) rejected; R2 (longitudinal only) not supported because transverse forgetting is +0.25 > 0; R5/R6 favoured over the HH-literal law by the intercept.

## Notes
- The within-transition reliability of χ^mem (median 0.89) is an upper bound: both day-1 halves share the same pre-state halves.
