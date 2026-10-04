# H70 × G36: the artifact row of the κ table (2026-03-23 → 2026-03-27)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · 12 agents with an own artifact · events with A⁻ known and ≥ 10 window calls: F 487, P 505, N 60, PN 60 (non-holdout). Primary scale: call scale (forced erasure vs pseudo-erasure).

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
| call: I_A (bits) | +0.045 [-0.01, +0.11]; raw 0.208, floor 0.163; p 0.010 | within-agent permutation | met |
| call: ΔV_A (open × scramble, Poisson) | rel +0.25 [-0.40, +1.41]; +0.13 commits / 20 calls [-0.33, +0.42] (open share F/N 0.17, placebo 0.19) | 0 (reading precedes writing) | not met |
| call: κ_A | +2.82 [-7.11, +12.11] commits / 20 calls / bit | – | – |
| call: context row (cost of the erasure) | cost rel +0.30 [+0.01, +0.49]; I_C +0.053 [-0.04, +0.14] | 0 | – |
| day: I_A (bits) | +0.126 [-0.05, +0.34]; raw 0.335, floor 0.209; p 0.045 | within-agent permutation | met |
| day: ΔV_A (open × scramble, Poisson) | rel +0.14 [-0.92, +6.60]; +0.02 commits / 20 calls [-1.92, +0.23] (open share F/N 0.17, placebo 0.30) | 0 (reading precedes writing) | not met |
| day: κ_A | +0.19 [-19.15, +3.42] commits / 20 calls / bit | – | – |
| day: context row (cost of the erasure) | cost rel +0.45 [-0.21, +0.81]; I_C +0.316 [+0.06, +0.58] | 0 | – |
| P(X⁺ = A⁻ \| commit) | F 0.71 (n 78), P 0.67 (n 101), N 0.33 (n 9), PN 0.80 (n 15) | – | not met |


## Scorecard (period-specific axes)
- **C:** I_A against the within-agent permutation floor; ΔV_A against the placebo arm (Poisson DiD). **E:** forced erasures (exogenous timing) and nights as context scrambles. **F:** synthetic recovery at these counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H70-artifact-store-semantic-info/results/periods.json` (key `G36`).
