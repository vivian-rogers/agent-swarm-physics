# H01 × G39: Build your own interactive world (2026-04-27 → 05-04)

**Verdict:** mixed (round 2: continuity, partial agency; round 1: mixed)
**Verdict (1b):** mixed (unchanged)
**Role:** replication (exploratory)
**Period:** regime III · mode I · 15 agents · two rooms after the 04-27 transfer (3 agents #best → #rest; GPT-5.5 joins) · 5 days.

## Why this period
Individual world-building; also the pre-window of the 05-04 merge (P7, see G40).

## Prediction
*Written 2026-10-03 on the main card (P1–P9, Amendments 1–3), before any analysis of this period.*
P1–P3, P5, P6, P9.
Falsifiers as on the main card: ΔH ≥ 0 on most days (D3.1.a); field R² < 0.3 or exposure slope ≥ 0.1 (D3.2′); slope and within > cross vanish under the rotation null (D3.2).

## Result
Units: 39. Data: `data/processed/H01-emergent-superagents-exist/G39/results.json`. Figure: `figures/G39_panels.pdf`.

| unit | P1 rooms: days ΔH<0 · median ΔH · days p<.05 · day-1 ΔH | P2 labs median ΔH | P3 pairs below null q05 | P5 R² (rotation null) | P6 slope ± SE (rotation p) | within − cross (perm p) | P9 βJ₀/n ± SE · ρ_within/ρ_cross |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 39 | 80% · -0.037 · 0% · -0.025 | -0.253 | 12% of 8 | 0.75 (0.75) | +0.018 ± 0.020 (0.239) | +0.086 (0.018) | 0.66 ± 0.06 · 0.17/0.08 |

## Scorecard (period-specific axes)
- **C** 1: rooms vs random partitions and the rotation/day-shuffle nulls computed per unit (see table). **G** 1 where rooms are ordered. **E** n/a within the period.

## Notes
- 2026-10-03: Rooms barely more ordered than random (median ΔH −0.04, no day significant) but labs are (−0.25): the one unit where lab order beats room order. H05 also found no block structure in #39.
- Agent field h_i: the agent's first day in the unit (Amendment 3, after the invariance check failed in regimes II and III), so P5/P6 use days 2+. P6 uses rarefied agent-day vectors (8 statements, Amendment 2).

## Round 2 (2026-10-04)
Round 2 (effective superagents in Kolchinsky–Wolpert terms) is in [`README_round2.md`](README_round2.md). Verdict: **mixed**: continuity, partial agency.

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Round-1 statistics re-run on the corrected inputs (card: Round 1b): shared goal vectors, restatements removed (each model's own DQ5 flag, chat only), bge-small and gte-modernbert, and DQ5's style-residualized vectors (identity claims).

| unit | statistic | round 1 | 1b bge | 1b gte | 1b bge style-resid | 1b gte style-resid |
| --- | --- | --- | --- | --- | --- | --- |
| 39 | P1 room ΔH (median) | -0.037 | -0.045 | -0.059 | 0.008 | 0.010 |
| 39 | P5 field R² | 0.75 | 0.75 | 0.83 | 0.65 | 0.69 |
| 39 | P6 exposure slope | +0.018 ± 0.020 | +0.019 ± 0.019 | +0.036 ± 0.025 | +0.008 ± 0.023 | -0.014 ± 0.023 |
| 39 | P6 within − cross | 0.086 | 0.084 | 0.058 | 0.002 | -0.036 |
| 39 | within − cross, room fields removed | 0.086 | 0.084 | 0.058 | 0.002 | -0.036 |
| 39 | P9 βJ₀/n (upper bound) | 0.66 | 0.67 | 0.62 | – | – |

Style-residualized runs report P1/P2/P5–P7 only (goal fields are not defined in that space). Data: `data/processed/H01-emergent-superagents-exist/r1b/<instrument>/explore.json`, `r1b/compare.json`.
<!-- /R1B -->
