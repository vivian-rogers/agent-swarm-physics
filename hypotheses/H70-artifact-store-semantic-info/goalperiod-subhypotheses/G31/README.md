# H70 × G31: the artifact row of the κ table (2026-02-16 → 2026-02-20)

**Verdict:** mixed
**Role:** replication
**Period:** regime I · 12 agents with an own artifact · events with A⁻ known and ≥ 10 window calls: F 0, P 0, N 55, PN 56 (non-holdout). Primary scale: day scale (night vs mid-day placebo).

## Why this period
The common estimator on every non-holdout period with dense git (DQ4 from #30): the artifact channel's information about the next allocation (bits) and its value (commits per 20 calls) at the context erasures this period has. Each period is one point for the κ row of HH307.

## Prediction
*Written 2026-10-04 20:05 UTC, before running on this period (card P1, P2, P7 applied).*
- I_A > 0 (within-agent permutation p < 0.05) at the primary scale; I_A ≥ 0.3 bits expected where agents hold more than one repo in the period.
- ΔV_A (open × scramble DiD, agent-period fixed effects, V_pre covariate) > 0 with the cluster-bootstrap CI excluding 0 at the primary scale.
- P(X⁺ = A⁻ | a commit) ≥ 0.8 after the scramble, within 0.1 of the placebo.
- Counts against: I_A not significant, or ΔV_A's CI excludes 0 below zero.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; agent-day cluster bootstrap, B = 300).* Primary scale: day.

| Statistic | Observed | Null | Verdict |
| --- | --- | --- | --- |
| day: I_A (bits) | +0.212 [-0.00, +0.45]; raw 0.878, floor 0.667; p 0.015 | within-agent permutation | met |
| day: ΔV_A (open × scramble, Poisson) | rel +2.05 [-0.57, +19.81]; +0.34 commits / 20 calls [-0.44, +0.67] (open share F/N 0.33, placebo 0.21) | 0 (reading precedes writing) | not met |
| day: κ_A | +1.59 [-3.98, +7.32] commits / 20 calls / bit | – | – |
| day: context row (cost of the erasure) | cost rel +0.58 [+0.18, +0.79]; I_C +0.099 [-0.29, +0.48] | 0 | – |
| P(X⁺ = A⁻ \| commit) | N 0.83 (n 12), PN 0.36 (n 22) | – | met |


## Scorecard (period-specific axes)
- **C:** I_A against the within-agent permutation floor; ΔV_A against the placebo arm (Poisson DiD). **E:** forced erasures (exogenous timing) and nights as context scrambles. **F:** synthetic recovery at these counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H70-artifact-store-semantic-info/results/periods.json` (key `G31`).
