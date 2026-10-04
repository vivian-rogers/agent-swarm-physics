# H51 × NE42: rooms merged for one week (#39 → #40 → #41, A-B-A)

**Verdict:** failed
**Role:** native (exploratory)
**Period:** goals #39, #40, #41 · regime III · roster ≈ 15 · #39 two rooms, #40 one merged room (#universe-coordination), #41 two rooms again.

## Why this period
The merge doubles the room size at a fixed roster. H67 measures the read-out coupling collapsing in the merged week (g_lag 0.144 → 0.003 → 0.189) because per-read coupling dilutes. Room N, in contrast, goes up and back down. So the dial (K) and the size rival (N) predict *opposite* A-B-A signs for #40. The goal changes each week (#40 has a shared objective), which confounds the contrast.

## Prediction
*Written 2026-10-04 20:45 UTC, before running on this NE.*
- **One-dial prediction (D1):** for each observable j, sign(Y_j(#40) − mean(Y_j(#39), Y_j(#41))) = sign(b_j · ΔK), with ΔK = g_lag(#40) − mean(g_lag(#39), g_lag(#41)) < 0 and b_j the across-period slope fitted on all periods except #39–#41.
- **N rival:** the #40 deviation has the sign of c_j · ΔlogN_room, with c_j the across-period slope on log N fitted the same way.
- Observables: τ_settle, herding share (H11), R̂, loop rate (all period level).
- **Expected:** the A-B-A shape follows the dial on ≥ 2 of the 4 observables with credence 0.3; the #40 deviation exceeds the D1-predicted size (|b_j ΔK|) on ≥ 2 observables with credence 0.6 (goal effects dominate).
- **Counts for the dial:** ≥ 3/4 observables follow the D1 sign, and their #40 deviations lie within the D1 prediction band.

## Result
*Run 2026-10-04 ~22:10 UTC (exploratory). Data: `data/processed/H51-one-dial-collapse/natives/NE42.json`.*
g_lag 0.144 → **0.003** → 0.189 (#39 → #40 → #41), so ΔK(#40) = −0.164. Room size doubles in #40 (Δlog N_room = log 2). Slopes fitted across all other periods (#39–#41 excluded).

| Observable | #39 / #40 / #41 | #40 deviation | D1 predicts | N rival predicts | follows D1 | follows N |
| --- | --- | --- | --- | --- | --- | --- |
| settling (log h) | 1.83 / 2.85 / 1.94 | +0.96 | −0.77 | +0.56 | no | yes |
| herding share | 0.013 / 0.004 / 0.028 | −0.017 | +0.053 | −0.129 | no | yes |
| branching (logit R̂) | −2.34 / −1.16 / −1.14 | +0.57 | +0.16 | +0.30 | yes | yes |
| loop rate (logit) | −1.25 / −2.15 / −2.62 | −0.22 | +1.85 | −0.93 | no | yes |

- **Expected (written before):** the A-B-A follows the dial on ≥ 2/4 (credence 0.3): **failed, 1/4**. The #40 deviation exceeds the D1 size on ≥ 2 (0.6): **seen** for settling and branching (2/4).
- **N rival:** the sign of the #40 deviation matches the across-period log-N slope on **4/4** observables. Every deviation is still inside the wide D1 band (residual SD across periods), and #40 has its own goal (a shared objective), so this is a sign test, not a size test.
- **Reading:** where coupling and room size move in opposite directions, the observables follow room size, not the read-out coupling.

## Scorecard (period-specific axes)
E: 0 for the dial (1/4 signs); H: N beats the dial on sign (4/4 vs 1/4), goal-confounded.
