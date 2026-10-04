# H107 × G39: goal #39 (2026-04-27 → 05-01)

**Verdict:** mixed
**Role:** exploratory · replication + native (04-27 reshuffle)
**Period:** regime III · #best 4, #rest 11 agents (one-room agents with ≥ 2 days, H100 counts) · 5 non-holdout days. identical kickoffs; 04-27 reshuffle: Opus 4.6, Sonnet 4.6, GPT-5.4 moved #best → #rest.

## Why this period
Identical kickoffs after a reshuffle: three #38 #best agents moved into #rest, carrying 17 days of room-specific #38 work. The inherited repo field (from #38 commits) is strongest here.

## Prediction
*Written 2026-10-04 ~21:29 UTC, before running on this period (card predictions applied).*
- P1 replication clauses as for every identical period (SSB r₁ ≤ 0.3 [0.2]; kill [0.35]).
- P6 native: f_repo(day 1) along the #38-repo field ≥ 0.15 with p < 0.05 [0.3]; f_prev(day 1) along the members' #38 content grouped by #39 rooms ≥ 0.15 with p < 0.05 [0.3].
- Counts against SSB here: either P6 clause met (the split is inherited).

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout). Primary bge style_resid, a_i removed (P and P⁻ left out); gte alongside.*

| Statistic | bge | gte |
| --- | --- | --- |
| agents #best / #rest | 4 / 11 | |
| final split E_F (relabel p) | 0.089 (0.023) | 0.037 (0.113) |
| onset ratio r₁ = E(1)/E_F [95% CI] | -0.09 [0.02, 1.63] | 0.43 |
| onset projection π₁ [95% CI] | -0.20 [-0.46, 0.42] | -0.57 |
| onset cosine c₁ (E(1) p) | – (0.540) | -0.87 (0.295) |
| growth: E(d)/E_F by day | -0.09, 0.64, 0.41, 0.86, 1.16 | 0.43, 0.85, -1.42, 0.23, 2.19 |
| first half-day E/E_F | -0.11 | 0.94 |
| inherited repo field f_repo period / day 1 (p) | 0.07 (0.192) / -0.00 (0.760) | 0.01 (0.647) / 0.05 (0.131) |
| carried content field f_prev period / day 1 (p) | 0.10 (0.127) / 0.01 (0.492) | 0.02 (0.471) / 0.22 (0.002) |
| work persistence κ_w | 0.00 | |

Verdict components: {"replication": "supported", "bge": "supported", "gte": "descriptive", "native": "mixed", "native_by_model": ["supported", "failed"]}.

Data: `data/processed/H107-room-split-onset/results/raw_all.json` (key `G39`), `results.json`.

## Scorecard (period-specific axes)
- **C, D:** onset shape; **E:** the 04-27 reshuffle (inherited #38 work).

## Notes
