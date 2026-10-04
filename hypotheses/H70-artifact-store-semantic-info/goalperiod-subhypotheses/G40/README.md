# H70 × G40: the artifact row of the κ table (2026-05-04 → 2026-05-08)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · 14 agents with an own artifact · events with A⁻ known and ≥ 10 window calls: F 758, P 781, N 69, PN 67 (non-holdout). Primary scale: call scale (forced erasure vs pseudo-erasure).

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
| call: I_A (bits) | +0.083 [+0.02, +0.17]; raw 0.636, floor 0.552; p 0.005 | within-agent permutation | met |
| call: ΔV_A (open × scramble, Poisson) | rel -0.27 [-0.47, +0.10]; -0.69 commits / 20 calls [-1.64, +0.15] (open share F/N 0.64, placebo 0.59) | 0 (reading precedes writing) | not met |
| call: κ_A | -8.26 [-37.71, +1.68] commits / 20 calls / bit | – | – |
| call: context row (cost of the erasure) | cost rel +0.34 [+0.25, +0.41]; I_C +0.050 [-0.00, +0.10] | 0 | – |
| day: I_A (bits) | +0.300 [+0.06, +0.58]; raw 1.152, floor 0.852; p 0.010 | within-agent permutation | met |
| day: ΔV_A (open × scramble, Poisson) | rel -0.22 [-0.83, +2.06]; -0.35 commits / 20 calls [-7.28, +0.76] (open share F/N 0.51, placebo 0.58) | 0 (reading precedes writing) | not met |
| day: κ_A | -1.15 [-42.82, +3.25] commits / 20 calls / bit | – | – |
| day: context row (cost of the erasure) | cost rel +0.47 [+0.24, +0.65]; I_C -0.135 [-0.36, +0.12] | 0 | – |
| P(X⁺ = A⁻ \| commit) | F 0.95 (n 348), P 0.95 (n 408), N 0.86 (n 28), PN 0.91 (n 35) | – | met |


## Scorecard (period-specific axes)
- **C:** I_A against the within-agent permutation floor; ΔV_A against the placebo arm (Poisson DiD). **E:** forced erasures (exogenous timing) and nights as context scrambles. **F:** synthetic recovery at these counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H70-artifact-store-semantic-info/results/periods.json` (key `G40`).
