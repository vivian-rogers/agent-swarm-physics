# H70 × G44: the artifact row of the κ table (2026-05-26 → 2026-05-29)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · 15 agents with an own artifact · events with A⁻ known and ≥ 10 window calls: F 309, P 396, N 54, PN 55 (non-holdout). Primary scale: call scale (forced erasure vs pseudo-erasure).

## Why this period
The common estimator on every non-holdout period with dense git (DQ4 from #30): the artifact channel's information about the next allocation (bits) and its value (commits per 20 calls) at the context erasures this period has. Each period is one point for the κ row of HH307.

## Prediction
*Written 2026-10-04 20:05 UTC, before running on this period (card P1, P2, P7 applied).*
- I_A > 0 (within-agent permutation p < 0.05) at the primary scale; I_A ≥ 0.3 bits expected where agents hold more than one repo in the period.
- ΔV_A (open × scramble DiD, agent-period fixed effects, V_pre covariate) > 0 with the cluster-bootstrap CI excluding 0 at the primary scale.
- P(X⁺ = A⁻ | a commit) ≥ 0.8 after the scramble, within 0.1 of the placebo.
- Counts against: I_A not significant, or ΔV_A's CI excludes 0 below zero.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; agent-day cluster bootstrap, B = 300).* Primary scale: call.

| Statistic | Observed | Null | Verdict |
| --- | --- | --- | --- |
| call: I_A (bits) | +0.248 [+0.12, +0.39]; raw 1.751, floor 1.503; p 0.005 | within-agent permutation | met |
| call: ΔV_A (open × scramble, Poisson) | rel +0.20 [-0.36, +1.02]; +0.38 commits / 20 calls [-1.03, +1.62] (open share F/N 0.34, placebo 0.33) | 0 (reading precedes writing) | not met |
| call: κ_A | +1.51 [-4.23, +9.43] commits / 20 calls / bit | – | – |
| call: context row (cost of the erasure) | cost rel +0.44 [+0.29, +0.54]; I_C -0.086 [-0.29, +0.10] | 0 | – |
| day: I_A (bits) | +0.030 [-0.18, +0.25]; raw 2.653, floor 2.623; p 0.423 | within-agent permutation | not met |
| day: ΔV_A (open × scramble, Poisson) | rel -0.71 [-0.96, +0.62]; -4.00 commits / 20 calls [-20.96, +0.68] (open share F/N 0.28, placebo 0.33) | 0 (reading precedes writing) | not met |
| day: κ_A | -133.86 [-436.39, +6.44] commits / 20 calls / bit | – | – |
| day: context row (cost of the erasure) | cost rel -0.07 [-0.73, +0.37]; I_C +0.300 [-0.03, +0.61] | 0 | – |
| P(X⁺ = A⁻ \| commit) | F 0.71 (n 137), P 0.70 (n 204), N 0.39 (n 28), PN 0.59 (n 27) | – | not met |


## Scorecard (period-specific axes)
- **C:** I_A against the within-agent permutation floor; ΔV_A against the placebo arm (Poisson DiD). **E:** forced erasures (exogenous timing) and nights as context scrambles. **F:** synthetic recovery at these counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H70-artifact-store-semantic-info/results/periods.json` (key `G44`).
