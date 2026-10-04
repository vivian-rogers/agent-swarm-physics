# H01 × G37: Pick your own goal (2026-03-30 → 04-02)

**Verdict:** failed (round 2: no agency signature; round 1: failed)
**Verdict (1b):** failed (unchanged)
**Role:** replication (exploratory)
**Period:** regime III · mode F · 12 agents · two rooms · 3 days.

## Why this period
Short pick-your-own week in two rooms (secondary for P1).

## Prediction
*Written 2026-10-03 on the main card (P1–P9, Amendments 1–3), before any analysis of this period.*
Secondary P1; P5/P6; P9.
Falsifiers as on the main card: ΔH ≥ 0 on most days (D3.1.a); field R² < 0.3 or exposure slope ≥ 0.1 (D3.2′); slope and within > cross vanish under the rotation null (D3.2).

## Result
Units: 37. Data: `data/processed/H01-emergent-superagents-exist/G37/results.json`. Figure: `figures/G37_panels.pdf`.

| unit | P1 rooms: days ΔH<0 · median ΔH · days p<.05 · day-1 ΔH | P2 labs median ΔH | P3 pairs below null q05 | P5 R² (rotation null) | P6 slope ± SE (rotation p) | within − cross (perm p) | P9 βJ₀/n ± SE · ρ_within/ρ_cross |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 37 | 100% · -0.024 · 33% · -0.021 | -0.038 | – | 0.50 (0.59) | +0.042 ± 0.110 (0.308) | +0.010 (0.426) | 0.76 ± 0.06 · 0.30/0.26 |

## Scorecard (period-specific axes)
- **C** 1: rooms vs random partitions and the rotation/day-shuffle nulls computed per unit (see table). **G** 1 where rooms are ordered. **E** n/a within the period.

## Notes
- 2026-10-03: Weak order (median ΔH −0.02), no room excess (+0.01), cross-room co-fluctuation as large as within (0.26 vs 0.30): in a free week the rooms are not distinct units.
- Agent field h_i: the agent's first day in the unit (Amendment 3, after the invariance check failed in regimes II and III), so P5/P6 use days 2+. P6 uses rarefied agent-day vectors (8 statements, Amendment 2).

## Round 2 (2026-10-04)
Round 2 (effective superagents in Kolchinsky–Wolpert terms) is in [`README_round2.md`](README_round2.md). Verdict: **failed**: no agency signature.

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Round-1 statistics re-run on the corrected inputs (card: Round 1b): shared goal vectors, restatements removed (each model's own DQ5 flag, chat only), bge-small and gte-modernbert, and DQ5's style-residualized vectors (identity claims).

| unit | statistic | round 1 | 1b bge | 1b gte | 1b bge style-resid | 1b gte style-resid |
| --- | --- | --- | --- | --- | --- | --- |
| 37 | P1 room ΔH (median) | -0.024 | -0.034 | -0.105 | -0.012 | -0.047 |
| 37 | P5 field R² | 0.50 | 0.50 | 0.54 | 0.46 | 0.45 |
| 37 | P6 exposure slope | +0.042 ± 0.110 | +0.070 ± 0.087 | +0.083 ± 0.131 | +0.028 ± 0.113 | +0.040 ± 0.108 |
| 37 | P6 within − cross | 0.010 | 0.027 | 0.074 | -0.038 | -0.016 |
| 37 | within − cross, room fields removed | 0.010 | 0.027 | 0.074 | -0.038 | -0.016 |
| 37 | P9 βJ₀/n (upper bound) | 0.76 | 0.76 | 0.80 | – | – |

Style-residualized runs report P1/P2/P5–P7 only (goal fields are not defined in that space). Data: `data/processed/H01-emergent-superagents-exist/r1b/<instrument>/explore.json`, `r1b/compare.json`.
<!-- /R1B -->
