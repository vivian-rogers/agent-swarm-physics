# H107 × G42: goal #42 (2026-05-18 → 05-22)

**Verdict:** failed
**Role:** exploratory · replication
**Period:** regime III · #best 5, #rest 11 agents (one-room agents with ≥ 2 days, H100 counts) · 5 non-holdout days. identical kickoffs.

## Why this period
Identical kickoffs, 5 days. H100: Q_spont 1.61 (p 0.069), borderline.

## Prediction
*Written 2026-10-04 ~21:29 UTC, before running on this period (card predictions applied).*
- P1 (SSB [0.2]; kill [0.35]); repo clause [0.2]; half-day [0.35].
- If E_F has relabel p ≥ 0.05 the period is descriptive (no final split).

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout). Primary bge style_resid, a_i removed (P and P⁻ left out); gte alongside.*

| Statistic | bge | gte |
| --- | --- | --- |
| agents #best / #rest | 5 / 11 | |
| final split E_F (relabel p) | 0.042 (0.029) | 0.075 (0.001) |
| onset ratio r₁ = E(1)/E_F [95% CI] | 0.89 [0.37, 1.91] | 0.48 |
| onset projection π₁ [95% CI] | 0.47 [-0.22, 0.90] | 0.32 |
| onset cosine c₁ (E(1) p) | 0.50 (0.070) | 0.46 (0.078) |
| growth: E(d)/E_F by day | 0.89, 0.44, 0.61, 0.44, 1.60 | 0.48, 0.05, 0.20, 0.85, 1.13 |
| first half-day E/E_F | 2.38 | 1.20 |
| inherited repo field f_repo period / day 1 (p) | 0.05 (0.336) / 0.34 (0.002) | 0.07 (0.217) / 0.39 (0.005) |
| carried content field f_prev period / day 1 (p) | 0.13 (0.119) / 0.40 (0.000) | 0.18 (0.033) / 0.42 (0.002) |
| work persistence κ_w | 0.06 | |

Verdict components: {"replication": "failed", "bge": "failed", "gte": "failed"}.

Data: `data/processed/H107-room-split-onset/results/raw_all.json` (key `G42`), `results.json`.

## Scorecard (period-specific axes)
- **C, D:** relabel null for E and π₁; onset shape is unfitted.

## Notes
