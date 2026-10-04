# H86 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-20)

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** regime I · units 31a, 31b, 31c, 31d.

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
| 31a | 11 | 0.22 / 0.11 | -0.117 / -0.128 | 0.005 / 0.000 | -0.001 (0.64) | 0.09 / 0.01 | – | – |
| 31b | 12 | 0.91 / 0.83 | -0.021 / -0.031 | -0.001 / -0.001 | -0.001 (0.62) | -0.02 / -0.02 | – | – |
| 31c | 11 | 0.47 / 0.44 | -0.204 / -0.216 | -0.004 / -0.004 | -0.004 (0.60) | -0.04 / -0.04 | – | – |
| 31d | 11 | 1.27 / 1.27 | 0.007 / 0.007 | 0.010 / 0.010 | 0.010 (0.02) | 0.11 / 0.11 | -0.09 | – |

- **Verdict: descriptive** (gauge rule). The HH's Taylor clause fails here as everywhere: across agents b is near or below 1 and c_T near or below 0.

## Scorecard (period-specific axes)
- Replication point: informs C (shared share vs the shift null) and I (consistency across units) in the main card.
