# H101 × G20: goal period #20

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** goal #20 · regime I · units 20a, 20b, 20c, 20d · active agents per day (median) 8, 9, 9, 10 · 39763 item-subset rows.

## Why this period
Eligible for the replication layer (a day with ≥ 3 active agents and ≥ 30 convention items).

## Prediction
*The card's rule, written 2026-10-04 20:24 UTC before any H101 statistic, read through Amendment A1 (20:37 UTC, after the synthetic, before real data); this folder was written after the run and copies it.* Pairwise sufficiency after field removal ρ_F ≥ 0.9 (HH322). A1: ρ_F ≥ 0.9 cannot exclude a planted group term, so it is *descriptive*; a unit is a higher-order candidate only if ρ_F < 0.8, the remainder z ≥ 2.33 against the pairwise bootstrap and r_HO exceeds the heterogeneous-field reference (verdict *failed* for the HH). Units with median N_d < 6 have no power (A1).

## Result

| Unit | N_d | I_N (nats/item) | I₂/I_N raw | φ (field share) | ρ_F | r_HO | z (remainder) | field-ref r_HO | class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20a | 8 | 0.316 | 0.958 | 0.782 | 0.836 | 0.036 | 3.0 | 0.178 | partial (0.8-0.9) |
| 20b | 9 | 0.192 | 0.922 | 0.596 | 0.884 | 0.047 | 3.1 | 0.119 | partial (0.8-0.9) |
| 20c | 9 | 0.214 | 0.919 | 0.546 | 0.863 | 0.062 | 12.4 | 0.188 | partial (0.8-0.9) |
| 20d | 10 | 0.260 | 0.955 | 0.711 | 0.845 | 0.045 | 10.6 | 0.175 | partial (0.8-0.9) |

Data: `data/processed/H101-pairwise-vs-multi-information/results/units_conv_classed.parquet`, `units_proj.parquet`.

## Scorecard (period-specific axes)
C: multi-information against the independent bootstrap; remainder against the pairwise bootstrap. H: pairwise + uniform field against the heterogeneous-field reference. F: power by N (A1).
