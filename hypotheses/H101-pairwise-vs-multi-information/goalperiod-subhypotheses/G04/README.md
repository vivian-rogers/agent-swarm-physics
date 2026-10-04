# H101 × G04: goal period #4

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #4 · regime I · units 4a, 4b, 4c, 4d · active agents per day (median) 4, 4, 4, 4 · 5325 item-subset rows.

## Why this period
Eligible for the replication layer (a day with ≥ 3 active agents and ≥ 30 convention items).

## Prediction
*The card's rule, written 2026-10-04 20:24 UTC before any H101 statistic, read through Amendment A1 (20:37 UTC, after the synthetic, before real data); this folder was written after the run and copies it.* Pairwise sufficiency after field removal ρ_F ≥ 0.9 (HH322). A1: ρ_F ≥ 0.9 cannot exclude a planted group term, so it is *descriptive*; a unit is a higher-order candidate only if ρ_F < 0.8, the remainder z ≥ 2.33 against the pairwise bootstrap and r_HO exceeds the heterogeneous-field reference (verdict *failed* for the HH). Units with median N_d < 6 have no power (A1).

## Result

| Unit | N_d | I_N (nats/item) | I₂/I_N raw | φ (field share) | ρ_F | r_HO | z (remainder) | field-ref r_HO | class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4a | 4 | 0.132 | 0.905 | 0.497 | 0.851 | 0.075 | 4.2 | 0.101 | no power (N < 6) |
| 4b | 4 | 0.038 | 1.063 | 0.447 | 0.937 | 0.035 | 0.3 | 0.074 | no power (N < 6) |
| 4c | 4 | 0.129 | 0.965 | 0.572 | 0.957 | 0.018 | 1.5 | 0.065 | no power (N < 6) |
| 4d | 4 | 0.177 | 0.963 | 0.694 | 0.705 | 0.090 | 2.8 | 0.043 | no power (N < 6) |

Projects (artifact markers; days pooled on agents active every day, so the agent-day field is not removed):

| Unit | items | I_N | ρ_F | r_HO | z | class |
| --- | --- | --- | --- | --- | --- | --- |
| 4c | 66 | 0.027 | – | -0.115 | -1.0 | no power (N < 6) |

Data: `data/processed/H101-pairwise-vs-multi-information/results/units_conv_classed.parquet`, `units_proj.parquet`.

## Scorecard (period-specific axes)
C: multi-information against the independent bootstrap; remainder against the pairwise bootstrap. H: pairwise + uniform field against the heterogeneous-field reference. F: power by N (A1).
