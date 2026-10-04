# H79 × G31: Free week (farewell to Claude 3.7 Sonnet) (2026-02-16 → 02-20)

**Verdict:** mixed
**Role:** replication
**Period:** regime I · N 11–12 · #general · 5 days · 1,324 agent work commits, 1,345 automated commits (one stream).

## Why this period
The first period with an automated stream, and a field-free herding wave onto one repo. NE29 (a retirement) sits inside it.

## Prediction
*Written 2026-10-04, before running on this period (card P1–P5, amendments A1–A2).*
- P1: maxRAF coverage ≤ 20% of agent work commits.
- P2: no irrRAF of size ≥ 3 beyond the rewired null (support ≥ 3 cycles: S3 = 0, or rewired p ≥ 0.05).
- P3: self-catalysed reactions carry ≥ 50% of maxRAF commits (automated included); in-period tools catalysing other repos carry ≤ 5% of agent work commits.
- P4: real catalysed coverage / time-reversed catalysed coverage > 1 (day-bootstrap CI excludes 1).
- P5: maxCAF ≥ 90% of maxRAF commits.

## Result
Data: `data/processed/H79-artifact-autocatalytic-set/results/G31.json`; pipeline `analysis/run.py --period G31`; events from `scheme/build.py`.

| Prediction | Observed (95% CI) | Null | Verdict |
| --- | --- | --- | --- |
| P1 coverage ≤ 20% | 0.395 [0.238, 0.531] of 1,324 agent work commits | rewired 0.395 | failed |
| P2 no supported ≥3 cycles | 0 (one supported 2-cycle) | rewired mean 0 | supported |
| P3a self ≥ 50% of maxRAF commits | 0.849 | – | supported |
| P3b in-period tools ≤ 5% | 0.211 | rewired 0.195 (p 0.04) | failed |
| P4 exec before/after > 1 | 0.855 [0.640, 1.003] | 1 | failed |
| P5 maxCAF ≥ 90% | 0.911 | – | supported |

Regime I. The herding wave puts many agents into one in-period repo's working directory; part of the 21% "in-period tool" share is likely cwd mis-resolution across repos (cwd precision 0.89).

## Scorecard (period-specific axes)
- C: 0. Coverage and in-period share equal the rewired null to within 0.02.
- D: 1. P2, P3a, P5 hold; P1, P3b, P4 fail.

## Notes
- 2026-10-04: round 1 run (exploratory replication).
