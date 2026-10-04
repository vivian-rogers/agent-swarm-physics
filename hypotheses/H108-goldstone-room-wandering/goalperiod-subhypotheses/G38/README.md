# H108 × G38: goal #38 (2026-04-02 → 04-24)

**Verdict:** supported
**Role:** exploratory · replication + native (lag profile)
**Period:** regime III · #best 6, #rest 8 agents (one-room agents with ≥ 2 days, H100 counts) · 17 non-holdout days. room-specific kickoffs (whitened cos 0.86); the longest two-room period.

## Why this period
Room-specific kickoffs and 17 days: the only period long enough for a lag profile.

## Prediction
*Written 2026-10-04 ~21:29 UTC, before running on this period (card predictions applied).*
- Fielded rule: D_θ ≤ ½ D_id supports; D_θ ≥ D_id fails.
- P4 native: slope of ln P(ℓ) over ℓ = 1…6 ≥ −0.05 per day and P(6) ≥ 0.5 [0.35].
- Counts against pinning: P(ℓ) decays steadily with lag.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout). Primary bge style_resid, a_i removed (period left out); gte alongside. CIs: agent bootstrap within rooms (200), relabel null recomputed per replicate; they sit low (duplicated agents shift the null).*

| Statistic | bge | gte |
| --- | --- | --- |
| agents #best / #rest; days | 6 / 8; 17 | |
| persistence P(1) [95% CI] | 0.95 [0.83, 0.94] | 0.94 [0.85, 0.94] |
| decorrelation rate D_θ = −ln P(1) (per day) | 0.056 | 0.061 |
| split-half P_sh(1) (variant, biased low) | 0.91 | 0.92 |
| persistence relabel p (Σ D(d)·D(d+1)) | 0.001 | 0.001 |
| N_eff; mean daily E | 2.85; 0.447 | 2.85; 0.486 |
| pooled reference (bge): D_id 0.355, D_f 0.075 | | |
| lag profile P(ℓ), ℓ = 1…6 | 0.95, 0.90, 0.87, 0.87, 0.86, 0.85 | 0.94, 0.91, 0.88, 0.85, 0.86, 0.84 |
| slope of ln P(ℓ) per day; P(6) | -0.019; 0.85 | -0.022; 0.84 |

Verdict components: {"replication": "supported", "bge": "supported", "gte": "supported", "native": "supported", "P4": {"slope_bge": -0.018835632108754965, "P6_bge": 0.851524218457811, "slope_gte": -0.021784422795022695, "P6_gte": 0.8398048082318478}}.

Data: `data/processed/H108-goldstone-room-wandering/results/raw_all.json` (key `G38`), `results.json`.

## Scorecard (period-specific axes)
- **D:** lag profile (pinned plateau vs decay); **G:** a known field should pin.

## Notes
