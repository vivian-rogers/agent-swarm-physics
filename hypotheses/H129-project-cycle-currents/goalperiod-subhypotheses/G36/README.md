# H129 × G36: Interact with other AI agents outside the Village! (2026-03-23 → 03-27)

**Verdict:** failed
**Role:** exploratory (replication)
**Period:** regime II→III · mode C · 12 agents · #best/#rest · 5 days. Shared-goal code: shared.

## Why this period
Shared objective, 16 repos, regime boundary inside (03-24).

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
| G36 | work | 53 / 27 | 0.45 [-0.51, 1.95], p 0.301 | 0.70 [-1.92, 2.53], p 0.257; W1* q95 3.17, p 0.454 | 0.06, p 0.319 | 0.71, DB p 0.524 | λ̂ -1.00, b̂ 1.0; return share 0.49 | 0.18 [-0.24, 0.61] | no | descriptive |
| G36 | attention | 208 / 127 | 0.50 [-0.06, 1.07], p 0.085 | -0.67 [-1.91, 0.69], p 0.813; W1* q95 1.29, p 0.850 | 0.07, p 0.051 | 0.91, DB p 0.587 | λ̂ 0.00, b̂ 2.0; return share 0.60 | -0.62 [-0.88, -0.35] | yes | failed |

No period-specific synthetic skeleton; nearest-size skeletons (A1) give 𝒜_cyc power 0.55–0.62 at κ = 2 for 59–120 hops.
Work channel untestable; the verdict is the attention channel's.

Data: `data/processed/H129-project-cycle-currents/G36/`.

## Scorecard (period-specific axes)
- **C:** reversal null, detailed-balance null, calibrated age walker.
- **D:** dwell shape and return share are unfitted by the triple statistics.
- **F:** see the synthetic line above.

## Notes
- 2026-10-04 22:19 UTC: folder and prediction written before any H129 statistic on this period.
- 2026-10-04 23:15 UTC: result filled (verdict failed).
