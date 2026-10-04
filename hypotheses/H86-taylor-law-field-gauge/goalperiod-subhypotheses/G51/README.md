# H86 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-04)

**Verdict:** supported
**Role:** replication (exploratory)
**Period:** regime III · units 51a, 51b, 51c, 51d, 51e, 51f, 51g, 51h, 51i, 51j, 51k, 51l.

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
| 51a | 21 | 1.16 / 0.22 | 0.211 / -0.152 | 0.370 / 0.006 | -0.001 (0.76) | 0.66 / 0.05 | 0.05 | 1.19 |
| 51b | 24 | 1.07 / – | -0.287 / – | 0.102 / – | – (–) | 0.31 / – | – | – |
| 51c | 25 | 0.69 / 0.62 | -0.183 / -0.204 | 0.049 / 0.004 | 0.001 (0.22) | 0.26 / 0.03 | 0.11 | 1.26 |
| 51d | 26 | 0.96 / 0.88 | -0.042 / -0.055 | 0.021 / 0.024 | 0.023 (0.02) | 0.09 / 0.12 | 0.26 | 1.27 |
| 51e | 27 | 1.29 / 0.84 | 0.142 / -0.056 | 0.205 / 0.005 | 0.002 (0.08) | 0.58 / 0.04 | 0.06 | 1.22 |
| 51f | 27 | 0.89 / 0.90 | -0.107 / -0.110 | 0.007 / 0.007 | 0.006 (0.02) | 0.04 / 0.04 | 0.20 | 1.26 |
| 51g | 27 | 0.81 / 0.81 | -0.262 / -0.288 | 0.013 / 0.012 | 0.008 (0.02) | 0.04 / 0.04 | 0.08 | 1.26 |
| 51h | 27 | 1.03 / 1.07 | -0.111 / -0.064 | 0.013 / 0.018 | 0.004 (0.04) | 0.07 / 0.12 | 0.23 | 1.32 |
| 51i | 28 | 1.06 / 1.34 | -0.049 / -0.029 | 0.007 / -0.000 | 0.001 (0.30) | 0.04 / -0.00 | 0.10 | – |
| 51j | 29 | 0.77 / 1.04 | -0.185 / -0.023 | 0.023 / 0.007 | 0.007 (0.02) | 0.12 / 0.05 | 0.01 | – |
| 51k | 31 | 1.14 / – | -0.030 / – | 0.028 / – | – (–) | 0.12 / – | – | – |
| 51l | 32 | 1.14 / 1.23 | -0.094 / -0.070 | 0.008 / 0.005 | 0.005 (0.06) | 0.06 / 0.05 | – | – |

- **Verdict: supported** (gauge rule). The HH's Taylor clause fails here as everywhere: across agents b is near or below 1 and c_T near or below 0.

## Scorecard (period-specific axes)
- Replication point: informs C (shared share vs the shift null) and I (consistency across units) in the main card.
