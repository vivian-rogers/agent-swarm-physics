# H129 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 03-20)

**Verdict:** descriptive
**Role:** exploratory (replication, native N1)
**Period:** regime II · mode C · 12 agents · #best/#rest · 5 days. Shared-goal code: shared.

## Why this period
Fixed set: the #34 game's few repos, almost no births. Native N1: the reversible (fixed-attractiveness) control.

## Prediction
*Written 2026-10-04 22:19 UTC, before running H129 on this period.*
- Shared-goal week. HH370 (card P1): A_3 > 0 beyond the per-agent reversal null (one-sided p < 0.05); card P2: 𝒜_cyc > 0 beyond the reversal null and the age walker W1*'s 95th percentile.
- Card P4: m_2 > 0 (net flow to newer projects), reversal p < 0.05. Card P5a: dwell hazard slope γ CI ∋ 0.
- My expectation: m_2 > 0 and A_3 > 0 (age drift); 𝒜_cyc inside W1*'s band (no circulation beyond age).
- Verdict rule (per channel, work primary): supported if 𝒜_cyc passes both nulls; mixed if A_3 passes the reversal null but 𝒜_cyc does not beat W1*; failed if A_3 is inside the reversal null (HH370's kill); descriptive if untestable (< 20 age-ordered triples).
- Native N1 (credence 0.7): A_3, 𝒜_cyc and m_2 inside the reversal null; C_2 inside the DB null or untestable.

## Result
*Run 2026-10-04 23:15 UTC (`scheme/build.py`, `analysis/run.py`; non-holdout days).* Work channel primary. p values one-sided; reversal null = per-agent sequence flips (2,000); W1* = age walker calibrated to m_2 and the return share (400 runs).

| Unit | Channel | Hops / triples | A_3 [boot] , reversal p | 𝒜_cyc [boot], reversal p; W1* | m_2, reversal p | κ_c, DB p | W1* calibration | dwell slope γ [95%] | testable | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G35 | work | 2 | – | – | – | – | – | – | – | descriptive |
| G35 | attention | 15 / 0 | 0.00 [0.00, 0.00], p 1.000 | 0.00 [0.00, 0.00], p 1.000; W1* q95 –, p – | 0.07, p 0.499 | 0.44, DB p 0.737 | λ̂ –, b̂ –; return share 0.47 | – | no | descriptive |

No period-specific synthetic skeleton; nearest-size skeletons (A1) give 𝒜_cyc power 0.55–0.62 at κ = 2 for 59–120 hops.
Native N1 (fixed set): the work channel has 2 hops (3 repos, no births) and the attention channel 15 hops with no age-ordered triple. Every statistic sits inside its null (A_3 = 𝒜_cyc = 0, reversal p = 1.00; m_2 0.07, p 0.50; DB p 0.74), but nothing is testable: descriptive, consistent with a reversible fixed landscape.

Data: `data/processed/H129-project-cycle-currents/G35/`.

## Scorecard (period-specific axes)
- **C:** reversal null, detailed-balance null, calibrated age walker.
- **D:** dwell shape and return share are unfitted by the triple statistics.
- **F:** see the synthetic line above.

## Notes
- 2026-10-04 22:19 UTC: folder and prediction written before any H129 statistic on this period.
- 2026-10-04 23:15 UTC: result filled (verdict descriptive).
