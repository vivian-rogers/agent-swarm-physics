# H01 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 04-27)

**Verdict:** mixed
**Role:** exploratory
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
