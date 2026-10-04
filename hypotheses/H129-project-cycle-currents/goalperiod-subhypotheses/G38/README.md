# H129 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 04-24)

**Verdict:** failed
**Role:** exploratory (replication, native N2)
**Period:** regime III · mode C · 12–14 agents · #best/#rest · 17 days. Shared-goal code: shared.

## Why this period
Seventeen days, the most repos (35) and births of any shared week: native N2, the strongest age drift.

## Prediction
*Written 2026-10-04 22:19 UTC, before running H129 on this period.*
- Shared-goal week. HH370 (card P1): A_3 > 0 beyond the per-agent reversal null (one-sided p < 0.05); card P2: 𝒜_cyc > 0 beyond the reversal null and the age walker W1*'s 95th percentile.
- Card P4: m_2 > 0 (net flow to newer projects), reversal p < 0.05. Card P5a: dwell hazard slope γ CI ∋ 0.
- My expectation: m_2 > 0 and A_3 > 0 (age drift); 𝒜_cyc inside W1*'s band (no circulation beyond age).
- Verdict rule (per channel, work primary): supported if 𝒜_cyc passes both nulls; mixed if A_3 passes the reversal null but 𝒜_cyc does not beat W1*; failed if A_3 is inside the reversal null (HH370's kill); descriptive if untestable (< 20 age-ordered triples).
- Native N2 (credence 0.5): m_2 > 0 with reversal p < 0.05 and 𝒜_cyc inside W1*'s band.

## Result
*Run 2026-10-04 23:15 UTC (`scheme/build.py`, `analysis/run.py`; non-holdout days).* Work channel primary. p values one-sided; reversal null = per-agent sequence flips (2,000); W1* = age walker calibrated to m_2 and the return share (400 runs).

| Unit | Channel | Hops / triples | A_3 [boot] , reversal p | 𝒜_cyc [boot], reversal p; W1* | m_2, reversal p | κ_c, DB p | W1* calibration | dwell slope γ [95%] | testable | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G38 | work | 87 / 53 | 0.66 [-0.11, 1.42], p 0.098 | 0.46 [-1.52, 2.89], p 0.335; W1* q95 1.49, p 0.269 | 0.17, p 0.027 | 0.72, DB p 0.175 | λ̂ 0.75, b̂ 0.0; return share 0.40 | -0.24 [-0.41, -0.06] | yes | failed |
| G38 | attention | 265 / 136 | 0.55 [-0.80, 1.30], p 0.463 | -0.26 [-3.00, 1.48], p 0.569; W1* q95 1.02, p 0.628 | 0.07, p 0.432 | 0.85, DB p 0.388 | λ̂ 0.75, b̂ 2.0; return share 0.58 | -0.86 [-1.01, -0.71] | yes | failed |

Synthetic on this period's skeleton (A1): 𝒜_cyc false-positive max 0.025, power at κ = 2 0.93.
Native N2: work m_2 0.17 (reversal p 0.027): a net flow to newer repos, the excess the card expected; 𝒜_cyc 0.46 sits inside the calibrated age walker (p 0.27; W1* λ̂ 0.75, b̂ 0). Attention m_2 0.07 (p 0.43). N2 holds on the primary (work) channel. Dwell hazards age (γ −0.24 work, −0.86 attention, CI < 0).

Data: `data/processed/H129-project-cycle-currents/G38/`.

## Scorecard (period-specific axes)
- **C:** reversal null, detailed-balance null, calibrated age walker.
- **D:** dwell shape and return share are unfitted by the triple statistics.
- **F:** see the synthetic line above.

## Notes
- 2026-10-04 22:19 UTC: folder and prediction written before any H129 statistic on this period.
- 2026-10-04 23:15 UTC: result filled (verdict failed).
