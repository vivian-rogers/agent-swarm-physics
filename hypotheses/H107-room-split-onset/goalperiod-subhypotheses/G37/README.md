# H107 × G37: goal #37 (2026-03-30 → 04-01)

**Verdict:** supported
**Role:** exploratory · replication
**Period:** regime III · #best 3, #rest 9 agents (one-room agents with ≥ 2 days, H100 counts) · 3 non-holdout days. identical kickoffs; first fully regime-III goal.

## Why this period
Identical kickoffs, 3 days, fully regime III. H100: Q_spont 2.55 (p 0.027).

## Prediction
*Written 2026-10-04 ~21:29 UTC, before running on this period (card predictions applied).*
- P1 (SSB clause): r₁ = E(1)/E_F ≤ 0.3 and growth; credence that it holds here 0.2.
- Kill (onset clause): r₁ ≥ 0.8 and c₁ ≥ 0.7 [0.35]. Repo clause: f_repo ≥ 0.15, direction-null p < 0.05 [0.2].
- Half-day: E(1,0)/E_F ≤ 0.3 [0.35].
- Short period: F = day 3 only; underpowered if P0 says so.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout). Primary bge style_resid, a_i removed (P and P⁻ left out); gte alongside.*

| Statistic | bge | gte |
| --- | --- | --- |
| agents #best / #rest | 3 / 9 | |
| final split E_F (relabel p) | 0.277 (0.018) | 0.338 (0.016) |
| onset ratio r₁ = E(1)/E_F [95% CI] | 0.09 [0.06, 1.08] | 0.15 |
| onset projection π₁ [95% CI] | 0.20 [-0.08, 0.45] | 0.32 |
| onset cosine c₁ (E(1) p) | 0.68 (0.246) | 0.81 (0.107) |
| growth: E(d)/E_F by day | 0.09, 0.66, 1.00 | 0.15, 0.67, 1.00 |
| first half-day E/E_F | -0.03 | 0.03 |
| inherited repo field f_repo period / day 1 (p) | -0.00 (0.932) / -0.00 (0.916) | 0.00 (0.914) / 0.01 (0.816) |
| carried content field f_prev period / day 1 (p) | 0.35 (0.148) / 0.34 (0.000) | 0.21 (0.412) / 0.23 (0.155) |
| work persistence κ_w | 0.31 | |

Verdict components: {"replication": "supported", "bge": "supported", "gte": "supported"}.

Data: `data/processed/H107-room-split-onset/results/raw_all.json` (key `G37`), `results.json`.

## Scorecard (period-specific axes)
- **C, D:** relabel null for E and π₁; onset shape is unfitted.

## Notes
