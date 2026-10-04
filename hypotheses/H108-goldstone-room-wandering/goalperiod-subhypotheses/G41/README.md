# H108 × G41: goal #41 (2026-05-11 → 05-15)

**Verdict:** supported
**Role:** exploratory · replication
**Period:** regime III · #best 4, #rest 11 agents (one-room agents with ≥ 2 days, H100 counts) · 5 non-holdout days. identical kickoffs; NE42 re-split to #39's partition after the merged week #40.

## Why this period
Identical kickoffs after the NE42 re-split; the largest spontaneous split in H100.

## Prediction
*Written 2026-10-04 ~21:29 UTC, before running on this period (card predictions applied).*
- Identical-period rule as for G36. A large |m| predicts slow Goldstone diffusion here (D ∝ 1/(N|m|²)).

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout). Primary bge style_resid, a_i removed (period left out); gte alongside. CIs: agent bootstrap within rooms (200), relabel null recomputed per replicate; they sit low (duplicated agents shift the null).*

| Statistic | bge | gte |
| --- | --- | --- |
| agents #best / #rest; days | 4 / 11; 5 | |
| persistence P(1) [95% CI] | 0.69 [0.53, 0.78] | 0.75 [0.57, 0.83] |
| decorrelation rate D_θ = −ln P(1) (per day) | 0.370 | 0.290 |
| split-half P_sh(1) (variant, biased low) | 0.69 | 0.74 |
| persistence relabel p (Σ D(d)·D(d+1)) | 0.001 | 0.001 |
| N_eff; mean daily E | 2.93; 0.224 | 2.93; 0.306 |
| pooled reference (bge): D_id 0.355, D_f 0.075 | | |

Verdict components: {"replication": "supported", "bge": "supported", "gte": "supported"}.

Data: `data/processed/H108-goldstone-room-wandering/results/raw_all.json` (key `G41`), `results.json`.

## Scorecard (period-specific axes)
- **C:** joint-relabel noise correction; **D:** rotation is unfitted.

## Notes
