# H129 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 05-08)

**Verdict:** descriptive
**Role:** exploratory (replication)
**Period:** regime III · mode C · 15 agents · #universe-coordination (NE42 merge) · 5 days. Shared-goal code: shared.

## Why this period
Shared target (connect the worlds) after the NE42 merge: flows into a hub.

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
| G40 | work | 15 / 0 | 0.00 [0.00, 0.00], p 1.000 | 0.00 [0.00, 0.00], p 1.000; W1* q95 –, p – | 0.07, p 0.505 | 0.00, DB p 0.980 | λ̂ –, b̂ –; return share 0.60 | – | no | descriptive |
| G40 | attention | 50 / 5 | 0.00 [0.00, 0.00], p 1.000 | 0.51 [0.00, 1.95], p 0.494; W1* q95 –, p – | 0.04, p 0.342 | 0.22, DB p 0.611 | λ̂ –, b̂ –; return share 0.74 | -1.30 [-1.66, -0.94] | no | descriptive |

No period-specific synthetic skeleton; nearest-size skeletons (A1) give 𝒜_cyc power 0.55–0.62 at κ = 2 for 59–120 hops.


Data: `data/processed/H129-project-cycle-currents/G40/`.

## Scorecard (period-specific axes)
- **C:** reversal null, detailed-balance null, calibrated age walker.
- **D:** dwell shape and return share are unfitted by the triple statistics.
- **F:** see the synthetic line above.

## Notes
- 2026-10-04 22:19 UTC: folder and prediction written before any H129 statistic on this period.
- 2026-10-04 23:15 UTC: result filled (verdict descriptive).
