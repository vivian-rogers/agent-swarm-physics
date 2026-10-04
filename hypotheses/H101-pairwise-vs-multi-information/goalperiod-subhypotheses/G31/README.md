# H101 × G31: goal period #31

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** goal #31 · regime I · units 31a, 31b, 31c, 31d · active agents per day (median) 11, 12, 11, 11 · 37209 item-subset rows.

## Why this period
Eligible for the replication layer (a day with ≥ 3 active agents and ≥ 30 convention items).

## Prediction
*The card's rule, written 2026-10-04 20:24 UTC before any H101 statistic, read through Amendment A1 (20:37 UTC, after the synthetic, before real data); this folder was written after the run and copies it.* Pairwise sufficiency after field removal ρ_F ≥ 0.9 (HH322). A1: ρ_F ≥ 0.9 cannot exclude a planted group term, so it is *descriptive*; a unit is a higher-order candidate only if ρ_F < 0.8, the remainder z ≥ 2.33 against the pairwise bootstrap and r_HO exceeds the heterogeneous-field reference (verdict *failed* for the HH). Units with median N_d < 6 have no power (A1).

## Result

| Unit | N_d | I_N (nats/item) | I₂/I_N raw | φ (field share) | ρ_F | r_HO | z (remainder) | field-ref r_HO | class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 31a | 11 | 0.202 | 0.973 | 0.888 | 0.792 | 0.023 | 3.6 | 0.173 | low rho_F (within field ref.) |
| 31b | 12 | 0.201 | 0.963 | 0.790 | 0.827 | 0.037 | 4.7 | 0.242 | partial (0.8-0.9) |
| 31c | 11 | 0.154 | 0.982 | 0.849 | 0.897 | 0.016 | 2.5 | 0.239 | partial (0.8-0.9) |
| 31d | 11 | 0.252 | 0.972 | 0.787 | 0.905 | 0.020 | 4.5 | 0.194 | pairs + fields |

Projects (artifact markers; days pooled on agents active every day, so the agent-day field is not removed):

| Unit | items | I_N | ρ_F | r_HO | z | class |
| --- | --- | --- | --- | --- | --- | --- |
| 31a | 297 | 0.034 | – | -1.193 | -1.7 | unresolved |
| 31b | 86 | 0.096 | – | -0.057 | -0.4 | unresolved |
| 31c | 154 | 0.231 | 0.519 | 0.399 | 3.6 | higher-order candidate |

Data: `data/processed/H101-pairwise-vs-multi-information/results/units_conv_classed.parquet`, `units_proj.parquet`.

## Scorecard (period-specific axes)
C: multi-information against the independent bootstrap; remainder against the pairwise bootstrap. H: pairwise + uniform field against the heterogeneous-field reference. F: power by N (A1).
