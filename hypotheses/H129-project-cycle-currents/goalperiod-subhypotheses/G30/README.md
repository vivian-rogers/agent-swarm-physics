# H129 × G30: Adopt a park and get it cleaned! (2026-02-09 → 02-13)

**Verdict:** descriptive
**Role:** exploratory (replication)
**Period:** regime I · mode C · 11 agents · #general · 5 days. Shared-goal code: shared.

## Why this period
Shared objective; very few repos (H93: 2), so triples may be untestable (a two-state chain carries no cycle).

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
| G30 | work | 35 / 0 | 0.00 [0.00, 0.00], p 1.000 | 0.00 [0.00, 0.00], p 1.000; W1* q95 –, p – | 0.03, p 0.503 | 0.00, DB p 1.000 | λ̂ –, b̂ –; return share 0.77 | 0.39 [-0.11, 0.90] | no | descriptive |
| G30 | attention | 148 / 43 | 2.83 [1.61, 3.43], p 0.037 | 5.46 [3.00, 7.13], p 0.037; W1* q95 3.50, p 0.007 | 0.07, p 0.020 | 0.96, DB p 0.220 | λ̂ -1.00, b̂ 0.0; return share 0.80 | -0.29 [-0.56, -0.01] | no | descriptive |

No period-specific synthetic skeleton; nearest-size skeletons (A1) give 𝒜_cyc power 0.55–0.62 at κ = 2 for 59–120 hops.


Data: `data/processed/H129-project-cycle-currents/G30/`.

## Scorecard (period-specific axes)
- **C:** reversal null, detailed-balance null, calibrated age walker.
- **D:** dwell shape and return share are unfitted by the triple statistics.
- **F:** see the synthetic line above.

## Notes
- 2026-10-04 22:19 UTC: folder and prediction written before any H129 statistic on this period.
- 2026-10-04 23:15 UTC: result filled (verdict descriptive).
