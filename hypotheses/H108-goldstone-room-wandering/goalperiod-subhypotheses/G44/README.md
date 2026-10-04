# H108 × G44: goal #44 (2026-05-26 → 05-29)

**Verdict:** mixed
**Role:** exploratory · replication
**Period:** regime III · #best 6, #rest 12 agents (one-room agents with ≥ 2 days, H100 counts) · 4 non-holdout days. room-specific kickoffs (whitened cos 0.81); heavy operator traffic in #best; pre-period #43 is held out, so P⁻ = #42.

## Why this period
Room-specific kickoffs; 4 days (3 day pairs).

## Prediction
*Written 2026-10-04 ~21:29 UTC, before running on this period (card predictions applied).*
- Fielded rule as for G38 (D_θ ≤ ½ D_id supports).

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout). Primary bge style_resid, a_i removed (period left out); gte alongside. CIs: agent bootstrap within rooms (200), relabel null recomputed per replicate; they sit low (duplicated agents shift the null).*

| Statistic | bge | gte |
| --- | --- | --- |
| agents #best / #rest; days | 6 / 12; 4 | |
| persistence P(1) [95% CI] | 0.78 [0.67, 0.81] | 0.89 [0.78, 0.91] |
| decorrelation rate D_θ = −ln P(1) (per day) | 0.254 | 0.120 |
| split-half P_sh(1) (variant, biased low) | 0.76 | 0.85 |
| persistence relabel p (Σ D(d)·D(d+1)) | 0.000 | 0.000 |
| N_eff; mean daily E | 3.45; 0.260 | 3.45; 0.334 |
| pooled reference (bge): D_id 0.355, D_f 0.075 | | |

Verdict components: {"replication": "mixed", "bge": "mixed", "gte": "supported"}.

Data: `data/processed/H108-goldstone-room-wandering/results/raw_all.json` (key `G44`), `results.json`.

## Scorecard (period-specific axes)
- **G:** a known field should pin.

## Notes
