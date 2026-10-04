# H86 × G18: Reduce global poverty as much as you can (2025-10-20 → 2025-10-31)

**Verdict:** supported
**Role:** replication (exploratory)
**Period:** regime I · units 18a, 18b, 18c.

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
| 18a | 7 | 0.21 / 0.12 | -0.217 / -0.270 | 0.090 / 0.086 | 0.084 (0.02) | 0.31 / 0.29 | 0.59 | – |
| 18b | 8 | 0.79 / 0.89 | -0.057 / -0.029 | 0.024 / 0.016 | 0.017 (0.02) | 0.12 / 0.09 | 0.57 | – |
| 18c | 7 | 0.36 / 0.34 | -0.167 / -0.172 | 0.017 / 0.017 | 0.023 (0.02) | 0.13 / 0.14 | 0.53 | – |

- **Verdict: supported** (gauge rule). The HH's Taylor clause fails here as everywhere: across agents b is near or below 1 and c_T near or below 0.

## Scorecard (period-specific axes)
- Replication point: informs C (shared share vs the shift null) and I (consistency across units) in the main card.
