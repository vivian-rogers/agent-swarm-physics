# H129 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 09-04 (non-holdout; tail held out))

**Verdict:** descriptive
**Role:** exploratory (replication)
**Period:** regime III · mode P · 21–32 agents · #general (+#focus in 51g) · 45 days. Shared-goal code: own-role.

## Why this period
Private-goal era: twelve non-holdout units (51a–l), most hops of any period; own-role (agents avoid occupied repos, H93).

## Prediction
*Written 2026-10-04 22:19 UTC, before running H129 on this period.*
- Own-role week: HH370 predicts circulation in shared-goal weeks only. Card P6: |𝒜_cyc| and the hop rate lower than in shared-goal units.
- Card P4 still applies: m_2 > 0 (new own repos are born and joined). Card P5a/b: geometric dwell; low hop rate (high habit).
- Verdict rule: descriptive (no HH prediction for own-role weeks); numbers reported for P4–P6.

## Result
*Run 2026-10-04 23:15 UTC (`scheme/build.py`, `analysis/run.py`; non-holdout days).* Work channel primary. p values one-sided; reversal null = per-agent sequence flips (2,000); W1* = age walker calibrated to m_2 and the return share (400 runs).

| Unit | Channel | Hops / triples | A_3 [boot] , reversal p | 𝒜_cyc [boot], reversal p; W1* | m_2, reversal p | κ_c, DB p | W1* calibration | dwell slope γ [95%] | testable | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | attention | 243 / 149 | 0.31 [-0.16, 0.85], p 0.195 | -0.28 [-1.49, 0.90], p 0.668; W1* q95 1.02, p 0.643 | 0.05, p 0.134 | 0.95, DB p 0.643 | λ̂ 0.75, b̂ 2.0; return share 0.53 | -1.06 [-1.27, -0.85] | yes | descriptive |
| 51a | work | 57 / 27 | 1.73 [0.51, 3.30], p 0.059 | 2.19 [0.85, 4.14], p 0.028; W1* q95 2.66, p 0.110 | 0.16, p 0.059 | 0.67, DB p 0.375 | λ̂ 0.75, b̂ 2.0; return share 0.47 | -0.36 [-0.54, -0.18] | no | descriptive |
| 51b | attention | 72 / 47 | 0.79 [0.00, 2.34], p 0.069 | 1.53 [-0.27, 4.10], p 0.069; W1* q95 1.51, p 0.052 | 0.11, p 0.154 | 0.67, DB p 0.138 | λ̂ 0.75, b̂ 1.0; return share 0.29 | -1.58 [-2.17, -1.00] | yes | descriptive |
| 51b | work | 15 / 6 | -1.10 [-1.95, 0.00], p 1.000 | -0.59 [-1.95, 1.95], p 0.749; W1* q95 –, p – | -0.07, p 0.748 | 0.56, DB p 0.195 | λ̂ –, b̂ –; return share 0.27 | – | no | descriptive |
| 51c | attention | 355 / 241 | 0.77 [0.30, 1.23], p 0.008 | 1.47 [0.41, 2.38], p 0.014; W1* q95 0.77, p 0.002 | 0.10, p 0.005 | 0.96, DB p 0.086 | λ̂ -1.00, b̂ 2.0; return share 0.54 | -1.05 [-1.20, -0.89] | yes | descriptive |
| 51c | work | 59 / 18 | 1.00 [-1.61, 2.83], p 0.251 | -0.44 [-2.71, 2.71], p 0.666; W1* q95 3.30, p 0.643 | 0.12, p 0.211 | 0.23, DB p 0.698 | λ̂ 0.75, b̂ 2.0; return share 0.59 | -0.33 [-0.51, -0.15] | no | descriptive |
| 51d | attention | 336 / 184 | -0.23 [-0.71, 0.16], p 0.886 | -0.81 [-2.15, -0.03], p 0.961; W1* q95 0.91, p 0.935 | -0.01, p 0.737 | 0.91, DB p 0.953 | λ̂ -1.00, b̂ 2.0; return share 0.63 | -0.94 [-1.09, -0.79] | yes | descriptive |
| 51d | work | 71 / 24 | 0.79 [-1.61, 2.83], p 0.267 | 0.35 [-4.14, 3.60], p 0.421; W1* q95 2.54, p 0.357 | 0.07, p 0.204 | 0.49, DB p 0.610 | λ̂ 0.00, b̂ 3.0; return share 0.59 | -0.41 [-0.59, -0.23] | no | descriptive |
| 51e | attention | 273 / 143 | 0.25 [-0.09, 0.62], p 0.142 | -0.40 [-1.46, 0.56], p 0.781; W1* q95 -0.59, p 0.005 | 0.04, p 0.089 | 0.89, DB p 0.977 | λ̂ 4.00, b̂ 1.0; return share 0.60 | -0.88 [-1.06, -0.70] | yes | descriptive |
| 51e | work | 39 / 7 | 0.85 [-1.61, 2.56], p 0.388 | 0.34 [-2.79, 3.22], p 0.489; W1* q95 –, p – | 0.08, p 0.350 | 0.12, DB p 0.597 | λ̂ –, b̂ –; return share 0.56 | -0.32 [-0.58, -0.07] | no | descriptive |
| 51f | attention | 418 / 245 | 0.08 [-0.33, 0.55], p 0.382 | 0.10 [-0.69, 0.92], p 0.383; W1* q95 0.68, p 0.145 | 0.00, p 0.535 | 0.96, DB p 0.959 | λ̂ 0.75, b̂ 2.0; return share 0.64 | -0.85 [-0.98, -0.71] | yes | descriptive |
| 51f | work | 108 / 28 | 0.89 [-0.20, 2.20], p 0.157 | 1.51 [-0.17, 4.11], p 0.078; W1* q95 2.71, p 0.195 | 0.07, p 0.096 | 0.61, DB p 0.785 | λ̂ 0.75, b̂ 4.5; return share 0.70 | -0.33 [-0.46, -0.20] | yes | descriptive |
| 51g | attention | 1040 / 629 | 0.04 [-0.19, 0.27], p 0.409 | -0.27 [-0.69, 0.24], p 0.858; W1* q95 0.41, p 0.840 | 0.00, p 0.465 | 0.98, DB p 0.999 | λ̂ 0.00, b̂ 2.0; return share 0.71 | -0.87 [-0.96, -0.79] | yes | descriptive |
| 51g | work | 355 / 135 | 0.45 [0.05, 1.37], p 0.044 | 0.81 [-0.19, 2.52], p 0.072; W1* q95 1.12, p 0.112 | 0.03, p 0.063 | 0.82, DB p 0.989 | λ̂ 1.50, b̂ 4.5; return share 0.79 | -0.40 [-0.46, -0.33] | yes | descriptive |
| 51h | attention | 321 / 145 | 0.34 [-0.06, 0.85], p 0.073 | 0.54 [-0.96, 2.09], p 0.216; W1* q95 -0.37, p 0.002 | 0.04, p 0.059 | 0.93, DB p 0.955 | λ̂ 4.00, b̂ 0.0; return share 0.68 | -0.79 [-0.95, -0.63] | yes | descriptive |
| 51h | work | 59 / 20 | 0.62 [-0.51, 2.56], p 0.256 | -0.85 [-4.17, 2.77], p 0.711; W1* q95 1.69, p 0.446 | 0.05, p 0.311 | 0.35, DB p 0.787 | λ̂ 1.50, b̂ 4.5; return share 0.54 | -0.27 [-0.45, -0.09] | no | descriptive |
| 51i | attention | 120 / 67 | 0.00 [-1.22, 0.65], p 0.589 | -0.38 [-3.29, 0.96], p 0.651; W1* q95 1.45, p 0.698 | -0.02, p 0.693 | 0.82, DB p 0.433 | λ̂ -1.00, b̂ 2.0; return share 0.52 | -1.31 [-1.62, -1.00] | yes | descriptive |
| 51i | work | 34 / 8 | 0.85 [0.00, 2.20], p 0.502 | -0.76 [-2.56, 2.20], p 0.750; W1* q95 –, p – | 0.06, p 0.379 | 0.30, DB p 0.411 | λ̂ –, b̂ –; return share 0.59 | -0.30 [-0.53, -0.06] | no | descriptive |
| 51j | attention | 130 / 58 | -0.42 [-1.15, 0.17], p 0.947 | 0.40 [-0.94, 2.38], p 0.291; W1* q95 1.66, p 0.362 | -0.03, p 0.833 | 0.78, DB p 0.473 | λ̂ -1.00, b̂ 3.0; return share 0.56 | -1.13 [-1.40, -0.86] | yes | descriptive |
| 51j | work | 31 / 11 | 0.85 [0.00, 2.20], p 0.247 | 2.21 [-1.61, 6.59], p 0.247; W1* q95 3.38, p 0.125 | 0.03, p 0.505 | 0.40, DB p 0.249 | λ̂ 0.00, b̂ 3.0; return share 0.48 | -0.28 [-0.58, 0.01] | no | descriptive |
| 51k | attention | 82 / 35 | 0.00 [-1.10, 1.10], p 0.651 | -0.86 [-3.68, 1.55], p 0.781; W1* q95 2.08, p 0.763 | -0.02, p 0.748 | 0.57, DB p 0.388 | λ̂ -1.00, b̂ 3.0; return share 0.49 | -1.18 [-1.61, -0.75] | yes | descriptive |
| 51k | work | 7 / 0 | 0.00 [0.00, 0.00], p 1.000 | 0.00 [0.00, 0.00], p 1.000; W1* q95 –, p – | 0.14, p 0.506 | 0.00, DB p 1.000 | λ̂ –, b̂ –; return share 0.43 | – | no | descriptive |
| 51l | attention | 99 / 40 | 1.42 [0.75, 2.84], p 0.008 | 2.57 [0.81, 5.29], p 0.024; W1* q95 2.54, p 0.052 | 0.13, p 0.039 | 0.70, DB p 0.358 | λ̂ 0.75, b̂ 4.5; return share 0.59 | -1.11 [-1.50, -0.73] | yes | descriptive |
| 51l | work | 10 / 1 | 0.00 [0.00, 0.00], p 1.000 | 1.10 [0.00, 1.95], p 0.513; W1* q95 –, p – | 0.00, p 0.680 | 0.00, DB p 0.686 | λ̂ –, b̂ –; return share 0.50 | – | no | descriptive |

Synthetic on this period's skeleton (A1): 𝒜_cyc false-positive max 0.075, power at κ = 2 0.55.
Own-role units (private goals): no HH prediction. 2/12 work units are triple-testable (51f, 51g); 12/12 attention units. Attention 51c (𝒜_cyc 1.47, reversal p 0.014, W1* p 0.002) and 51l (2.57; 0.024; 0.052) exceed the nulls; with 14 own-role tests, about one such hit is expected by chance. Pooled over the 12 attention units (DerSimonian–Laird, exception (d)): A_3 0.21 [−0.00, 0.43], 𝒜_cyc 0.16 [−0.32, 0.64], m_2 0.023 [−0.001, 0.046]. Dwell hazards age in every testable unit (work γ −0.27 to −0.41; attention −0.79 to −1.58).

Data: `data/processed/H129-project-cycle-currents/G51/`.

## Scorecard (period-specific axes)
- **C:** reversal null, detailed-balance null, calibrated age walker.
- **D:** dwell shape and return share are unfitted by the triple statistics.
- **F:** see the synthetic line above.

## Notes
- 2026-10-04 22:19 UTC: folder and prediction written before any H129 statistic on this period.
- 2026-10-04 23:15 UTC: result filled (verdict descriptive).
