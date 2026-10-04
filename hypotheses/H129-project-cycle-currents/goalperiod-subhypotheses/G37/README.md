# H129 × G37: Pick your own goal! (2026-03-30 → 04-01)

**Verdict:** failed
**Role:** exploratory (replication)
**Period:** regime III · mode F · 12 agents · #best/#rest (identical kickoff) · 3 days. Shared-goal code: shared.

## Why this period
Free shared week, two rooms, 14 repos in 3 days.

## Prediction
*Written 2026-10-04 22:19 UTC, before running H129 on this period.*
- Shared-goal week. HH370 (card P1): A_3 > 0 beyond the per-agent reversal null (one-sided p < 0.05); card P2: 𝒜_cyc > 0 beyond the reversal null and the age walker W1*'s 95th percentile.
- Card P4: m_2 > 0 (net flow to newer projects), reversal p < 0.05. Card P5a: dwell hazard slope γ CI ∋ 0.
- My expectation: m_2 > 0 and A_3 > 0 (age drift); 𝒜_cyc inside W1*'s band (no circulation beyond age).
- Verdict rule (per channel, work primary): supported if 𝒜_cyc passes both nulls; mixed if A_3 passes the reversal null but 𝒜_cyc does not beat W1*; failed if A_3 is inside the reversal null (HH370's kill); descriptive if untestable (< 20 age-ordered triples).

## Result
*Run 2026-10-04 23:15 UTC (`scheme/build.py`, `analysis/run.py`; non-holdout days).* Work channel primary. p values one-sided; reversal null = per-agent sequence flips (2,000); W1* = age walker calibrated to m_2 and the return share (400 runs).

| Unit | Channel | Hops / triples | A_3 [boot] , reversal p | 𝒜_cyc [boot], reversal p; W1* | m_2, reversal p | κ_c, DB p | W1* calibration | dwell slope γ [95%] | testable | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G37 | work | 21 / 11 | 0.85 [0.00, 2.20], p 0.236 | 0.51 [-2.40, 3.56], p 0.364; W1* q95 –, p – | -0.05, p 0.806 | 0.21, DB p 0.883 | λ̂ –, b̂ –; return share 0.19 | – | no | descriptive |
| G37 | attention | 97 / 66 | 1.05 [-0.55, 2.71], p 0.177 | 1.03 [-2.23, 3.92], p 0.262; W1* q95 2.69, p 0.329 | 0.13, p 0.247 | 0.74, DB p 0.482 | λ̂ 1.50, b̂ 3.0; return share 0.36 | -0.63 [-1.05, -0.21] | yes | failed |

No period-specific synthetic skeleton; nearest-size skeletons (A1) give 𝒜_cyc power 0.55–0.62 at κ = 2 for 59–120 hops.
Work channel untestable; the verdict is the attention channel's.

Data: `data/processed/H129-project-cycle-currents/G37/`.

## Scorecard (period-specific axes)
- **C:** reversal null, detailed-balance null, calibrated age walker.
- **D:** dwell shape and return share are unfitted by the triple statistics.
- **F:** see the synthetic line above.

## Notes
- 2026-10-04 22:19 UTC: folder and prediction written before any H129 statistic on this period.
- 2026-10-04 23:15 UTC: result filled (verdict failed).
