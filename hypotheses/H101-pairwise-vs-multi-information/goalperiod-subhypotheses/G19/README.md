# H101 × G19: goal period #19

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** goal #19 · regime I · units 19a, 19b · active agents per day (median) 7, 8 · 29040 item-subset rows.

## Why this period
Eligible for the replication layer (a day with ≥ 3 active agents and ≥ 30 convention items).

## Prediction
*The card's rule, written 2026-10-04 20:24 UTC before any H101 statistic, read through Amendment A1 (20:37 UTC, after the synthetic, before real data); this folder was written after the run and copies it.* Pairwise sufficiency after field removal ρ_F ≥ 0.9 (HH322). A1: ρ_F ≥ 0.9 cannot exclude a planted group term, so it is *descriptive*; a unit is a higher-order candidate only if ρ_F < 0.8, the remainder z ≥ 2.33 against the pairwise bootstrap and r_HO exceeds the heterogeneous-field reference (verdict *failed* for the HH). Units with median N_d < 6 have no power (A1).

## Result

| Unit | N_d | I_N (nats/item) | I₂/I_N raw | φ (field share) | ρ_F | r_HO | z (remainder) | field-ref r_HO | class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 19a | 7 | 0.248 | 0.954 | 0.825 | 0.808 | 0.033 | 8.8 | 0.187 | partial (0.8-0.9) |
| 19b | 8 | 0.213 | 0.954 | 0.785 | 0.884 | 0.025 | 2.8 | 0.212 | partial (0.8-0.9) |

Projects (artifact markers; days pooled on agents active every day, so the agent-day field is not removed):

| Unit | items | I_N | ρ_F | r_HO | z | class |
| --- | --- | --- | --- | --- | --- | --- |
| 19a | 460 | 0.372 | 0.504 | 0.091 | 2.8 | higher-order candidate |

Data: `data/processed/H101-pairwise-vs-multi-information/results/units_conv_classed.parquet`, `units_proj.parquet`.

## Scorecard (period-specific axes)
C: multi-information against the independent bootstrap; remainder against the pairwise bootstrap. H: pairwise + uniform field against the heterogeneous-field reference. F: power by N (A1).
