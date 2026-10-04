# H70 × G37: the artifact row of the κ table (2026-03-30 → 2026-04-01)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · 12 agents with an own artifact · events with A⁻ known and ≥ 10 window calls: F 359, P 369, N 36, PN 36 (non-holdout). Primary scale: call scale (forced erasure vs pseudo-erasure).

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
| call: I_A (bits) | +0.058 [+0.01, +0.11]; raw 0.334, floor 0.276; p 0.005 | within-agent permutation | met |
| call: ΔV_A (open × scramble, Poisson) | rel +0.01 [-0.65, +0.91]; +0.00 commits / 20 calls [-0.79, +0.31] (open share F/N 0.15, placebo 0.11) | 0 (reading precedes writing) | not met |
| call: κ_A | +0.05 [-17.33, +6.39] commits / 20 calls / bit | – | – |
| call: context row (cost of the erasure) | cost rel +0.12 [-0.30, +0.37]; I_C +0.020 [-0.07, +0.13] | 0 | – |
| day: I_A (bits) | -0.077 [-0.19, +0.07]; raw 0.422, floor 0.499; p 1.000 | within-agent permutation | not met |
| day: ΔV_A (open × scramble, Poisson) | rel +nan [-1.00, +4.82]; +nan commits / 20 calls [-243999524.41, +0.81] (open share F/N 0.06, placebo 0.14) | 0 (reading precedes writing) | not met |
| day: κ_A | undefined (I_A ≤ 0.02) – commits / 20 calls / bit | – | – |
| day: context row (cost of the erasure) | cost rel +0.43 [-2.20, +0.95]; I_C +0.382 [-0.01, +0.81] | 0 | – |
| P(X⁺ = A⁻ \| commit) | F 0.77 (n 43), P 0.65 (n 51), N 0.50 (n 4), PN 0.83 (n 6) | – | not met |


## Scorecard (period-specific axes)
- **C:** I_A against the within-agent permutation floor; ΔV_A against the placebo arm (Poisson DiD). **E:** forced erasures (exogenous timing) and nights as context scrambles. **F:** synthetic recovery at these counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H70-artifact-store-semantic-info/results/periods.json` (key `G37`).
