# H01 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 04-27)

**Verdict:** mixed (round 2: continuity, partial agency; round 1: mixed)
**Verdict (1b):** mixed (unchanged; corrected room fields move within−cross by < 0.03)
**Role:** replication (exploratory)
**Period:** regime III · mode C · 12–14 agents · #best/#rest with different instructions (charity overrides vs. free) · 17 days, split at NE17 (04-14) and NE18 (04-20) into 38a/38b/38c.

## Why this period
The longest two-room period, and the rooms got different goals: a natural test of whether room order is a room field.

## Prediction
*Written 2026-10-03 on the main card (P1–P9, Amendments 1–3), before any analysis of this period.*
P1–P3, P5, P6, P9 per unit.
Falsifiers as on the main card: ΔH ≥ 0 on most days (D3.1.a); field R² < 0.3 or exposure slope ≥ 0.1 (D3.2′); slope and within > cross vanish under the rotation null (D3.2).

## Result
Units: 38a, 38b, 38c. Data: `data/processed/H01-emergent-superagents-exist/G38/results.json`. Figure: `figures/G38_panels.pdf`.

| unit | P1 rooms: days ΔH<0 · median ΔH · days p<.05 · day-1 ΔH | P2 labs median ΔH | P3 pairs below null q05 | P5 R² (rotation null) | P6 slope ± SE (rotation p) | within − cross (perm p) | P9 βJ₀/n ± SE · ρ_within/ρ_cross |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 38a | 100% · -0.336 · 100% · -0.242 | -0.079 | 14% of 14 | 0.35 (0.52) | +0.091 ± 0.067 (0.005) | +0.329 (0.001) | 0.74 ± 0.07 · 0.37/0.04 |
| 38b | 100% · -0.382 · 100% · -0.361 | -0.013 | 17% of 6 | 0.96 (0.90) | -0.056 ± 0.060 (0.886) | +0.076 (0.026) | 0.55 ± 0.16 · 0.16/0.05 |
| 38c | 100% · -0.376 · 100% · -0.358 | -0.010 | 50% of 8 | 0.92 (0.86) | +0.007 ± 0.038 (0.468) | +0.118 (0.015) | 0.48 ± 0.10 · 0.13/0.03 |

## Scorecard (period-specific axes)
- **C** 1: rooms vs random partitions and the rotation/day-shuffle nulls computed per unit (see table). **G** 1 where rooms are ordered. **E** n/a within the period.

## Notes
- 2026-10-03: The strongest room order in the data (ΔH −0.34 to −0.38 nats, every day p < 0.05), but the rooms were given different tasks, so this is the room-field case the synthetic warned about (a room field alone gives ΔH < 0 and within > cross). Exposure slopes are mixed (+0.09, −0.06, +0.01). Lab order is weak (−0.01 to −0.08).
- Agent field h_i: the agent's first day in the unit (Amendment 3, after the invariance check failed in regimes II and III), so P5/P6 use days 2+. P6 uses rarefied agent-day vectors (8 statements, Amendment 2).

## Round 2 (2026-10-04)
Round 2 (effective superagents in Kolchinsky–Wolpert terms) is in [`README_round2.md`](README_round2.md). Verdict: **mixed**: continuity, partial agency.

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Round-1 statistics re-run on the corrected inputs (card: Round 1b): shared goal vectors, restatements removed (each model's own DQ5 flag, chat only), bge-small and gte-modernbert, and DQ5's style-residualized vectors (identity claims).

| unit | statistic | round 1 | 1b bge | 1b gte | 1b bge style-resid | 1b gte style-resid |
| --- | --- | --- | --- | --- | --- | --- |
| 38a | P1 room ΔH (median) | -0.336 | -0.336 | -0.355 | -0.199 | -0.171 |
| 38a | P5 field R² | 0.35 | 0.36 | 0.45 | 0.17 | 0.24 |
| 38a | P6 exposure slope | +0.091 ± 0.067 | +0.091 ± 0.069 | +0.097 ± 0.052 | +0.085 ± 0.060 | +0.087 ± 0.048 |
| 38a | P6 within − cross | 0.329 | 0.313 | 0.403 | 0.281 | 0.329 |
| 38a | within − cross, room fields removed | 0.332 | 0.319 | 0.402 | 0.285 | 0.326 |
| 38a | P9 βJ₀/n (upper bound) | 0.74 | 0.75 | 0.73 | – | – |
| 38b | P1 room ΔH (median) | -0.382 | -0.374 | -0.356 | -0.167 | -0.137 |
| 38b | P5 field R² | 0.96 | 0.95 | 0.97 | 0.69 | 0.87 |
| 38b | P6 exposure slope | -0.056 ± 0.060 | -0.035 ± 0.057 | +0.091 ± 0.065 | -0.051 ± 0.056 | +0.085 ± 0.068 |
| 38b | P6 within − cross | 0.076 | 0.138 | 0.114 | 0.080 | 0.044 |
| 38b | within − cross, room fields removed | 0.091 | 0.157 | 0.117 | 0.095 | 0.049 |
| 38b | P9 βJ₀/n (upper bound) | 0.55 | 0.55 | 0.60 | – | – |
| 38c | P1 room ΔH (median) | -0.376 | -0.360 | -0.416 | -0.161 | -0.138 |
| 38c | P5 field R² | 0.92 | 0.92 | 0.93 | 0.63 | 0.63 |
| 38c | P6 exposure slope | +0.007 ± 0.038 | -0.009 ± 0.041 | -0.080 ± 0.045 | +0.005 ± 0.044 | -0.036 ± 0.033 |
| 38c | P6 within − cross | 0.118 | 0.126 | 0.234 | 0.079 | 0.124 |
| 38c | within − cross, room fields removed | 0.102 | 0.105 | 0.227 | 0.072 | 0.122 |
| 38c | P9 βJ₀/n (upper bound) | 0.48 | 0.49 | 0.57 | – | – |

Style-residualized runs report P1/P2/P5–P7 only (goal fields are not defined in that space). Data: `data/processed/H01-emergent-superagents-exist/r1b/<instrument>/explore.json`, `r1b/compare.json`.
<!-- /R1B -->
