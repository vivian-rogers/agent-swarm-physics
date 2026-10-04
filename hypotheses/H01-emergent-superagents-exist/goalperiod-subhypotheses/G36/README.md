# H01 × G36: Interact with other AI agents outside the Village (2026-03-23 → 03-30)

**Verdict:** mixed (round 2: continuity, partial agency; round 1: failed)
**Verdict (1b):** failed (unchanged)
**Role:** exploratory
**Period:** regime II (36a, 03-23, one day) / regime III (36b, 03-24 → 03-27) · mode C · 13 agents · two rooms · split at the 03-24 regime boundary.

## Why this period
Two-room regime-III days not in the card's P1 list; reported as secondary (Amendment 2). 36a is one day (P9 needs ≥ 2).

## Prediction
*Written 2026-10-03 on the main card (P1–P9, Amendments 1–3), before any analysis of this period.*
Secondary P1; P5/P6 per Amendment 1; P9.
Falsifiers as on the main card: ΔH ≥ 0 on most days (D3.1.a); field R² < 0.3 or exposure slope ≥ 0.1 (D3.2′); slope and within > cross vanish under the rotation null (D3.2).

## Result
Units: 36a, 36b. Data: `data/processed/H01-emergent-superagents-exist/G36/results.json`. Figure: `figures/G36_panels.pdf`.

| unit | P1 rooms: days ΔH<0 · median ΔH · days p<.05 · day-1 ΔH | P2 labs median ΔH | P3 pairs below null q05 | P5 R² (rotation null) | P6 slope ± SE (rotation p) | within − cross (perm p) | P9 βJ₀/n ± SE · ρ_within/ρ_cross |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 36a | n/a | – | – | – | – | – | – |
| 36b | 0% · +0.031 · 0% · +0.024 | -0.134 | – | 0.71 (0.74) | +0.037 ± 0.020 (0.060) | +0.084 (0.085) | 0.82 ± 0.05 · 0.31/0.15 |

## Scorecard (period-specific axes)
- **C** 1: rooms vs random partitions and the rotation/day-shuffle nulls computed per unit (see table). **G** 1 where rooms are ordered. **E** n/a within the period.

## Notes
- 2026-10-03: Rooms are not more ordered than random here (ΔH > 0 on all 4 days). The within-room excess is +0.08 (p = 0.09).
- Agent field h_i: the agent's first day in the unit (Amendment 3, after the invariance check failed in regimes II and III), so P5/P6 use days 2+. P6 uses rarefied agent-day vectors (8 statements, Amendment 2).

## Round 2 (2026-10-04)
Round 2 (effective superagents in Kolchinsky–Wolpert terms) is in [`README_round2.md`](README_round2.md). Verdict: **mixed**: continuity, partial agency.

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Round-1 statistics re-run on the corrected inputs (card: Round 1b): shared goal vectors, restatements removed (each model's own DQ5 flag, chat only), bge-small and gte-modernbert, and DQ5's style-residualized vectors (identity claims).

| unit | statistic | round 1 | 1b bge | 1b gte | 1b bge style-resid | 1b gte style-resid |
| --- | --- | --- | --- | --- | --- | --- |
| 36b | P1 room ΔH (median) | 0.031 | 0.026 | 0.019 | 0.024 | 0.042 |
| 36b | P5 field R² | 0.71 | 0.70 | 0.76 | 0.68 | 0.70 |
| 36b | P6 exposure slope | +0.037 ± 0.020 | +0.023 ± 0.019 | +0.039 ± 0.018 | +0.030 ± 0.023 | +0.030 ± 0.019 |
| 36b | P6 within − cross | 0.084 | 0.064 | 0.061 | 0.042 | 0.023 |
| 36b | within − cross, room fields removed | 0.084 | 0.064 | 0.061 | 0.042 | 0.023 |
| 36b | P9 βJ₀/n (upper bound) | 0.82 | 0.81 | 0.83 | – | – |

Style-residualized runs report P1/P2/P5–P7 only (goal fields are not defined in that space). Data: `data/processed/H01-emergent-superagents-exist/r1b/<instrument>/explore.json`, `r1b/compare.json`.
<!-- /R1B -->
