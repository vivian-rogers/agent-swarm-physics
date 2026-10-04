# H76 × NE41: forced context erasures as event-aligned copies (G51 head and G38, each separately)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** regime III; forced erasures at the 41-turn cap (`context_ledger_turns.reset_forced`, non-holdout), isolated (no other reset within 3 windows; not in the first or last 3 windows of a day).

## Why this period
- The scaffold sets the timing of a forced erasure, so the copies are quasi-random in time. H44: read share doubles at the first post-reset call, writes fall 26%. Excess needs copies at a fixed time; aligned erasures are such copies.

## Prediction
*Written 2026-10-04 ~20:15 UTC, after the synthetic validation (amendment A1), before running on this period.*
- N2: at the reset steps (e−1 → e and e → e+1), the event-aligned σ_ex is ≥ 2× the placebo copies' σ_ex, and σ_hk is within ×[0.5, 2] of the placebo's, in both periods → supported; neither period → failed. Credence 0.45. Known issues 66 and 71 apply (v3 labels post-reset windows as more executing; no burn-in is used).

## Result
*Run 2026-10-04 ~21:05 UTC (`analysis/run.py: ne41`; `data/processed/H76-excess-housekeeping-split/NE41/results_G51.json`, `results_G38.json`; figure `../../figures/synthetic_ne41.pdf` panel b).* Coarse states. Placebo windows: the same agents, ≥ 3 windows from any reset, present (labelled) at p−2 … p+2, nearest to the reset in time of day (amendment A2).

| Period | copies / placebos | σ_ex at reset steps vs placebo (95% CI) | σ_hk ratio (95% CI) | N2 |
| --- | --- | --- | --- | --- |
| G51 | 2989 / 670 | ×12.1 [6.2, 27.3] | ×1.31 [0.64, 3.96] | pass |
| G38 | 410 / 77 | ×5.2 [2.8, 10.4] | ×0.38 [0.05, 2.39] | fail (σ_hk below 0.5) |

- Mean coarse occupancy (absent, work, explore, coord, wait) of the G51 copies: e−1 [0.43, 0.35, 0.08, 0.03, 0.11], e [0.17, 0.45, 0.12, 0.03, 0.22], e+1 [0.21, 0.51, 0.13, 0.04, 0.11]. The window before the reset window is 43% "absent": the forced consolidation is a multi-minute summary call with no logged action, so v3 reads it as no record. The excess pulse is that gap closing.
- One window later (e+1 → e+2) the excess is back at the placebo level (G51 0.013 vs 0.029 nats per copy-step; G38 −0.001 vs 0.069).

**Verdict: mixed.** The scaffold-timed erasure produces a one-window excess pulse (×5–12), as predicted, and no lasting change in the behavior mix. The pulse is mostly the consolidation gap itself, a scaffold artifact in the v3 grid, not a change of behavior. Housekeeping is unchanged in G51 and lower in G38 with a CI that spans the band.
