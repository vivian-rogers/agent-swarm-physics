# H79 × G41: Novel research (NE42 split back) (2026-05-11 → 05-15)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · N 15 · #best / #rest · 5 days · 1,812 agent work commits, 858 automated commits (one stream, one day).

## Why this period
Individual research projects with automation: many small tools that could catalyse each other.

## Prediction
*Written 2026-10-04, before running on this period (card P1–P5, amendments A1–A2).*
- P1: maxRAF coverage ≤ 20% of agent work commits.
- P2: no irrRAF of size ≥ 3 beyond the rewired null (support ≥ 3 cycles: S3 = 0, or rewired p ≥ 0.05).
- P3: self-catalysed reactions carry ≥ 50% of maxRAF commits (automated included); in-period tools catalysing other repos carry ≤ 5% of agent work commits.
- P4: real catalysed coverage / time-reversed catalysed coverage > 1 (day-bootstrap CI excludes 1).
- P5: maxCAF ≥ 90% of maxRAF commits.

## Result
Data: `data/processed/H79-artifact-autocatalytic-set/results/G41.json`; pipeline `analysis/run.py --period G41`; events from `scheme/build.py`.

| Prediction | Observed (95% CI) | Null | Verdict |
| --- | --- | --- | --- |
| P1 coverage ≤ 20% | 0.349 [0.285, 0.398] of 1,812 | rewired 0.349 | failed |
| P2 no supported ≥3 cycles | 0 | rewired 0 | supported |
| P3a self ≥ 50% | 0.989 (858 automated commits in one self-reaction) | – | supported |
| P3b in-period tools ≤ 5% | 0.010 | rewired 0.008 | supported |
| P4 exec before/after > 1 | 0.875 [0.774, 0.995] | 1 | failed (reversed) |
| P5 maxCAF ≥ 90% | 0.752 | – | failed |

## Scorecard (period-specific axes)
- C: 0 (coverage = null). D: 1. G: 1 (the one automated stream is one self-reaction).

## Notes
- 2026-10-04: round 1 run (exploratory replication).
