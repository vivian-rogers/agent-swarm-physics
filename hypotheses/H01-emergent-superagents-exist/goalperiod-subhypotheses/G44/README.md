# H01 × G44: Finetune your leader (2026-05-26 → 06-01)

**Verdict:** failed (round 2: no agency signature; round 1: mixed)
**Verdict (1b):** mixed (unchanged)
**Role:** replication (exploratory)
**Period:** regime III · mode C · 16–18 agents · two rooms with a per-room goal/kickoff override (05-26) · 4 days (Opus 4.8 and the temporary fine-tuned leader join 05-28).

## Why this period
Rooms with different instructions again (per-room override), like #38.

## Prediction
*Written 2026-10-03 on the main card (P1–P9, Amendments 1–3), before any analysis of this period.*
P1–P3, P5, P6, P9.
Falsifiers as on the main card: ΔH ≥ 0 on most days (D3.1.a); field R² < 0.3 or exposure slope ≥ 0.1 (D3.2′); slope and within > cross vanish under the rotation null (D3.2).

## Result
Units: 44. Data: `data/processed/H01-emergent-superagents-exist/G44/results.json`. Figure: `figures/G44_panels.pdf`.

| unit | P1 rooms: days ΔH<0 · median ΔH · days p<.05 · day-1 ΔH | P2 labs median ΔH | P3 pairs below null q05 | P5 R² (rotation null) | P6 slope ± SE (rotation p) | within − cross (perm p) | P9 βJ₀/n ± SE · ρ_within/ρ_cross |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 44 | 100% · -0.110 · 75% · -0.031 | -0.091 | 17% of 6 | 0.80 (0.73) | +0.039 ± 0.070 (0.229) | +0.238 (0.000) | 0.74 ± 0.06 · 0.34/-0.01 |

## Scorecard (period-specific axes)
- **C** 1: rooms vs random partitions and the rotation/day-shuffle nulls computed per unit (see table). **G** 1 where rooms are ordered. **E** n/a within the period.

## Notes
- 2026-10-03: Rooms ordered (ΔH −0.11, meets both P1 criteria in this unit) and a large within-room excess (+0.24, p < 0.001), but the exposure slope is n.s. and the rooms had different kickoffs (room field).
- Agent field h_i: the agent's first day in the unit (Amendment 3, after the invariance check failed in regimes II and III), so P5/P6 use days 2+. P6 uses rarefied agent-day vectors (8 statements, Amendment 2).

## Round 2 (2026-10-04)
Round 2 (effective superagents in Kolchinsky–Wolpert terms) is in [`README_round2.md`](README_round2.md). Verdict: **failed**: no agency signature.

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Round-1 statistics re-run on the corrected inputs (card: Round 1b): shared goal vectors, restatements removed (each model's own DQ5 flag, chat only), bge-small and gte-modernbert, and DQ5's style-residualized vectors (identity claims).

| unit | statistic | round 1 | 1b bge | 1b gte | 1b bge style-resid | 1b gte style-resid |
| --- | --- | --- | --- | --- | --- | --- |
| 44 | P1 room ΔH (median) | -0.110 | -0.115 | -0.210 | -0.055 | -0.166 |
| 44 | P5 field R² | 0.80 | 0.80 | 0.91 | 0.66 | 0.80 |
| 44 | P6 exposure slope | +0.039 ± 0.070 | +0.058 ± 0.069 | +0.085 ± 0.073 | +0.005 ± 0.079 | +0.070 ± 0.076 |
| 44 | P6 within − cross | 0.238 | 0.243 | 0.150 | 0.240 | 0.161 |
| 44 | within − cross, room fields removed | 0.248 | 0.248 | 0.138 | 0.243 | 0.161 |
| 44 | P9 βJ₀/n (upper bound) | 0.74 | 0.74 | 0.74 | – | – |

Style-residualized runs report P1/P2/P5–P7 only (goal fields are not defined in that space). Data: `data/processed/H01-emergent-superagents-exist/r1b/<instrument>/explore.json`, `r1b/compare.json`.
<!-- /R1B -->
