# H107 × G35: goal #35 (2026-03-16 → 03-20)

**Verdict:** mixed
**Role:** exploratory · native (G35 forks: a known work field)
**Period:** regime II · #best 3, #rest 9 agents (one-room agents with ≥ 2 days, H100 counts) · 5 non-holdout days. RPG fork week (NE15): each room works on its own fork from day 1.

## Why this period
A known work field set on day 1 (each room on its own fork; NE15). The onset should look like a step. Regime II: no agent constants, so composition stays in.

## Prediction
*Written 2026-10-04 ~21:29 UTC, before running on this period (card predictions applied).*
- P5: π₁ ≥ 0.6 (the day-1 room difference already lies along the final one at ≥ 60% of its size).
- Expected also: r₁ ≥ 0.5; f_repo is undefined (the forks are new repos, no pre-period statements name them).
- Counts against: π₁ < 0.3 (a known work field shows no step: the estimator misses steps at this period's counts).

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout). Primary bge style_resid, a_i removed (P and P⁻ left out); gte alongside.*

| Statistic | bge | gte |
| --- | --- | --- |
| agents #best / #rest | 3 / 9 | |
| final split E_F (relabel p) | 0.064 (0.007) | 0.064 (0.010) |
| onset ratio r₁ = E(1)/E_F [95% CI] | 1.39 [0.88, 1.89] | 1.95 |
| onset projection π₁ [95% CI] | 0.43 [0.31, 0.69] | 0.62 |
| onset cosine c₁ (E(1) p) | 0.37 (0.007) | 0.45 (0.000) |
| growth: E(d)/E_F by day | 1.39, 0.36, 3.10, 0.77, 1.95 | 1.95, 0.86, 2.95, 0.60, 2.50 |
| first half-day E/E_F | 1.18 | 1.95 |
| work persistence κ_w | 0.00 | |

Verdict components: {"native": "mixed", "pi1_bge": 0.43250484562054914, "pi1_gte": 0.6235421731776096}.

Data: `data/processed/H107-room-split-onset/results/raw_all.json` (key `G35`), `results.json`.

## Scorecard (period-specific axes)
- **G, E:** a known work field (forks, NE15).

## Notes
