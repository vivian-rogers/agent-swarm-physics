# H70 × G51: the artifact row of the κ table (2026-07-06 → 2026-09-04)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · 32 agents with an own artifact · events with A⁻ known and ≥ 10 window calls: F 12780, P 13665, N 1028, PN 1039 (non-holdout). Primary scale: call scale (forced erasure vs pseudo-erasure).

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
| call: I_A (bits) | +0.143 [+0.11, +0.17]; raw 1.536, floor 1.393; p 0.005 | within-agent permutation | met |
| call: ΔV_A (open × scramble, Poisson) | rel -0.07 [-0.17, +0.02]; -0.12 commits / 20 calls [-0.31, +0.03] (open share F/N 0.23, placebo 0.23) | 0 (reading precedes writing) | not met |
| call: κ_A | -0.84 [-2.29, +0.18] commits / 20 calls / bit | – | – |
| call: context row (cost of the erasure) | cost rel +0.42 [+0.39, +0.46]; I_C +0.065 [+0.04, +0.09] | 0 | – |
| day: I_A (bits) | +0.094 [+0.05, +0.14]; raw 2.070, floor 1.976; p 0.005 | within-agent permutation | met |
| day: ΔV_A (open × scramble, Poisson) | rel +0.09 [-0.14, +0.35]; +0.19 commits / 20 calls [-0.39, +0.66] (open share F/N 0.27, placebo 0.30) | 0 (reading precedes writing) | not met |
| day: κ_A | +2.01 [-4.39, +7.01] commits / 20 calls / bit | – | – |
| day: context row (cost of the erasure) | cost rel +0.08 [-0.01, +0.16]; I_C +0.141 [+0.05, +0.24] | 0 | – |
| P(X⁺ = A⁻ \| commit) | F 0.88 (n 4288), P 0.86 (n 5461), N 0.78 (n 441), PN 0.80 (n 499) | – | met |


## Scorecard (period-specific axes)
- **C:** I_A against the within-agent permutation floor; ΔV_A against the placebo arm (Poisson DiD). **E:** forced erasures (exogenous timing) and nights as context scrambles. **F:** synthetic recovery at these counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H70-artifact-store-semantic-info/results/periods.json` (key `G51`).
