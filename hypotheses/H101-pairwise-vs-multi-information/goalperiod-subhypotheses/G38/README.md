# H101 × G38: goal period #38

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** goal #38 · regime III · units 38a, 38b, 38c, 38d, 38e · active agents per day (median) 10, 9, 12, 11.5, 12 · 85409 item-subset rows.

## Why this period
Eligible for the replication layer (a day with ≥ 3 active agents and ≥ 30 convention items).

## Prediction
*The card's rule, written 2026-10-04 20:24 UTC before any H101 statistic, read through Amendment A1 (20:37 UTC, after the synthetic, before real data); this folder was written after the run and copies it.* Pairwise sufficiency after field removal ρ_F ≥ 0.9 (HH322). A1: ρ_F ≥ 0.9 cannot exclude a planted group term, so it is *descriptive*; a unit is a higher-order candidate only if ρ_F < 0.8, the remainder z ≥ 2.33 against the pairwise bootstrap and r_HO exceeds the heterogeneous-field reference (verdict *failed* for the HH). Units with median N_d < 6 have no power (A1).

## Result

| Unit | N_d | I_N (nats/item) | I₂/I_N raw | φ (field share) | ρ_F | r_HO | z (remainder) | field-ref r_HO | class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 38a | 10 | 0.208 | 0.955 | 0.215 | 0.954 | 0.036 | 15.4 | 0.077 | pairs + fields |
| 38b | 9 | 0.242 | 0.950 | 0.122 | 0.952 | 0.042 | 10.1 | 0.035 | pairs + fields (remainder above field ref.) |
| 38c | 12 | 0.194 | 0.861 | 0.116 | 0.892 | 0.095 | 6.5 | 0.105 | partial (0.8-0.9) |
| 38d | 11.5 | 0.268 | 0.922 | 0.175 | 0.938 | 0.051 | 10.9 | 0.108 | pairs + fields |
| 38e | 12 | 0.250 | 0.915 | 0.137 | 0.928 | 0.062 | 11.6 | 0.047 | pairs + fields (remainder above field ref.) |

Projects (artifact markers; days pooled on agents active every day, so the agent-day field is not removed):

| Unit | items | I_N | ρ_F | r_HO | z | class |
| --- | --- | --- | --- | --- | --- | --- |
| 38a | 993 | 0.315 | 0.983 | 0.016 | 0.8 | pairs + fields |

Data: `data/processed/H101-pairwise-vs-multi-information/results/units_conv_classed.parquet`, `units_proj.parquet`.

## Scorecard (period-specific axes)
C: multi-information against the independent bootstrap; remainder against the pairwise bootstrap. H: pairwise + uniform field against the heterogeneous-field reference. F: power by N (A1).
