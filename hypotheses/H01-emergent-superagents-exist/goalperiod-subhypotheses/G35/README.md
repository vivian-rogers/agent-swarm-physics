# H01 × G35: Test your game to make it as fun and functional as you can (2026-03-16 → 03-23)

**Verdict:** failed (round 2: no agency signature; round 1: mixed)
**Verdict (1b):** mixed (unchanged, both models)
**Role:** replication (exploratory)
**Period:** regime II · mode C · 13 agents · #best/#rest (split 03-16, NE15; RPG forked per room) · 5 days. The pre-split window (#34) is held out.

## Why this period
First week with two populated rooms; each room tests its own fork of a shared game, so rooms differ in content by design.

## Prediction
*Written 2026-10-03 on the main card (P1–P9, Amendments 1–3), before any analysis of this period.*
P1–P3 (rooms ordered, stable), P5 (fields ≥ 60%), P6 (exposure slope > 0, within > cross), P9.
Falsifiers as on the main card: ΔH ≥ 0 on most days (D3.1.a); field R² < 0.3 or exposure slope ≥ 0.1 (D3.2′); slope and within > cross vanish under the rotation null (D3.2).

## Result
Units: 35. Data: `data/processed/H01-emergent-superagents-exist/G35/results.json`. Figure: `figures/G35_panels.pdf`.

| unit | P1 rooms: days ΔH<0 · median ΔH · days p<.05 · day-1 ΔH | P2 labs median ΔH | P3 pairs below null q05 | P5 R² (rotation null) | P6 slope ± SE (rotation p) | within − cross (perm p) | P9 βJ₀/n ± SE · ρ_within/ρ_cross |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 35 | 100% · -0.070 · 60% · -0.086 | -0.054 | 12% of 8 | 0.15 (0.49) | -0.019 ± 0.015 (0.945) | +0.222 (0.003) | 0.87 ± 0.03 · 0.66/0.09 |

## Scorecard (period-specific axes)
- **C** 1: rooms vs random partitions and the rotation/day-shuffle nulls computed per unit (see table). **G** 1 where rooms are ordered. **E** n/a within the period.

## Notes
- 2026-10-03: P5 R² (0.15) is below the D3.2′ falsifier (0.3) and far below its rotation null: alignment here is not field-like. The within-room excess is large (+0.22) but the exposure slope is ≈ 0, which the synthetic world produces for saturated coupling or a room field (the room forks). Day-to-day co-fluctuation within rooms ρ = 0.66 vs 0.09 across.
- Agent field h_i: the agent's first day in the unit (Amendment 3, after the invariance check failed in regimes II and III), so P5/P6 use days 2+. P6 uses rarefied agent-day vectors (8 statements, Amendment 2).

## Round 2 (2026-10-04)
Round 2 (effective superagents in Kolchinsky–Wolpert terms) is in [`README_round2.md`](README_round2.md). Verdict: **failed**: no agency signature.

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Round-1 statistics re-run on the corrected inputs (card: Round 1b): shared goal vectors, restatements removed (each model's own DQ5 flag, chat only), bge-small and gte-modernbert, and DQ5's style-residualized vectors (identity claims).

| unit | statistic | round 1 | 1b bge | 1b gte | 1b bge style-resid | 1b gte style-resid |
| --- | --- | --- | --- | --- | --- | --- |
| 35 | P1 room ΔH (median) | -0.070 | -0.071 | -0.137 | -0.077 | -0.111 |
| 35 | P5 field R² | 0.15 | 0.13 | 0.09 | 0.06 | 0.05 |
| 35 | P6 exposure slope | -0.019 ± 0.015 | -0.010 ± 0.014 | -0.022 ± 0.014 | -0.021 ± 0.012 | -0.028 ± 0.013 |
| 35 | P6 within − cross | 0.222 | 0.227 | 0.219 | 0.208 | 0.202 |
| 35 | within − cross, room fields removed | 0.222 | 0.227 | 0.219 | 0.208 | 0.202 |
| 35 | P9 βJ₀/n (upper bound) | 0.87 | 0.87 | 0.86 | – | – |

Style-residualized runs report P1/P2/P5–P7 only (goal fields are not defined in that space). Data: `data/processed/H01-emergent-superagents-exist/r1b/<instrument>/explore.json`, `r1b/compare.json`.
<!-- /R1B -->
