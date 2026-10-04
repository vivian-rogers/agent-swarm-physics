# H101 × G25: goal period #25

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** goal #25 · regime I · units 25 · active agents per day (median) 10 · 28005 item-subset rows.

## Why this period
Eligible for the replication layer (a day with ≥ 3 active agents and ≥ 30 convention items).

## Prediction
*The card's rule, written 2026-10-04 20:24 UTC before any H101 statistic, read through Amendment A1 (20:37 UTC, after the synthetic, before real data); this folder was written after the run and copies it.* Pairwise sufficiency after field removal ρ_F ≥ 0.9 (HH322). A1: ρ_F ≥ 0.9 cannot exclude a planted group term, so it is *descriptive*; a unit is a higher-order candidate only if ρ_F < 0.8, the remainder z ≥ 2.33 against the pairwise bootstrap and r_HO exceeds the heterogeneous-field reference (verdict *failed* for the HH). Units with median N_d < 6 have no power (A1).

## Result

| Unit | N_d | I_N (nats/item) | I₂/I_N raw | φ (field share) | ρ_F | r_HO | z (remainder) | field-ref r_HO | class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 25 | 10 | 0.205 | 0.945 | 0.790 | 0.823 | 0.037 | 9.7 | 0.192 | partial (0.8-0.9) |

Projects (artifact markers; days pooled on agents active every day, so the agent-day field is not removed):

| Unit | items | I_N | ρ_F | r_HO | z | class |
| --- | --- | --- | --- | --- | --- | --- |
| 25 | 265 | 0.214 | 0.999 | 0.001 | 0.0 | pairs + fields |

Data: `data/processed/H101-pairwise-vs-multi-information/results/units_conv_classed.parquet`, `units_proj.parquet`.

## Scorecard (period-specific axes)
C: multi-information against the independent bootstrap; remainder against the pairwise bootstrap. H: pairwise + uniform field against the heterogeneous-field reference. F: power by N (A1).
