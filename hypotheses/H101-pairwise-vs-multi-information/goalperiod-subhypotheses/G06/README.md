# H101 × G06: goal period #6

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #6 · regime I · units 6a, 6b · active agents per day (median) 4, 4 · 2068 item-subset rows.

## Why this period
Eligible for the replication layer (a day with ≥ 3 active agents and ≥ 30 convention items).

## Prediction
*The card's rule, written 2026-10-04 20:24 UTC before any H101 statistic, read through Amendment A1 (20:37 UTC, after the synthetic, before real data); this folder was written after the run and copies it.* Pairwise sufficiency after field removal ρ_F ≥ 0.9 (HH322). A1: ρ_F ≥ 0.9 cannot exclude a planted group term, so it is *descriptive*; a unit is a higher-order candidate only if ρ_F < 0.8, the remainder z ≥ 2.33 against the pairwise bootstrap and r_HO exceeds the heterogeneous-field reference (verdict *failed* for the HH). Units with median N_d < 6 have no power (A1).

## Result

| Unit | N_d | I_N (nats/item) | I₂/I_N raw | φ (field share) | ρ_F | r_HO | z (remainder) | field-ref r_HO | class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 6a | 4 | 0.042 | 1.161 | 0.867 | 2.224 | -0.163 | -3.1 | 0.210 | no power (N < 6) |
| 6b | 4 | 0.064 | 0.987 | 0.200 | 0.988 | 0.010 | 0.3 | -0.027 | no power (N < 6) |

Data: `data/processed/H101-pairwise-vs-multi-information/results/units_conv_classed.parquet`, `units_proj.parquet`.

## Scorecard (period-specific axes)
C: multi-information against the independent bootstrap; remainder against the pairwise bootstrap. H: pairwise + uniform field against the heterogeneous-field reference. F: power by N (A1).
