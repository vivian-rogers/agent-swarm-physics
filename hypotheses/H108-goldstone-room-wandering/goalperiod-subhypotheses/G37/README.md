# H108 × G37: goal #37 (2026-03-30 → 04-01)

**Verdict:** supported
**Role:** exploratory · replication
**Period:** regime III · #best 3, #rest 9 agents (one-room agents with ≥ 2 days, H100 counts) · 3 non-holdout days. identical kickoffs; first fully regime-III goal.

## Why this period
Identical kickoffs; 3 days (2 day pairs); #best has 3 agents.

## Prediction
*Written 2026-10-04 ~21:29 UTC, before running on this period (card predictions applied).*
- Identical-period rule as for G36. Few pairs: wide CI expected.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout). Primary bge style_resid, a_i removed (period left out); gte alongside. CIs: agent bootstrap within rooms (200), relabel null recomputed per replicate; they sit low (duplicated agents shift the null).*

| Statistic | bge | gte |
| --- | --- | --- |
| agents #best / #rest; days | 3 / 9; 3 | |
| persistence P(1) [95% CI] | 0.83 [0.25, 0.92] | 0.83 [0.42, 0.92] |
| decorrelation rate D_θ = −ln P(1) (per day) | 0.189 | 0.186 |
| split-half P_sh(1) (variant, biased low) | 0.72 | 0.76 |
| persistence relabel p (Σ D(d)·D(d+1)) | 0.029 | 0.010 |
| N_eff; mean daily E | 2.25; 0.153 | 2.25; 0.201 |
| pooled reference (bge): D_id 0.355, D_f 0.075 | | |

Verdict components: {"replication": "supported", "bge": "supported", "gte": "supported"}.

Data: `data/processed/H108-goldstone-room-wandering/results/raw_all.json` (key `G37`), `results.json`.

## Scorecard (period-specific axes)
- **C:** joint-relabel noise correction; **D:** rotation is unfitted.

## Notes
