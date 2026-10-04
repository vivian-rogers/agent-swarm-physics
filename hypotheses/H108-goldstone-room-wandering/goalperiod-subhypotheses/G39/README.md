# H108 × G39: goal #39 (2026-04-27 → 05-01)

**Verdict:** mixed
**Role:** exploratory · replication
**Period:** regime III · #best 4, #rest 11 agents (one-room agents with ≥ 2 days, H100 counts) · 5 non-holdout days. identical kickoffs; 04-27 reshuffle: Opus 4.6, Sonnet 4.6, GPT-5.4 moved #best → #rest.

## Why this period
Identical kickoffs after the 04-27 reshuffle; 5 days.

## Prediction
*Written 2026-10-04 ~21:29 UTC, before running on this period (card predictions applied).*
- Identical-period rule as for G36.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout). Primary bge style_resid, a_i removed (period left out); gte alongside. CIs: agent bootstrap within rooms (200), relabel null recomputed per replicate; they sit low (duplicated agents shift the null).*

| Statistic | bge | gte |
| --- | --- | --- |
| agents #best / #rest; days | 4 / 11; 5 | |
| persistence P(1) [95% CI] | 0.89 [0.44, 0.85] | – [-0.03, 0.73] |
| decorrelation rate D_θ = −ln P(1) (per day) | 0.115 | – |
| split-half P_sh(1) (variant, biased low) | 0.79 | 0.62 |
| persistence relabel p (Σ D(d)·D(d+1)) | 0.024 | 0.554 |
| N_eff; mean daily E | 2.92; 0.068 | 2.92; 0.016 |
| pooled reference (bge): D_id 0.355, D_f 0.075 | | |

Verdict components: {"replication": "mixed", "bge": "mixed", "gte": "descriptive"}.

Data: `data/processed/H108-goldstone-room-wandering/results/raw_all.json` (key `G39`), `results.json`.

## Scorecard (period-specific axes)
- **C:** joint-relabel noise correction; **D:** rotation is unfitted.

## Notes
