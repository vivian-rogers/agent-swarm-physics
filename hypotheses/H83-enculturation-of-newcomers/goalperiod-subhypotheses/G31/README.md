# H83 × G31: newcomers joining goal period #31 (2026-02-16 → 2026-02-20)

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** regime I · up to 12 agents · units 31a, 31b, 31c, 31d · non-holdout days 5. Joins: Claude Sonnet 4.6 (2026-02-18).

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
| Claude Sonnet 4.6 | +0.032 | -0.035 | -0.077 | -0.002 | -8.209 | 1472 | failed |

- **Templated verdict:** failed. One join has no power alone; see the card for the pooled test.

## Scorecard (period-specific axes)
- Replication point only (layer 1): informs C and I in the main card.
