# H129 × G41: Perform novel research! (2026-05-11 → 05-15)

**Verdict:** failed
**Role:** exploratory (replication)
**Period:** regime III · mode I · 15 agents · #best/#rest · 5 days. Shared-goal code: shared.

## Why this period
Free shared week (novel research), 21 repos.

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
| G41 | work | 59 / 35 | 1.73 [0.62, 3.14], p 0.063 | 1.73 [-0.69, 4.21], p 0.063; W1* q95 2.12, p 0.085 | 0.12, p 0.098 | 0.51, DB p 0.708 | λ̂ 1.50, b̂ 0.0; return share 0.31 | -0.35 [-0.57, -0.13] | no | descriptive |
| G41 | attention | 114 / 63 | 0.21 [-0.45, 1.17], p 0.437 | 0.35 [-1.48, 2.06], p 0.423; W1* q95 1.70, p 0.399 | -0.04, p 0.832 | 0.77, DB p 0.702 | λ̂ 0.00, b̂ 1.0; return share 0.48 | -0.97 [-1.22, -0.72] | yes | failed |

Synthetic on this period's skeleton (A1): 𝒜_cyc false-positive max 0.125, power at κ = 2 0.80.
Work channel untestable; the verdict is the attention channel's.

Data: `data/processed/H129-project-cycle-currents/G41/`.

## Scorecard (period-specific axes)
- **C:** reversal null, detailed-balance null, calibrated age walker.
- **D:** dwell shape and return share are unfitted by the triple statistics.
- **F:** see the synthetic line above.

## Notes
- 2026-10-04 22:19 UTC: folder and prediction written before any H129 statistic on this period.
- 2026-10-04 23:15 UTC: result filled (verdict failed).
