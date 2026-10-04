# H129 × G44: Finetune your leader! (2026-05-26 → 05-29)

**Verdict:** failed
**Role:** exploratory (replication, native N3)
**Period:** regime III · mode C · 17–18 agents · #best (named leader) / #rest (free) · 4 days. Shared-goal code: shared.

## Why this period
Two rooms: #best (assigned team, named leader) vs #rest (free). Native N3: an assigned field should turn hops into one-way flow (excess).

## Prediction
*Written 2026-10-04 22:19 UTC, before running H129 on this period.*
- Shared-goal week. HH370 (card P1): A_3 > 0 beyond the per-agent reversal null (one-sided p < 0.05); card P2: 𝒜_cyc > 0 beyond the reversal null and the age walker W1*'s 95th percentile.
- Card P4: m_2 > 0 (net flow to newer projects), reversal p < 0.05. Card P5a: dwell hazard slope γ CI ∋ 0.
- My expectation: m_2 > 0 and A_3 > 0 (age drift); 𝒜_cyc inside W1*'s band (no circulation beyond age).
- Verdict rule (per channel, work primary): supported if 𝒜_cyc passes both nulls; mixed if A_3 passes the reversal null but 𝒜_cyc does not beat W1*; failed if A_3 is inside the reversal null (HH370's kill); descriptive if untestable (< 20 age-ordered triples).
- Native N3 (credence 0.4): #best's cycle share κ_c below #rest's; #best's net flow concentrated into its assigned repo (excess).

## Result
*Run 2026-10-04 23:15 UTC (`scheme/build.py`, `analysis/run.py`; non-holdout days).* Work channel primary. p values one-sided; reversal null = per-agent sequence flips (2,000); W1* = age walker calibrated to m_2 and the return share (400 runs).

| Unit | Channel | Hops / triples | A_3 [boot] , reversal p | 𝒜_cyc [boot], reversal p; W1* | m_2, reversal p | κ_c, DB p | W1* calibration | dwell slope γ [95%] | testable | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G44 | work | 67 / 32 | 1.10 [0.00, 3.22], p 0.070 | 0.71 [-2.54, 4.57], p 0.342; W1* q95 1.85, p 0.269 | 0.13, p 0.041 | 0.47, DB p 0.108 | λ̂ 2.50, b̂ 3.0; return share 0.46 | -0.18 [-0.35, 0.00] | yes | failed |
| G44 | attention | 156 / 89 | 1.17 [0.60, 1.61], p 0.006 | 0.28 [-1.10, 1.27], p 0.328; W1* q95 1.31, p 0.227 | 0.17, p 0.001 | 0.83, DB p 0.831 | λ̂ 4.00, b̂ 3.0; return share 0.48 | -0.56 [-0.85, -0.27] | yes | mixed |
| G44best | work | 16 / 1 | 0.00 [0.00, 0.00], p 1.000 | -1.10 [-1.95, 0.00], p 1.000; W1* q95 –, p – | 0.00, p 0.751 | 0.00, DB p 0.930 | λ̂ –, b̂ –; return share 0.69 | – | no | descriptive |
| G44rest | work | 51 / 31 | 1.10 [0.20, 3.14], p 0.080 | 0.84 [-2.19, 4.55], p 0.329; W1* q95 1.73, p 0.187 | 0.18, p 0.033 | 0.51, DB p 0.092 | λ̂ 4.00, b̂ 2.0; return share 0.39 | -0.15 [-0.36, 0.06] | yes | failed |
| G44best | attention | 34 / 10 | 0.34 [-1.61, 1.61], p 0.475 | -1.78 [-4.39, 0.96], p 0.801; W1* q95 3.63, p 0.838 | 0.00, p 0.744 | 0.81, DB p 0.979 | λ̂ -1.00, b̂ 1.0; return share 0.68 | -0.14 [-0.69, 0.40] | no | descriptive |
| G44rest | attention | 122 / 79 | 1.30 [0.80, 1.89], p 0.006 | 0.57 [-0.83, 1.60], p 0.195; W1* q95 1.65, p 0.314 | 0.21, p 0.001 | 0.83, DB p 0.512 | λ̂ -1.00, b̂ 2.0; return share 0.43 | -0.62 [-0.97, -0.27] | yes | mixed |

Synthetic on this period's skeleton (A1): 𝒜_cyc false-positive max 0.025, power at κ = 2 0.57.
Native N3 (rooms): #best's work hops form a tree (cycle share κ_c ≈ 0, m_2 0.00, few hops); #rest κ_c 0.51, m_2 0.18 (p 0.03). Attention: κ_c 0.81 vs 0.83. N3 holds by the letter on both channels, but #best has too few hops for a triple test (mixed).

Data: `data/processed/H129-project-cycle-currents/G44/`.

## Scorecard (period-specific axes)
- **C:** reversal null, detailed-balance null, calibrated age walker.
- **D:** dwell shape and return share are unfitted by the triple statistics.
- **F:** see the synthetic line above.

## Notes
- 2026-10-04 22:19 UTC: folder and prediction written before any H129 statistic on this period.
- 2026-10-04 23:15 UTC: result filled (verdict failed).
