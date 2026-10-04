# H129 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 02-20)

**Verdict:** mixed
**Role:** exploratory (replication)
**Period:** regime I · mode F · 11–12 agents · #general · 5 days. Shared-goal code: shared.

## Why this period
Regime-I free shared week with many repos (H93: 24) and births: the age drift and any circulation should show.

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
| G31 | work | 120 / 89 | 1.13 [0.58, 1.99], p 0.002 | 0.53 [-0.82, 2.06], p 0.270; W1* q95 1.44, p 0.262 | 0.17, p 0.005 | 0.93, DB p 0.099 | λ̂ 0.75, b̂ 0.0; return share 0.38 | 0.00 [-0.17, 0.17] | yes | mixed |
| G31 | attention | 219 / 168 | 0.50 [0.21, 0.88], p 0.007 | 0.14 [-0.30, 0.76], p 0.301; W1* q95 1.06, p 0.446 | 0.10, p 0.003 | 0.95, DB p 0.017 | λ̂ 0.00, b̂ 0.0; return share 0.44 | -0.45 [-0.74, -0.16] | yes | mixed |

Synthetic on this period's skeleton (A1): 𝒜_cyc false-positive max 0.025, power at κ = 2 0.62.


Data: `data/processed/H129-project-cycle-currents/G31/`.

## Scorecard (period-specific axes)
- **C:** reversal null, detailed-balance null, calibrated age walker.
- **D:** dwell shape and return share are unfitted by the triple statistics.
- **F:** see the synthetic line above.

## Notes
- 2026-10-04 22:19 UTC: folder and prediction written before any H129 statistic on this period.
- 2026-10-04 23:15 UTC: result filled (verdict mixed).
