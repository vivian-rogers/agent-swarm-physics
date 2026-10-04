# H83 × G19: newcomers joining goal period #19 (2025-11-03 → 2025-11-14)

**Verdict:** supported
**Role:** replication (exploratory)
**Period:** regime I · up to 8 agents · units 19a, 19b · non-holdout days 10. Joins: GPT-5.1 (2025-11-14).

## Why this period
A replication point for the common estimator (layer 1): every eligible join gets the same statistic.

## Prediction
*Written 2026-10-04 20:34 UTC, before running on this period. Templated replication prediction (layer 1), the same for every join.*
- **Observable:** the enculturation index ΔG (O1): the newcomer's change in mean statement cosine with the veterans' same-day centroid from window E (tenure days 2–4) to window L (8–14), minus the same change of the veterans observed on the same days. Vectors: DQ5 `style_resid_period` (bge primary, gte check), goal and kickoff span projected out.
- **Prediction:** the newcomer starts below the veterans (Ḡ_E < 0) and closes part of the gap (ΔG > 0). Where a family baseline exists, the family signature fades (ΔK < 0). Style: ΔS < 0.
- **Verdict rule (per join, templated):** supported if ΔG > 0 and Ḡ_E < 0; failed if ΔG ≤ 0; mixed otherwise. One join has no power on its own (synthetic null SD of a single join ≈ 0.05); the card-level test pools the joins.
- *Counts against:* ΔG ≤ 0 (the newcomer converges only as far as the field pulls everyone).

## Result
*Run 2026-10-04 20:36 UTC (`analysis/replication.py`, `analysis/natives.py`) → `data/processed/H83-enculturation-of-newcomers/replication/replication.json`, `natives/natives.json`.*

| Join | Ḡ_E | ΔG (bge) | ΔG (gte) | ΔK | ΔS (style) | veteran items read, days 1–7 | templated |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GPT-5.1 | -0.049 | +0.054 | -0.011 | -0.023 | -5.819 | 2117 | supported |

- **Templated verdict:** supported. One join has no power alone; see the card for the pooled test.

## Scorecard (period-specific axes)
- Replication point only (layer 1): informs C and I in the main card.
