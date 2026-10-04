# H01 × G51: Each agent: maximize your assigned goal (2026-07-06 → 09-20 (09-07 → tail held out))

**Verdict:** mixed (round 2: continuity, partial agency; round 1: mixed)
**Verdict (1b):** mixed (unchanged)
**Role:** exploratory
**Period:** regime III · mode I/K · 21–32 agents · one room (#general) except #focus (51c: Gemini 2.5 Pro and Opus 4.8, 08-05 → 08-24) · 45 non-holdout days, split at 07-09 (NE32), 08-05, 08-25 (#focus) and 09-03 (NE33); 09-07 → tail held out.

## Why this period
The private-role era: each agent has its own assigned goal (agent-specific fields, NE26) and everyone shares one room; the largest N and longest window. #focus is the only partition (P1).

## Prediction
*Written 2026-10-03 on the main card (P1–P9, Amendments 1–3), before any analysis of this period.*
P1–P3 on #focus days; P5/P6 per sub-unit (agent goals added to the field subspace, Amendment 2); P9 per sub-unit. NE32 (P8) is in `NE32/`.
Falsifiers as on the main card: ΔH ≥ 0 on most days (D3.1.a); field R² < 0.3 or exposure slope ≥ 0.1 (D3.2′); slope and within > cross vanish under the rotation null (D3.2).

## Result
Units: 51a, 51b, 51c, 51d, 51e. Data: `data/processed/H01-emergent-superagents-exist/G51/results.json`. Figure: `figures/G51_panels.pdf`.

| unit | P1 rooms: days ΔH<0 · median ΔH · days p<.05 · day-1 ΔH | P2 labs median ΔH | P3 pairs below null q05 | P5 R² (rotation null) | P6 slope ± SE (rotation p) | within − cross (perm p) | P9 βJ₀/n ± SE · ρ_within/ρ_cross |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | n/a | – | – | 0.82 (0.81) | +0.039 ± 0.045 (0.104) | – | 0.73 ± 0.06 |
| 51b | n/a | – | – | 0.61 (0.61) | +0.008 ± 0.006 (0.060) | – | 0.65 ± 0.07 |
| 51c | 100% · -0.071 · 92% · -0.060 | -0.056 | 8% of 25 | 0.70 (0.67) | +0.010 ± 0.004 (0.010) | +0.069 (0.004) | 0.60 ± 0.09 · 0.06/0.01 |
| 51d | n/a | – | – | 0.77 (0.78) | +0.038 ± 0.014 (0.005) | – | 0.44 ± 0.10 |
| 51e | n/a | – | – | 0.94 (0.92) | – | – | 0.35 ± 0.44 |

NE32 (GPT-5.6 triplet, 07-09/07-10) is analysed in [`../NE32/`](../NE32/README.md).

## Scorecard (period-specific axes)
- **C** 1: rooms vs random partitions and the rotation/day-shuffle nulls computed per unit (see table). **G** 1 where rooms are ordered. **E** n/a within the period.

## Notes
- 2026-10-03: Small but consistently positive exposure slopes in the big single room (51b +0.008, 51c +0.010, 51d +0.038; rotation p ≤ 0.06), the only setting with enough within-pair exposure variation for tight estimates. The assigned-goal field explains little of the alignment (goal-only R² ≤ 0.05). Mean-field βJ₀/n falls as N grows (0.73 → 0.35).
- Agent field h_i: the agent's first day in the unit (Amendment 3, after the invariance check failed in regimes II and III), so P5/P6 use days 2+. P6 uses rarefied agent-day vectors (8 statements, Amendment 2).

## Round 2 (2026-10-04)
Round 2 (effective superagents in Kolchinsky–Wolpert terms) is in [`README_round2.md`](README_round2.md). Verdict: **mixed**: continuity, partial agency.

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Round-1 statistics re-run on the corrected inputs (card: Round 1b): shared goal vectors, restatements removed (each model's own DQ5 flag, chat only), bge-small and gte-modernbert, and DQ5's style-residualized vectors (identity claims).

| unit | statistic | round 1 | 1b bge | 1b gte | 1b bge style-resid | 1b gte style-resid |
| --- | --- | --- | --- | --- | --- | --- |
| 51a | P1 room ΔH (median) | – | – | – | – | – |
| 51a | P5 field R² | 0.82 | 0.82 | 0.87 | 0.77 | 0.85 |
| 51a | P6 exposure slope | +0.039 ± 0.045 | +0.046 ± 0.046 | +0.017 ± 0.039 | +0.035 ± 0.046 | -0.006 ± 0.042 |
| 51a | P6 within − cross | – | – | – | – | – |
| 51a | within − cross, room fields removed | – | – | – | – | – |
| 51a | P9 βJ₀/n (upper bound) | 0.73 | 0.73 | 0.75 | – | – |
| 51b | P1 room ΔH (median) | – | – | – | – | – |
| 51b | P5 field R² | 0.61 | 0.61 | 0.66 | 0.52 | 0.58 |
| 51b | P6 exposure slope | +0.008 ± 0.006 | +0.010 ± 0.006 | +0.017 ± 0.006 | +0.008 ± 0.006 | +0.013 ± 0.006 |
| 51b | P6 within − cross | – | – | – | – | – |
| 51b | within − cross, room fields removed | – | – | – | – | – |
| 51b | P9 βJ₀/n (upper bound) | 0.65 | 0.65 | 0.70 | – | – |
| 51c | P1 room ΔH (median) | -0.071 | -0.074 | -0.083 | -0.049 | -0.061 |
| 51c | P5 field R² | 0.70 | 0.70 | 0.69 | 0.62 | 0.60 |
| 51c | P6 exposure slope | +0.010 ± 0.004 | +0.011 ± 0.004 | +0.006 ± 0.004 | +0.011 ± 0.004 | +0.008 ± 0.004 |
| 51c | P6 within − cross | 0.069 | 0.068 | 0.080 | 0.076 | 0.090 |
| 51c | within − cross, room fields removed | 0.069 | 0.068 | 0.080 | 0.076 | 0.090 |
| 51c | P9 βJ₀/n (upper bound) | 0.60 | 0.60 | 0.63 | – | – |
| 51d | P1 room ΔH (median) | – | – | – | – | – |
| 51d | P5 field R² | 0.77 | 0.77 | 0.79 | 0.73 | 0.74 |
| 51d | P6 exposure slope | +0.038 ± 0.014 | +0.034 ± 0.014 | +0.015 ± 0.012 | +0.034 ± 0.014 | +0.014 ± 0.011 |
| 51d | P6 within − cross | – | – | – | – | – |
| 51d | within − cross, room fields removed | – | – | – | – | – |
| 51d | P9 βJ₀/n (upper bound) | 0.44 | 0.44 | 0.35 | – | – |
| 51e | P1 room ΔH (median) | – | – | – | – | – |
| 51e | P5 field R² | 0.94 | 0.94 | 0.95 | 0.89 | 0.87 |
| 51e | P6 exposure slope | – | – | – | – | – |
| 51e | P6 within − cross | – | – | – | – | – |
| 51e | within − cross, room fields removed | – | – | – | – | – |
| 51e | P9 βJ₀/n (upper bound) | 0.35 | 0.35 | 0.12 | – | – |

Style-residualized runs report P1/P2/P5–P7 only (goal fields are not defined in that space). Data: `data/processed/H01-emergent-superagents-exist/r1b/<instrument>/explore.json`, `r1b/compare.json`.
<!-- /R1B -->
