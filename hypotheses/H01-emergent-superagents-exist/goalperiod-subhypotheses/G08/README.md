# H01 × G08: Design the AI Village benchmark for open-ended goal pursuit (2025-07-18 → 08-13)

**Verdict:** descriptive
**Verdict (1b):** descriptive (unchanged; P4 still not as predicted)
**Role:** replication (exploratory)
**Period:** regime I · mode C · 4 agents · one room (#general) · 18 days.

## Why this period
Single-room, strongly fielded week (everyone builds a benchmark). No partition exists, so only P4 (polarization along ĝ) and P9 apply. Paired with #21 as the low-field contrast.

## Prediction
*Written 2026-10-03 on the main card (P1–P9, Amendments 1–3), before any analysis of this period.*
P4: whole-swarm polarization along ĝ is high (a strongly fielded week), higher than in #21. P9: βJ₀ < 0.5 n.
Falsifiers as on the main card: ΔH ≥ 0 on most days (D3.1.a); field R² < 0.3 or exposure slope ≥ 0.1 (D3.2′); slope and within > cross vanish under the rotation null (D3.2).

## Result
Units: 8. Data: `data/processed/H01-emergent-superagents-exist/G08/results.json`. Figure: `figures/G08_panels.pdf`.

| unit | P1 rooms: days ΔH<0 · median ΔH · days p<.05 · day-1 ΔH | P2 labs median ΔH | P3 pairs below null q05 | P5 R² (rotation null) | P6 slope ± SE (rotation p) | within − cross (perm p) | P9 βJ₀/n ± SE · ρ_within/ρ_cross |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 8 | n/a | – | – | – | – | – | 0.49 ± 0.08 |

**P4.** Mean polarization along ĝ 0.267 (null sd 0.088); rank 11 of 24 regime-I units. #8 vs #21: 0.267 vs 0.268 → not as predicted.

## Scorecard (period-specific axes)
- **C** 0: P4 has no null-beating contrast (#8 ≈ #21). **D** 0. **G** n/a (one room).

## Notes
- 2026-10-03: N = 4: P9's fluctuation ratio rests on 6 pairs. The ĝ alignment of agent-day vectors (mean cos 0.27) equals #21's, so the 'strong field' reading of #8 is not visible at this instrument.
- Agent field h_i: the agent's first day in the unit (Amendment 3, after the invariance check failed in regimes II and III), so P5/P6 use days 2+. P6 uses rarefied agent-day vectors (8 statements, Amendment 2).

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Round-1 statistics re-run on the corrected inputs (card: Round 1b): shared goal vectors, restatements removed (each model's own DQ5 flag, chat only), bge-small and gte-modernbert, and DQ5's style-residualized vectors (identity claims).

| unit | statistic | round 1 | 1b bge | 1b gte | 1b bge style-resid | 1b gte style-resid |
| --- | --- | --- | --- | --- | --- | --- |
| 8 | P1 room ΔH (median) | – | – | – | – | – |
| 8 | P5 field R² | – | – | – | – | – |
| 8 | P6 exposure slope | – | – | – | – | – |
| 8 | P6 within − cross | – | – | – | – | – |
| 8 | within − cross, room fields removed | – | – | – | – | – |
| 8 | P9 βJ₀/n (upper bound) | 0.49 | 0.50 | 0.53 | – | – |

Style-residualized runs report P1/P2/P5–P7 only (goal fields are not defined in that space). Data: `data/processed/H01-emergent-superagents-exist/r1b/<instrument>/explore.json`, `r1b/compare.json`.
<!-- /R1B -->
