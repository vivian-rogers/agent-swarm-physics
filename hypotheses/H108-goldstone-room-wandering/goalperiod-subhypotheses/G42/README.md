# H108 × G42: goal #42 (2026-05-18 → 05-22)

**Verdict:** supported
**Role:** exploratory · replication
**Period:** regime III · #best 5, #rest 11 agents (one-room agents with ≥ 2 days, H100 counts) · 5 non-holdout days. identical kickoffs.

## Why this period
Identical kickoffs; 5 days; borderline split in H100.

## Prediction
*Written 2026-10-04 ~21:29 UTC, before running on this period (card predictions applied).*
- Identical-period rule as for G36. A small |m| predicts fast diffusion (or descriptive if E ≈ 0).

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout). Primary bge style_resid, a_i removed (period left out); gte alongside. CIs: agent bootstrap within rooms (200), relabel null recomputed per replicate; they sit low (duplicated agents shift the null).*

| Statistic | bge | gte |
| --- | --- | --- |
| agents #best / #rest; days | 5 / 11; 5 | |
| persistence P(1) [95% CI] | 0.77 [0.17, 0.81] | 0.81 [0.43, 0.85] |
| decorrelation rate D_θ = −ln P(1) (per day) | 0.255 | 0.210 |
| split-half P_sh(1) (variant, biased low) | 0.72 | 0.73 |
| persistence relabel p (Σ D(d)·D(d+1)) | 0.124 | 0.086 |
| N_eff; mean daily E | 3.24; 0.027 | 3.24; 0.030 |
| pooled reference (bge): D_id 0.355, D_f 0.075 | | |

Verdict components: {"replication": "supported", "bge": "supported", "gte": "supported"}.

Data: `data/processed/H108-goldstone-room-wandering/results/raw_all.json` (key `G42`), `results.json`.

## Scorecard (period-specific axes)
- **C:** joint-relabel noise correction; **D:** rotation is unfitted.

## Notes
