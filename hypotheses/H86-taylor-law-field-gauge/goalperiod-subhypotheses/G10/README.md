# H86 × G10: Complete as many games as you can in a week! (2025-08-18 → 2025-08-22)

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** regime I · units 10a, 10b.

## Why this period
A replication point for the gauge (layer 1): every eligible unit gets the same Taylor fit and shared-field coefficient, raw and trimmed, so units are comparable points on a field-strength axis.

## Prediction
*Written 2026-10-04 20:05 UTC in the card (templated per unit; the per-period verdict rule in `analysis/write_period_cards.py` was fixed after the card-level run, 2026-10-04 20:22 UTC).*
- Raw activity: Taylor b ≈ 2 with c_T > 0 (HH, P1). Trimmed: b ≤ 1.3 (HH, P2; prior 0.25).
- Shared field: c_× falls under trimming (regime III by 60–90%, regime I < 40%); trimmed φ < 0.3 (no unaccounted shared field).
- *Counts against:* trimmed φ ≥ 0.5 with the within-day shift null p < 0.05 (P4 kill).

## Result
*Run 2026-10-04 20:16 UTC (`analysis/gauge.py` → `data/processed/H86-taylor-law-field-gauge/replication/gauge.parquet`). Activity = records per 15-min bin; CIs in the parquet (day bootstrap; they under-cover, A2).*

| Unit | agents | b raw / trim | c_T raw / trim | c_× raw / trim | c_×w trim (shift p) | φ raw / trim | φ msg trim | b commit (60 min) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10a | 7 | 2.45 / 2.88 | 1.573 / 1.868 | 0.249 / 0.258 | 0.258 (0.02) | 0.38 / 0.40 | 0.08 | – |
| 10b | 7 | 1.13 / 0.91 | -0.128 / -0.150 | 0.042 / 0.039 | 0.037 (0.02) | 0.35 / 0.35 | 0.15 | – |

- **Verdict: mixed** (gauge rule). The HH's Taylor clause fails here as everywhere: across agents b is near or below 1 and c_T near or below 0.

## Scorecard (period-specific axes)
- Replication point: informs C (shared share vs the shift null) and I (consistency across units) in the main card.
