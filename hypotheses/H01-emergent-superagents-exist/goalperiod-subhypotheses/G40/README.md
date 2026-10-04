# H01 × G40: Connect your worlds into a 3D universe (2026-05-04 → 05-11)

**Verdict:** mixed (round 2: continuity, partial agency; round 1: supported)
**Verdict (1b):** supported (P7) in both models; DiD gone after style residualization
**Role:** replication (exploratory)
**Period:** (verdict for P7, this period's specific prediction; P5/P6/P9 as in the table) regime III · mode C · 15 agents · merged into #universe-coordination 05-04, GPT-5 alone in #rest · 5 days.

## Why this period
The 05-04 merge, an 'add' of the cross-room channel: P7's difference-in-differences against #39 (no NE ID in the catalog, so it lives here). No P1 days (only one populated room).

## Prediction
*Written 2026-10-03 on the main card (P1–P9, Amendments 1–3), before any analysis of this period.*
P7: newly co-located pairs' residual alignment rises relative to pairs co-located throughout; GPT-5 (left alone) shows no rise. Direction only (shared-objective week).
Falsifiers as on the main card: ΔH ≥ 0 on most days (D3.1.a); field R² < 0.3 or exposure slope ≥ 0.1 (D3.2′); slope and within > cross vanish under the rotation null (D3.2).

## Result
Units: 40. Data: `data/processed/H01-emergent-superagents-exist/G40/results.json`. Figure: `figures/G40_panels.pdf`.

| unit | P1 rooms: days ΔH<0 · median ΔH · days p<.05 · day-1 ΔH | P2 labs median ΔH | P3 pairs below null q05 | P5 R² (rotation null) | P6 slope ± SE (rotation p) | within − cross (perm p) | P9 βJ₀/n ± SE · ρ_within/ρ_cross |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 40 | no two-room days | – | 0% of 4 | 0.77 (0.82) | +0.027 ± 0.042 (0.139) | +0.128 (0.197) | 0.89 ± 0.06 · 0.26/0.12 |

**P7 (05-04 merge, #39 → #40).**

| arm | pairs | pre (#39) | post (#40) | DiD vs stay | p (pair-clustered) | permutation p |
| --- | --- | --- | --- | --- | --- | --- |
| stay | 51 | 0.166 | 0.371 | – | – | – |
| new (best × rest) | 40 | 0.046 | 0.427 | +0.178 ± 0.048 | 0.0003 | 0.004 |
| GPT-5 × #rest (cut) | 10 | 0.089 | 0.211 | -0.081 ± 0.057 | 0.158 | – |
| GPT-5 × #best (cross) | 4 | 0.199 | 0.315 | -0.082 ± 0.077 | 0.289 | – |

Cross-fitted-h variant: new-arm DiD +0.102 (permutation p = 0.026).

## Scorecard (period-specific axes)
- **E** 1: the merge DiD has the predicted sign, permutation p = 0.004, robust to instrument variants; confounded with a goal change. **C** 1. **G** 1.

## Notes
- 2026-10-03: Supported in direction and robust to every instrument variant (+0.10 to +0.23), but #40 is a shared-objective week, so goal type is confounded with the merge; stay pairs also rose (+0.21). The A-B-A mirror (05-11 split, used as the confirm script's dry-run stand-in) gave cut-pair DiD −0.24 (permutation p = 0.006).
- Agent field h_i: the agent's first day in the unit (Amendment 3, after the invariance check failed in regimes II and III), so P5/P6 use days 2+. P6 uses rarefied agent-day vectors (8 statements, Amendment 2).

## Round 2 (2026-10-04)
Round 2 (effective superagents in Kolchinsky–Wolpert terms) is in [`README_round2.md`](README_round2.md). Verdict: **mixed**: continuity, partial agency.

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Round-1 statistics re-run on the corrected inputs (card: Round 1b): shared goal vectors, restatements removed (each model's own DQ5 flag, chat only), bge-small and gte-modernbert, and DQ5's style-residualized vectors (identity claims).

| unit | statistic | round 1 | 1b bge | 1b gte | 1b bge style-resid | 1b gte style-resid |
| --- | --- | --- | --- | --- | --- | --- |
| 40 | P1 room ΔH (median) | – | – | – | – | – |
| 40 | P5 field R² | 0.77 | 0.77 | 0.68 | 0.77 | 0.83 |
| 40 | P6 exposure slope | +0.027 ± 0.042 | +0.020 ± 0.041 | +0.040 ± 0.041 | +0.032 ± 0.026 | -0.012 ± 0.032 |
| 40 | P6 within − cross | 0.128 | 0.141 | 0.270 | 0.082 | 0.145 |
| 40 | within − cross, room fields removed | 0.128 | 0.141 | 0.270 | 0.082 | 0.145 |
| 40 | P9 βJ₀/n (upper bound) | 0.89 | 0.90 | 0.92 | – | – |

Style-residualized runs report P1/P2/P5–P7 only (goal fields are not defined in that space). Data: `data/processed/H01-emergent-superagents-exist/r1b/<instrument>/explore.json`, `r1b/compare.json`.
<!-- /R1B -->
