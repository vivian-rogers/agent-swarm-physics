# H98 × G41: #41 (2026-05-11 → 05-15)

**Verdict:** descriptive
**Role:** exploratory (replication, contrast)
**Period:** regime III · shared objective · 15 agents · #best / #rest · 5 days.

## Why this period
A shared-goal regime-III week: every agent works under one goal, so the uniform field should dominate the static configuration. It places a contrast point on the (R, b) phase diagram next to the #51 units.

## Prediction
*Written 2026-10-04 20:46 UTC, before running on this period.* From card P1–P3: R(unit 41) is below every counted #51 unit's R; b_ex is positive and < 0.5; W shows no collective switching (p_W ≥ 0.05), except that two-room weeks may carry a room-level day field (H22 saw W > 1 in 38a and #44 from per-room day fields). Verdict rule: descriptive (contrast point).

## Result
*Run 2026-10-04 20:46 UTC; primary variant style_resid_period × bge.*

| R [95% CI] | b_ex [95% CI] | W | R without style removal (white32, bge) |
| --- | --- | --- | --- |
| 0.53 [0.31, 0.68] | 0.55 [0.45, 0.62] | 3.35 (p 0.003; gte 2.97) | see `results/units.parquet` |

- R is below every counted #51 unit (0.67–0.73), as predicted.
- Two rooms: room-level day field. b_ex ≥ 0.5 is the only breach of P2's bound.
