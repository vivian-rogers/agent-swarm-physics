# H107 × G38: goal #38 (2026-04-02 → 04-24)

**Verdict:** mixed
**Role:** exploratory · native (positive control: room-specific kickoffs)
**Period:** regime III · #best 6, #rest 8 agents (one-room agents with ≥ 2 days, H100 counts) · 17 non-holdout days. room-specific kickoffs (whitened cos 0.86); the longest two-room period.

## Why this period
Room-specific kickoffs: a known field from day 1. The onset must show a step if the instrument works.

## Prediction
*Written 2026-10-04 ~21:29 UTC, before running on this period (card predictions applied).*
- P4: π₁ ≥ 0.6 [0.6]; r₁ ≥ 0.8 and c₁ ≥ 0.7 [0.4].
- F = the last 6 of 17 days; the period's work evolves over three weeks, so π₁ may fall below 1 by drift even with a field (read with H108).
- Counts against: π₁ < 0.3.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout). Primary bge style_resid, a_i removed (P and P⁻ left out); gte alongside.*

| Statistic | bge | gte |
| --- | --- | --- |
| agents #best / #rest | 6 / 8 | |
| final split E_F (relabel p) | 0.376 (0.001) | 0.345 (0.001) |
| onset ratio r₁ = E(1)/E_F [95% CI] | 1.11 [0.81, 1.60] | 1.36 |
| onset projection π₁ [95% CI] | 0.53 [0.34, 0.80] | 0.44 |
| onset cosine c₁ (E(1) p) | 0.51 (0.001) | 0.37 (0.001) |
| growth: E(d)/E_F by day | 1.11, 0.76, 1.06, 1.22, 1.15, 1.11, 1.23, 1.33, 1.23, 1.03, 0.90, 0.88, 1.25, 1.10, 1.08, 1.29, 0.98 | 1.36, 1.11, 1.54, 1.30, 1.69, 1.32, 1.43, 1.47, 1.33, 1.31, 1.10, 0.99, 1.02, 1.06, 1.17, 1.46, 1.05 |
| first half-day E/E_F | 1.06 | 1.48 |
| inherited repo field f_repo period / day 1 (p) | 0.07 (0.472) / 0.02 (0.450) | 0.04 (0.539) / 0.12 (0.144) |
| carried content field f_prev period / day 1 (p) | 0.16 (0.240) / 0.01 (0.532) | 0.24 (0.049) / 0.00 (0.843) |
| work persistence κ_w | 0.04 | |

Verdict components: {"native": "mixed", "pi1_bge": 0.5347121549571063, "pi1_gte": 0.4360749805947212}.

Data: `data/processed/H107-room-split-onset/results/raw_all.json` (key `G38`), `results.json`.

## Scorecard (period-specific axes)
- **G:** a known field (room kickoffs) must show a step; **E:** kickoff contrast.

## Notes
