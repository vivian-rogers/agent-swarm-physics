# H86 × G20: Start a Substack and join the blogosphere (2025-11-17 → 2025-11-28)

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** regime I · units 20a, 20b, 20c, 20d.

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
| 20a | 8 | 1.26 / 1.33 | 0.060 / 0.049 | 0.031 / 0.028 | 0.022 (0.02) | 0.31 / 0.32 | 0.54 | – |
| 20b | 9 | 1.57 / 1.57 | 0.026 / 0.026 | 0.001 / 0.001 | 0.001 (0.34) | 0.07 / 0.07 | – | – |
| 20c | 9 | 0.06 / -0.18 | -0.066 / -0.067 | 0.009 / 0.005 | -0.000 (0.64) | 0.24 / 0.16 | 1.03 | – |
| 20d | 10 | 0.21 / 0.30 | -0.181 / -0.146 | 0.044 / 0.041 | 0.015 (0.04) | 0.27 / 0.28 | 0.41 | – |

- **Verdict: mixed** (gauge rule). The HH's Taylor clause fails here as everywhere: across agents b is near or below 1 and c_T near or below 0.

## Scorecard (period-specific axes)
- Replication point: informs C (shared share vs the shift null) and I (consistency across units) in the main card.
