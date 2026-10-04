# H129 × G33: Discuss, debate, and act on your views about the Pentagon-AI news (2026-03-02 → 03-04)

**Verdict:** descriptive
**Role:** exploratory (replication)
**Period:** regime II · mode C · 11 agents · #general · 3 days. Shared-goal code: shared.

## Why this period
Short shared week (3 days).

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
| G33 | work | 24 / 4 | 1.95 [0.00, 2.94], p 0.496 | 0.85 [-1.95, 2.94], p 0.496; W1* q95 –, p – | 0.17, p 0.371 | 0.17, DB p 0.754 | λ̂ –, b̂ –; return share 0.42 | 0.69 [0.11, 1.28] | no | descriptive |
| G33 | attention | 32 / 6 | 2.20 [0.00, 3.05], p 0.237 | 2.20 [-1.61, 4.89], p 0.355; W1* q95 0.78, p 0.002 | 0.06, p 0.480 | 0.83, DB p 0.687 | λ̂ 0.00, b̂ 4.5; return share 0.50 | 0.18 [-0.27, 0.64] | no | descriptive |

No period-specific synthetic skeleton; nearest-size skeletons (A1) give 𝒜_cyc power 0.55–0.62 at κ = 2 for 59–120 hops.


Data: `data/processed/H129-project-cycle-currents/G33/`.

## Scorecard (period-specific axes)
- **C:** reversal null, detailed-balance null, calibrated age walker.
- **D:** dwell shape and return share are unfitted by the triple statistics.
- **F:** see the synthetic line above.

## Notes
- 2026-10-04 22:19 UTC: folder and prediction written before any H129 statistic on this period.
- 2026-10-04 23:15 UTC: result filled (verdict descriptive).
