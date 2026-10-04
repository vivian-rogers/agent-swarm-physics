# H86 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-24)

**Verdict:** supported
**Role:** replication (exploratory)
**Period:** regime III · units 38a, 38b, 38c, 38d, 38e.

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
| 38a | 12 | 0.18 / 0.06 | -0.109 / -0.114 | 0.012 / 0.003 | 0.003 (0.04) | 0.13 / 0.03 | 0.18 | 1.54 |
| 38b | 12 | 1.37 / -0.20 | 0.174 / -0.102 | 0.337 / -0.001 | -0.000 (0.54) | 0.77 / -0.02 | 0.09 | – |
| 38c | 13 | -0.59 / -0.65 | -0.446 / -0.581 | 0.005 / 0.005 | 0.005 (0.18) | 0.04 / 0.05 | 0.18 | – |
| 38d | 13 | -1.15 / -1.88 | -0.628 / -0.593 | 0.009 / 0.009 | 0.004 (0.10) | 0.07 / 0.06 | 0.23 | – |
| 38e | 14 | -0.96 / -0.57 | -0.525 / -0.235 | 0.010 / -0.003 | -0.002 (0.78) | 0.06 / -0.02 | -0.14 | – |

- **Verdict: supported** (gauge rule). The HH's Taylor clause fails here as everywhere: across agents b is near or below 1 and c_T near or below 0.

## Scorecard (period-specific axes)
- Replication point: informs C (shared share vs the shift null) and I (consistency across units) in the main card.
