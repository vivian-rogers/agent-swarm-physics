# H107 × G41: goal #41 (2026-05-11 → 05-15)

**Verdict:** mixed
**Role:** exploratory · replication + native (NE42 re-split)
**Period:** regime III · #best 4, #rest 11 agents (one-room agents with ≥ 2 days, H100 counts) · 5 non-holdout days. identical kickoffs; NE42 re-split to #39's partition after the merged week #40.

## Why this period
Identical kickoffs; rooms re-form with #39's partition after the merged week. H100: Q_spont 4.23, the largest spontaneous split; H47: separated from day 0.

## Prediction
*Written 2026-10-04 ~21:29 UTC, before running on this period (card predictions applied).*
- P1 replication clauses (SSB [0.2]; kill [0.35]).
- P7 native: the excess cross-product of #41 day 1 with the #39 period difference within the joint relabel null (|z| < 2) [0.65]; f_repo along the #40-repo field n.s. [0.7].
- Counts against SSB: day 1 recalls #39's direction (room memory through the merge) or follows #40's work.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout). Primary bge style_resid, a_i removed (P and P⁻ left out); gte alongside.*

| Statistic | bge | gte |
| --- | --- | --- |
| agents #best / #rest | 4 / 11 | |
| final split E_F (relabel p) | 0.244 (0.001) | 0.325 (0.000) |
| onset ratio r₁ = E(1)/E_F [95% CI] | 0.71 [0.53, 0.98] | 0.71 |
| onset projection π₁ [95% CI] | 0.50 [0.29, 0.71] | 0.44 |
| onset cosine c₁ (E(1) p) | 0.59 (0.001) | 0.52 (0.001) |
| growth: E(d)/E_F by day | 0.71, 0.45, 1.14, 1.42, 0.71 | 0.71, 0.59, 1.20, 1.13, 0.98 |
| first half-day E/E_F | 0.82 | 0.68 |
| inherited repo field f_repo period / day 1 (p) | -0.01 (0.991) / 0.08 (0.100) | 0.03 (0.564) / 0.01 (0.711) |
| carried content field f_prev period / day 1 (p) | -0.01 (0.963) / 0.13 (0.037) | -0.00 (0.955) / -0.00 (0.997) |
| work persistence κ_w | 0.31 | |
| P7: #41 day 1 × #39 difference, excess z (cos) | -4.48 (-0.69) | -3.52 (E_39 ≈ 0) |

Verdict components: {"replication": "mixed", "bge": "mixed", "gte": "mixed", "native": "mixed", "P7": {"z_bge": -4.4786052738586095, "z_gte": -3.5241886058389875, "cos_bge": -0.694923658774769, "repo40_ns": true}}.

Data: `data/processed/H107-room-split-onset/results/raw_all.json` (key `G41`), `results.json`.

## Scorecard (period-specific axes)
- **C, D:** onset shape; **E:** the NE42 re-split (room memory).

## Notes
