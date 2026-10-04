# H107 × G36: goal #36 (2026-03-23 → 03-27)

**Verdict:** descriptive
**Role:** exploratory · replication (descriptive only)
**Period:** regime II (03-23) / III (03-24 →) · #best 4, #rest 9 agents (one-room agents with ≥ 2 days, H100 counts) · 5 non-holdout days. identical kickoffs; crosses the regime II → III boundary on 03-24.

## Why this period
Identical kickoffs, but day 1 (03-23) is regime II and the other days regime III (different whitening bases), so the onset ratio is not defined. Run as descriptive: the regime-III days' profile E(d)/E_F from 03-24.

## Prediction
*Written 2026-10-04 ~21:29 UTC, before running on this period (card predictions applied).*
- Descriptive only (card rule): E(d)/E_F for 03-24 → 03-27 and f_repo at period level (regime III days).
- No verdict on the SSB clauses.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout). Primary bge style_resid, a_i removed (P and P⁻ left out); gte alongside.*

| Statistic | bge | gte |
| --- | --- | --- |
| agents #best / #rest | 3 / 8 | |
| final split E_F (relabel p) | 0.003 (0.396) | 0.029 (0.116) |
| onset ratio r₁ = E(1)/E_F [95% CI] | 19.17 [0.94, 13.74] | 0.35 |
| onset projection π₁ [95% CI] | 1.79 [-0.49, 1.73] | -0.06 |
| onset cosine c₁ (E(1) p) | 0.41 (0.120) | -0.10 (0.310) |
| growth: E(d)/E_F by day | 19.17, 22.54, 6.74, 0.10 | 0.35, 2.87, 0.93, 1.47 |
| first half-day E/E_F | 19.70 | 0.22 |
| work persistence κ_w | 0.00 | |

Verdict components: {"replication": "descriptive"}.

Data: `data/processed/H107-room-split-onset/results/raw_all.json` (key `G36`), `results.json`.

## Scorecard (period-specific axes)
- **C, D:** relabel null for E and π₁; onset shape is unfitted.

## Notes
