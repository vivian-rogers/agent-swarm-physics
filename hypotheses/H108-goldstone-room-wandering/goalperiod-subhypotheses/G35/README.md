# H108 × G35: goal #35 (2026-03-16 → 03-20)

**Verdict:** failed
**Role:** exploratory · native (G35 forks: work field)
**Period:** regime II · #best 3, #rest 9 agents (one-room agents with ≥ 2 days, H100 counts) · 5 non-holdout days. RPG fork week (NE15): each room works on its own fork from day 1.

## Why this period
Each room works on its own fork all week: a work field that should pin the room direction. Regime II: no agent constants.

## Prediction
*Written 2026-10-04 ~21:29 UTC, before running on this period (card predictions applied).*
- P5: ω(G35) ≤ ω pooled over the identical periods, both computed without agent constants [0.5].
- Counts against: ω(G35) ≥ 2× the identical no-constants ω.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/summarize.py`; non-holdout). Primary bge style_resid, a_i removed (period left out); gte alongside. CIs: agent bootstrap within rooms (200), relabel null recomputed per replicate; they sit low (duplicated agents shift the null).*

| Statistic | bge | gte |
| --- | --- | --- |
| agents #best / #rest; days | 3 / 9; 5 | |
| persistence P(1) [95% CI] | 0.32 [0.24, 0.48] | 0.37 [0.33, 0.48] |
| decorrelation rate D_θ = −ln P(1) (per day) | 1.151 | 0.986 |
| split-half P_sh(1) (variant, biased low) | 0.37 | 0.40 |
| persistence relabel p (Σ D(d)·D(d+1)) | 0.012 | 0.003 |
| N_eff; mean daily E | 2.25; 0.097 | 2.25; 0.113 |
| pooled reference (bge): D_id 0.355, D_f 0.075 | | |
| P5 (bge_small, no constants): ω(G35) vs pooled identical ω | 0.68 vs 0.27 | |
| P5 (gte_modernbert, no constants): ω(G35) vs pooled identical ω | 0.63 vs 0.24 | |

Verdict components: {"native": "failed", "P5": {"bge_small/style_resid/noconst": {"omega_G35": 0.6838340680565813, "omega_identical": 0.26705078239115676, "verdict": "failed"}, "gte_modernbert/style_resid/noconst": {"omega_G35": 0.6269657101355657, "omega_identical": 0.2360685608267834, "verdict": "failed"}}}.

Data: `data/processed/H108-goldstone-room-wandering/results/raw_all.json` (key `G35`), `results.json`.

## Scorecard (period-specific axes)
- **E, G:** a known work field (forks) should pin.

## Notes
