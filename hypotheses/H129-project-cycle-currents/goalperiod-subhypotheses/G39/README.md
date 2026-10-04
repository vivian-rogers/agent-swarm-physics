# H129 × G39: Build your own interactive world! (2026-04-27 → 05-01)

**Verdict:** descriptive
**Role:** exploratory (replication)
**Period:** regime III · mode I · 15 agents · #best/#rest · 5 days. Shared-goal code: own-role.

## Why this period
Own-role week (own world): hops should be rare and mostly births of the agent's own repos.

## Prediction
*Written 2026-10-04 22:19 UTC, before running H129 on this period.*
- Own-role week: HH370 predicts circulation in shared-goal weeks only. Card P6: |𝒜_cyc| and the hop rate lower than in shared-goal units.
- Card P4 still applies: m_2 > 0 (new own repos are born and joined). Card P5a/b: geometric dwell; low hop rate (high habit).
- Verdict rule: descriptive (no HH prediction for own-role weeks); numbers reported for P4–P6.

## Result
*Run 2026-10-04 23:15 UTC (`scheme/build.py`, `analysis/run.py`; non-holdout days).* Work channel primary. p values one-sided; reversal null = per-agent sequence flips (2,000); W1* = age walker calibrated to m_2 and the return share (400 runs).

| Unit | Channel | Hops / triples | A_3 [boot] , reversal p | 𝒜_cyc [boot], reversal p; W1* | m_2, reversal p | κ_c, DB p | W1* calibration | dwell slope γ [95%] | testable | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G39 | work | 8 / 1 | 0.00 [0.00, 0.00], p 1.000 | -1.10 [-1.95, 0.00], p 1.000; W1* q95 –, p – | 0.00, p 1.000 | –, DB p 1.000 | λ̂ –, b̂ –; return share 0.50 | – | no | descriptive |
| G39 | attention | 63 / 26 | 0.00 [-0.79, 1.61], p 0.609 | 0.59 [-2.74, 4.44], p 0.372; W1* q95 2.21, p 0.359 | 0.02, p 0.484 | 0.94, DB p 0.816 | λ̂ 0.00, b̂ 3.0; return share 0.62 | -1.04 [-1.34, -0.74] | yes | descriptive |

No period-specific synthetic skeleton; nearest-size skeletons (A1) give 𝒜_cyc power 0.55–0.62 at κ = 2 for 59–120 hops.


Data: `data/processed/H129-project-cycle-currents/G39/`.

## Scorecard (period-specific axes)
- **C:** reversal null, detailed-balance null, calibrated age walker.
- **D:** dwell shape and return share are unfitted by the triple statistics.
- **F:** see the synthetic line above.

## Notes
- 2026-10-04 22:19 UTC: folder and prediction written before any H129 statistic on this period.
- 2026-10-04 23:15 UTC: result filled (verdict descriptive).
