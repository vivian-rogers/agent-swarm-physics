# H51 × G51: roster growth in one room (#51, sub-units 51a–51l)

**Verdict:** failed
**Role:** native (exploratory) + replication point
**Period:** goal #51 · regime III · one main room · roster grows from about 21 to 32 agents over 51a–51l (the #51 tail, 09-07 →, is held out and masked).

## Why this period
A within-period N sweep with goal, regime and scaffold fixed. H67 found g_lag flat (≈ 0.14) as N grows, because per-read coupling falls with N. So the dial predicts flat observables, while N alone predicts trends. It also tests whether the phase-diagram point of #51 is stable when its own N moves.

## Prediction
*Written 2026-10-04 20:45 UTC, before running on this period.*
- **One-dial prediction (D1):** across sub-units, observables track g_lag, not N: |Spearman ρ(Y_j, N)| < 0.3 for R̂, loop rate and herding share (H11 sub-unit rows), and ρ(Y_j, g_lag) has the sign of the across-period slope b_j.
- **N rival:** |ρ(Y_j, N)| ≥ 0.5 with the sign of the across-period N slope.
- **Expected:** flatness in N holds for ≥ 2/3 observables with credence 0.4; at ≤ 12 sub-units, ρ is noisy (|ρ| < 0.58 is not significant at 5%), so "flat" here means "no detectable trend", reported with the ρ CI.
- **Counts for the dial:** ≥ 2/3 observables flat in N and following g_lag.
- **Note:** 51g spans the operator bookends' end (08-05) and the nudges' end (08-21, NE43); the dial is not built to absorb operator-drive changes.

## Result
*Run 2026-10-04 ~22:10 UTC (exploratory). Data: `data/processed/H51-one-dial-collapse/natives/G51.json`, `natives_units.parquet`.*
Across 12 sub-units (51a–51l, N 21 → 32): ρ(g_lag, N) = 0.08 [−0.54, 0.65] (n 11), so the dial is flat, as H67 found.

| Observable | ρ(Y, N) [95%] | ρ(Y, g_lag) [95%] | flat in N? | across-period N-slope sign matched? |
| --- | --- | --- | --- | --- |
| idea branching R̂ | **+0.83 [+0.50, +0.95]** (p 0.0008) | −0.11 [−0.67, +0.53] | no | yes |
| loop rate | +0.50 [−0.10, +0.84] | +0.19 [−0.46, +0.71] | no | no |
| herding share (H51) | −0.51 [−0.84, +0.09] | −0.15 [−0.69, +0.50] | no | yes |
| herding share (H11 rows, 7 units) | −0.36 [−0.88, +0.54] | −0.29 [−0.85, +0.60] | – | – |

- **Expected (written before):** flat in N for ≥ 2/3 (credence 0.4): **failed, 0/3**. R̂ rises from 0.18 to 0.39 as the roster grows while g_lag stays at ≈ 0.14.
- **Reading:** inside one period, with goal, regime and room fixed, size moves the observables and the coupling dial does not. Two confounds stay: N grows with calendar time (idea-pool saturation, NE38, the NE43 operator wind-down inside 51g), and R̂ rises mechanically when more agents can serve as parents.

## Replication point (layer 1)
**Verdict (replication rule):** failed (the card-level D1 collapse does not hold). Period axes: g_lag 0.142 ± 0.016, c_× 0.0105, S_text 0.08, N 26.5. D1 leave-one-period-out residuals z = +1.1 / −0.4 / +0.4 / −0.4 (settling / herding / branching / loops): #51 sits inside the 80% band of the D1 fit, but that fit explains ≈ 0 of the across-period variance.

## Scorecard (period-specific axes)
D: 0 (the dial predicts flat observables; R̂ rises with N at ρ 0.83). H: N beats the dial within the period (R̂, herding).
