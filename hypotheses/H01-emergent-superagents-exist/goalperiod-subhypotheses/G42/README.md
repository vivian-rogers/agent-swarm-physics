# H01 × G42: Run your own Youtube channel (2026-05-18 → 05-25)

**Verdict:** failed (round 2: no agency signature; round 1: mixed)
**Verdict (1b):** mixed (unchanged)
**Role:** exploratory
**Period:** regime III · mode I · 16 agents · two rooms · 5 days (Gemini 3.5 Flash joins 05-20; chat-length instruction 05-22, not split).

## Why this period
Individual YouTube channels in two rooms: a field-dominated week (one shared genre).

## Prediction
*Written 2026-10-03 on the main card (P1–P9, Amendments 1–3), before any analysis of this period.*
P1–P3, P5, P6, P9.
Falsifiers as on the main card: ΔH ≥ 0 on most days (D3.1.a); field R² < 0.3 or exposure slope ≥ 0.1 (D3.2′); slope and within > cross vanish under the rotation null (D3.2).

## Result
Units: 42. Data: `data/processed/H01-emergent-superagents-exist/G42/results.json`. Figure: `figures/G42_panels.pdf`.

| unit | P1 rooms: days ΔH<0 · median ΔH · days p<.05 · day-1 ΔH | P2 labs median ΔH | P3 pairs below null q05 | P5 R² (rotation null) | P6 slope ± SE (rotation p) | within − cross (perm p) | P9 βJ₀/n ± SE · ρ_within/ρ_cross |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | 80% · -0.038 · 20% · +0.016 | -0.119 | 0% of 8 | 0.86 (0.83) | -0.019 ± 0.022 (0.821) | +0.028 (0.196) | 0.87 ± 0.07 · 0.19/0.14 |

## Scorecard (period-specific axes)
- **C** 1: rooms vs random partitions and the rotation/day-shuffle nulls computed per unit (see table). **G** 1 where rooms are ordered. **E** n/a within the period.

## Notes
- 2026-10-03: The goal direction alone explains 54% of pairwise alignment (R² 0.54, the highest goal-only share), alignment with ĝ is the highest of regime III (0.43), and rooms add little (ΔH −0.04, within − cross +0.03, slope −0.02): field-driven order, as D3.2′ expects.
- Agent field h_i: the agent's first day in the unit (Amendment 3, after the invariance check failed in regimes II and III), so P5/P6 use days 2+. P6 uses rarefied agent-day vectors (8 statements, Amendment 2).

## Round 2 (2026-10-04)
Round 2 (effective superagents in Kolchinsky–Wolpert terms) is in [`README_round2.md`](README_round2.md). Verdict: **failed**: no agency signature.

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Round-1 statistics re-run on the corrected inputs (card: Round 1b): shared goal vectors, restatements removed (each model's own DQ5 flag, chat only), bge-small and gte-modernbert, and DQ5's style-residualized vectors (identity claims).

| unit | statistic | round 1 | 1b bge | 1b gte | 1b bge style-resid | 1b gte style-resid |
| --- | --- | --- | --- | --- | --- | --- |
| 42 | P1 room ΔH (median) | -0.038 | -0.034 | -0.033 | -0.031 | -0.017 |
| 42 | P5 field R² | 0.86 | 0.86 | 0.91 | 0.90 | 0.91 |
| 42 | P6 exposure slope | -0.019 ± 0.022 | -0.014 ± 0.022 | -0.028 ± 0.027 | -0.010 ± 0.022 | -0.020 ± 0.031 |
| 42 | P6 within − cross | 0.028 | 0.031 | 0.064 | 0.043 | 0.078 |
| 42 | within − cross, room fields removed | 0.028 | 0.031 | 0.064 | 0.043 | 0.078 |
| 42 | P9 βJ₀/n (upper bound) | 0.87 | 0.87 | 0.87 | – | – |

Style-residualized runs report P1/P2/P5–P7 only (goal fields are not defined in that space). Data: `data/processed/H01-emergent-superagents-exist/r1b/<instrument>/explore.json`, `r1b/compare.json`.
<!-- /R1B -->
