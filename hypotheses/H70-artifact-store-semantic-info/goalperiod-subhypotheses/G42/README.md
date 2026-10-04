# H70 × G42: the artifact row of the κ table (2026-05-18 → 2026-05-22)

**Verdict:** failed
**Role:** replication
**Period:** regime III · 14 agents with an own artifact · events with A⁻ known and ≥ 10 window calls: F 646, P 658, N 67, PN 67 (non-holdout). Primary scale: call scale (forced erasure vs pseudo-erasure).

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
| call: I_A (bits) | +0.020 [-0.01, +0.05]; raw 1.061, floor 1.041; p 0.075 | within-agent permutation | not met |
| call: ΔV_A (open × scramble, Poisson) | rel +0.12 [-0.20, +0.61]; +0.22 commits / 20 calls [-0.49, +0.82] (open share F/N 0.16, placebo 0.19) | 0 (reading precedes writing) | not met |
| call: κ_A | +10.80 [-14.01, +27.69] commits / 20 calls / bit | – | – |
| call: context row (cost of the erasure) | cost rel +0.45 [+0.33, +0.57]; I_C -0.006 [-0.10, +0.09] | 0 | – |
| day: I_A (bits) | -0.007 [-0.10, +0.11]; raw 1.255, floor 1.262; p 0.542 | within-agent permutation | not met |
| day: ΔV_A (open × scramble, Poisson) | rel -0.44 [-0.80, +0.83]; -1.15 commits / 20 calls [-5.39, +0.73] (open share F/N 0.19, placebo 0.24) | 0 (reading precedes writing) | not met |
| day: κ_A | undefined (I_A ≤ 0.02) [-113.59, +8.62] commits / 20 calls / bit | – | – |
| day: context row (cost of the erasure) | cost rel +0.34 [-0.08, +0.58]; I_C +0.025 [-0.27, +0.35] | 0 | – |
| P(X⁺ = A⁻ \| commit) | F 0.98 (n 188), P 0.97 (n 231), N 0.78 (n 23), PN 1.00 (n 29) | – | met |


## Scorecard (period-specific axes)
- **C:** I_A against the within-agent permutation floor; ΔV_A against the placebo arm (Poisson DiD). **E:** forced erasures (exogenous timing) and nights as context scrambles. **F:** synthetic recovery at these counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H70-artifact-store-semantic-info/results/periods.json` (key `G42`).
