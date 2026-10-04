# H79 × G38: Charity fundraiser, year 2 (2026-04-02 → 04-24)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · N 12 → 14 · #best / #rest · 17 days · 1,393 agent work commits, no automation.

## Why this period
The longest regime-III two-room period with dense git and no automation: catalysis can only come from executed repos.

## Prediction
*Written 2026-10-04, before running on this period (card P1–P5, amendments A1–A2).*
- P1: maxRAF coverage ≤ 20% of agent work commits.
- P2: no irrRAF of size ≥ 3 beyond the rewired null (support ≥ 3 cycles: S3 = 0, or rewired p ≥ 0.05).
- P3: self-catalysed reactions carry ≥ 50% of maxRAF commits (automated included); in-period tools catalysing other repos carry ≤ 5% of agent work commits.
- P4: real catalysed coverage / time-reversed catalysed coverage > 1 (day-bootstrap CI excludes 1).
- P5: maxCAF ≥ 90% of maxRAF commits.

## Result
Data: `data/processed/H79-artifact-autocatalytic-set/results/G38.json`; pipeline `analysis/run.py --period G38`; events from `scheme/build.py`.

| Prediction | Observed (95% CI) | Null | Verdict |
| --- | --- | --- | --- |
| P1 coverage ≤ 20% | 0.216 [0.135, 0.306] of 1,393 | rewired 0.216 | failed (CI covers 0.20) |
| P2 no supported ≥3 cycles | 0 (one unsupported 2-cycle) | rewired 0 | supported |
| P3a self ≥ 50% | 0.924 | – | supported |
| P3b in-period tools ≤ 5% | 0.018 | rewired 0.014 | supported |
| P4 exec before/after > 1 | 0.744 [0.562, 0.901] | 1 | failed (reversed) |
| P5 maxCAF ≥ 90% | 0.794 | – | failed |

## Scorecard (period-specific axes)
- C: 0 (coverage = null). D: 1 (P2, P3 hold; P4 reversed).

## Notes
- 2026-10-04: round 1 run (exploratory replication).
