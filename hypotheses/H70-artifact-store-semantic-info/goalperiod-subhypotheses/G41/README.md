# H70 × G41: the artifact row of the κ table (2026-05-11 → 2026-05-15)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · 13 agents with an own artifact · events with A⁻ known and ≥ 10 window calls: F 575, P 598, N 65, PN 65 (non-holdout). Primary scale: call scale (forced erasure vs pseudo-erasure).

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
| call: I_A (bits) | +0.343 [+0.22, +0.48]; raw 1.069, floor 0.726; p 0.005 | within-agent permutation | met |
| call: ΔV_A (open × scramble, Poisson) | rel +0.11 [-0.34, +0.68]; +0.13 commits / 20 calls [-0.70, +0.54] (open share F/N 0.62, placebo 0.53) | 0 (reading precedes writing) | not met |
| call: κ_A | +0.38 [-2.23, +1.66] commits / 20 calls / bit | – | – |
| call: context row (cost of the erasure) | cost rel +0.44 [+0.33, +0.55]; I_C +0.077 [-0.04, +0.23] | 0 | – |
| day: I_A (bits) | +0.065 [-0.12, +0.26]; raw 0.890, floor 0.825; p 0.159 | within-agent permutation | not met |
| day: ΔV_A (open × scramble, Poisson) | rel +0.02 [-0.82, +6.39]; +0.03 commits / 20 calls [-5.86, +1.54] (open share F/N 0.46, placebo 0.62) | 0 (reading precedes writing) | not met |
| day: κ_A | +0.44 [-58.61, +27.32] commits / 20 calls / bit | – | – |
| day: context row (cost of the erasure) | cost rel +0.33 [-0.11, +0.62]; I_C +0.452 [+0.17, +0.73] | 0 | – |
| P(X⁺ = A⁻ \| commit) | F 0.88 (n 245), P 0.89 (n 289), N 0.54 (n 24), PN 0.89 (n 36) | – | met |


## Scorecard (period-specific axes)
- **C:** I_A against the within-agent permutation floor; ΔV_A against the placebo arm (Poisson DiD). **E:** forced erasures (exogenous timing) and nights as context scrambles. **F:** synthetic recovery at these counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H70-artifact-store-semantic-info/results/periods.json` (key `G41`).
