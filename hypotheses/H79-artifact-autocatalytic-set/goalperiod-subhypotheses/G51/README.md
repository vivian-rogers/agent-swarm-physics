# H79 × G51: Maximize your private assigned role (2026-07-06 → 2026-09-04, non-holdout)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · N 21 → 32 · one room (+ #focus) · 45 non-holdout days · 48,087 agent work commits, 54,892 automated commits (the GPT-5 cron stream and others).

## Why this period
The densest git period, with the HH244 automata. If an artifact layer sustains itself anywhere, it is here: 45 days, 134 new repos and many in-period tools.

## Prediction
*Written 2026-10-04, before running on this period (card P1–P5, amendments A1–A2).*
- P1: maxRAF coverage ≤ 20% of agent work commits.
- P2: no irrRAF of size ≥ 3 beyond the rewired null (support ≥ 3 cycles: S3 = 0, or rewired p ≥ 0.05).
- P3: self-catalysed reactions carry ≥ 50% of maxRAF commits (automated included); in-period tools catalysing other repos carry ≤ 5% of agent work commits.
- P4: real catalysed coverage / time-reversed catalysed coverage > 1 (day-bootstrap CI excludes 1).
- P5: maxCAF ≥ 90% of maxRAF commits.

## Result
Data: `data/processed/H79-artifact-autocatalytic-set/results/G51.json`; pipeline `analysis/run.py --period G51`; events from `scheme/build.py`.

| Prediction | Observed (95% CI) | Null | Verdict |
| --- | --- | --- | --- |
| P1 coverage ≤ 20% | 0.210 [0.185, 0.236] of 48,087 agent work commits (strict reactants 0.128) | rewired 0.218 | failed (marginal) |
| P2 no supported ≥3 cycles | 0 cycles of length ≥ 3 with ≥ 3 events per edge; two supported 2-cycles (each between repos of 2 different makers) | rewired mean 27.3; real is **below** it (p_low 0.01) | supported |
| P3a self ≥ 50% of maxRAF commits | 0.969 (automated included) | – | supported |
| P3b in-period tools ≤ 5% | 0.037 | rewired 0.036 (p 0.14) | supported |
| P4 exec before/after > 1 | 0.858 [0.840, 0.875] | 1 | failed (reversed) |
| P5 maxCAF ≥ 90% of maxRAF | 0.086 (the in-period cron stream needs an agent bootstrap) | – | failed |

Unweighted cycles (any support): 51 of length 3–6 vs 1,954 in the rewired null. 14,512 agent events; 214 reactions, 178 in the maxRAF; food 2,790 artifacts. Catalysed share = maxRAF coverage up to 0.03: closure barely binds.

## Scorecard (period-specific axes)
- C (adequacy): 1. The cycle count sits below the rewired null (p_low 0.01); coverage equals the null (topology adds nothing).
- D (unfitted): 1. P2 and P3 hold; P4 reversed; P5 fails.
- G (known structure): 1. The HH244 cron stream appears as one self-catalysed reaction with 54,892 commits.

## Notes
- 2026-10-04: round 1 run (exploratory replication).
