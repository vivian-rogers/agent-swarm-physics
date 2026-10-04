# H108 × G36: goal #36 (2026-03-23 → 03-27)

**Verdict:** supported
**Role:** exploratory · replication
**Period:** regime II (03-23) / III (03-24 →) · #best 4, #rest 9 agents (one-room agents with ≥ 2 days, H100 counts) · 5 non-holdout days. identical kickoffs; crosses the regime II → III boundary on 03-24.

## Why this period
Identical kickoffs; regime-III days only (03-24 → 03-27; 3 day pairs).

## Prediction
*Written 2026-10-04 ~21:29 UTC, before running on this period (card predictions applied).*
- Identical-period rule: D_θ ≥ 2 D_f (pooled fielded) supports; D_θ ≤ D_f fails.
- Expected: a persistent direction (Σ C(d, d+1) > 0) but rotation similar to the fielded periods (P1 kill credence 0.35).

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout). Primary bge style_resid, a_i removed (period left out); gte alongside. CIs: agent bootstrap within rooms (200), relabel null recomputed per replicate; they sit low (duplicated agents shift the null).*

| Statistic | bge | gte |
| --- | --- | --- |
| agents #best / #rest; days | 3 / 8; 4 | |
| persistence P(1) [95% CI] | 0.19 [-0.09, 0.60] | 0.21 [-0.06, 0.62] |
| decorrelation rate D_θ = −ln P(1) (per day) | 1.652 | 1.564 |
| split-half P_sh(1) (variant, biased low) | 0.51 | 0.46 |
| persistence relabel p (Σ D(d)·D(d+1)) | 0.353 | 0.307 |
| N_eff; mean daily E | 2.18; 0.039 | 2.18; 0.041 |
| pooled reference (bge): D_id 0.355, D_f 0.075 | | |

Verdict components: {"replication": "supported", "bge": "supported", "gte": "supported"}.

Data: `data/processed/H108-goldstone-room-wandering/results/raw_all.json` (key `G36`), `results.json`.

## Scorecard (period-specific axes)
- **C:** joint-relabel noise correction; **D:** rotation is unfitted.

## Notes
