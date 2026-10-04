# H107 × G44: goal #44 (2026-05-26 → 05-29)

**Verdict:** supported
**Role:** exploratory · native (positive control: room-specific kickoffs)
**Period:** regime III · #best 6, #rest 12 agents (one-room agents with ≥ 2 days, H100 counts) · 4 non-holdout days. room-specific kickoffs (whitened cos 0.81); heavy operator traffic in #best; pre-period #43 is held out, so P⁻ = #42.

## Why this period
Room-specific kickoffs from day 1 (and heavy operator traffic in #best): a known field.

## Prediction
*Written 2026-10-04 ~21:29 UTC, before running on this period (card predictions applied).*
- P4: π₁ ≥ 0.6 [0.6]; r₁ ≥ 0.8 and c₁ ≥ 0.7 [0.4].
- Counts against: π₁ < 0.3.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout). Primary bge style_resid, a_i removed (P and P⁻ left out); gte alongside.*

| Statistic | bge | gte |
| --- | --- | --- |
| agents #best / #rest | 6 / 12 | |
| final split E_F (relabel p) | 0.255 (0.000) | 0.360 (0.000) |
| onset ratio r₁ = E(1)/E_F [95% CI] | 0.76 [0.58, 1.11] | 0.69 |
| onset projection π₁ [95% CI] | 0.73 [0.57, 0.87] | 0.78 |
| onset cosine c₁ (E(1) p) | 0.84 (0.000) | 0.94 (0.000) |
| growth: E(d)/E_F by day | 0.76, 1.45, 1.11, 1.04 | 0.69, 1.25, 1.04, 0.98 |
| first half-day E/E_F | 0.84 | 0.69 |
| inherited repo field f_repo period / day 1 (p) | 0.12 (0.058) / 0.17 (0.023) | 0.16 (0.057) / 0.12 (0.128) |
| carried content field f_prev period / day 1 (p) | 0.05 (0.210) / 0.18 (0.020) | 0.12 (0.114) / 0.18 (0.049) |
| work persistence κ_w | 0.00 | |

Verdict components: {"native": "supported", "pi1_bge": 0.7292336322232185, "pi1_gte": 0.7814186175666019}.

Data: `data/processed/H107-room-split-onset/results/raw_all.json` (key `G44`), `results.json`.

## Scorecard (period-specific axes)
- **G:** a known field must show a step; **E:** kickoff contrast.

## Notes
