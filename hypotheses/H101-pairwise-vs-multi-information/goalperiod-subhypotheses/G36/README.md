# H101 × G36: goal period #36

**Verdict:** descriptive
**Role:** replication (exploratory)
**Period:** goal #36 · regime II · units 36a, 36b, 36c · active agents per day (median) 12, 10, 11 · 32589 item-subset rows.

## Why this period
Eligible for the replication layer (a day with ≥ 3 active agents and ≥ 30 convention items).

## Prediction
*The card's rule, written 2026-10-04 20:24 UTC before any H101 statistic, read through Amendment A1 (20:37 UTC, after the synthetic, before real data); this folder was written after the run and copies it.* Pairwise sufficiency after field removal ρ_F ≥ 0.9 (HH322). A1: ρ_F ≥ 0.9 cannot exclude a planted group term, so it is *descriptive*; a unit is a higher-order candidate only if ρ_F < 0.8, the remainder z ≥ 2.33 against the pairwise bootstrap and r_HO exceeds the heterogeneous-field reference (verdict *failed* for the HH). Units with median N_d < 6 have no power (A1).

## Result

| Unit | N_d | I_N (nats/item) | I₂/I_N raw | φ (field share) | ρ_F | r_HO | z (remainder) | field-ref r_HO | class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 36a | 12 | 0.256 | 0.985 | 0.747 | 0.957 | 0.011 | 1.7 | 0.172 | pairs + fields |
| 36b | 10 | 0.206 | 0.942 | 0.360 | 0.920 | 0.051 | 9.3 | 0.120 | pairs + fields |
| 36c | 11 | 0.161 | 0.933 | 0.670 | 0.863 | 0.045 | 4.4 | 0.160 | partial (0.8-0.9) |

Projects (artifact markers; days pooled on agents active every day, so the agent-day field is not removed):

| Unit | items | I_N | ρ_F | r_HO | z | class |
| --- | --- | --- | --- | --- | --- | --- |
| 36a | 273 | 0.173 | -0.080 | 0.081 | 0.9 | low rho_F (within field ref.) |
| 36b | 145 | 0.070 | 1.346 | -0.277 | -0.7 | unresolved |
| 36c | 220 | 0.069 | 1.756 | -0.478 | -1.7 | unresolved |

Data: `data/processed/H101-pairwise-vs-multi-information/results/units_conv_classed.parquet`, `units_proj.parquet`.

## Scorecard (period-specific axes)
C: multi-information against the independent bootstrap; remainder against the pairwise bootstrap. H: pairwise + uniform field against the heterogeneous-field reference. F: power by N (A1).
