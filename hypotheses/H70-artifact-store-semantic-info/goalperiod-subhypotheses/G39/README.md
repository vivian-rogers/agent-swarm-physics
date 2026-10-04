# H70 × G39: the artifact row of the κ table (2026-04-27 → 2026-05-01)

**Verdict:** failed
**Role:** replication
**Period:** regime III · 14 agents with an own artifact · events with A⁻ known and ≥ 10 window calls: F 697, P 714, N 67, PN 69 (non-holdout). Primary scale: call scale (forced erasure vs pseudo-erasure).

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
| call: I_A (bits) | -0.002 [-0.01, +0.01]; raw 1.587, floor 1.589; p 0.507 | within-agent permutation | not met |
| call: ΔV_A (open × scramble, Poisson) | rel -0.23 [-0.55, +0.17]; -0.51 commits / 20 calls [-1.70, +0.23] (open share F/N 0.46, placebo 0.44) | 0 (reading precedes writing) | not met |
| call: κ_A | undefined (I_A ≤ 0.02) – commits / 20 calls / bit | – | – |
| call: context row (cost of the erasure) | cost rel +0.40 [+0.28, +0.51]; I_C +0.050 [-0.03, +0.14] | 0 | – |
| day: I_A (bits) | -0.138 [-0.23, -0.02]; raw 1.932, floor 2.070; p 0.985 | within-agent permutation | not met |
| day: ΔV_A (open × scramble, Poisson) | rel +0.38 [-0.40, +3.29]; +0.56 commits / 20 calls [-1.31, +1.75] (open share F/N 0.48, placebo 0.45) | 0 (reading precedes writing) | not met |
| day: κ_A | undefined (I_A ≤ 0.02) – commits / 20 calls / bit | – | – |
| day: context row (cost of the erasure) | cost rel -0.03 [-0.40, +0.19]; I_C +0.087 [-0.19, +0.34] | 0 | – |
| P(X⁺ = A⁻ \| commit) | F 0.99 (n 287), P 0.98 (n 360), N 0.76 (n 34), PN 1.00 (n 38) | – | met |


## Scorecard (period-specific axes)
- **C:** I_A against the within-agent permutation floor; ΔV_A against the placebo arm (Poisson DiD). **E:** forced erasures (exogenous timing) and nights as context scrambles. **F:** synthetic recovery at these counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H70-artifact-store-semantic-info/results/periods.json` (key `G39`).
