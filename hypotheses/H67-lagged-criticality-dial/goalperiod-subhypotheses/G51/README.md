# H67 × G51: the size sweep of the private-role era (non-holdout head, 2026-07-06 → 09-04)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** goal #51 (maximize your private assigned role) · regime III · one main room (#general; #focus 08-05 → 08-21) · units 51a–51l, N 21 → 32 in 11 steps at a fixed goal and hours. The tail (09-07 → 09-21) is locked holdout and is not read.

## Why this period
The only long sweep of headcount at a fixed goal and scaffold. If the swarm approached a critical point as it grew, g_lag would climb toward 1 with N. Read-out budgets (dilution, burial) predict the opposite: per-read coupling falls as messages per call grow. H42 found its world-B n_x collapses to 0 from 51h on, as read-out lags grow.

## Prediction
*Written 2026-10-04 19:35 UTC, before running on this period. Seen: H03's, H25's and H42's #51 size results (n̂ falls with N; talk per-pair correlation falls; world-B n_x → 0 from 51h); no H67 number.*
- **N51a (no approach to criticality):** g_lag upper 95% bound < 0.5 in every 51 unit, and Spearman ρ(g_lag, N) ≤ 0 across units. [0.6]
- **N51b (dilution):** Spearman ρ(J₁*, N) < 0 across units. [0.6]
- **Counts against:** ρ(g_lag, N) > 0.5 with the largest units above 0.5.

## Result
*Run 2026-10-04 ~20:20 UTC.* Unit table under "Replication layer" below.
- **N51a:** every unit's g_lag upper bound is < 0.5 (maximum 0.39, 51h). Spearman ρ(g_lag, N) = 0.06 (p 0.87, 11 units): flat, not ≤ 0 as written. **Half supported** (no approach to criticality; the sign clause misses by 0.06).
- **N51b:** ρ(J₁*, N) = −0.15 (p 0.66). Right sign, not significant. **Failed (underpowered).** Across all 25 regime-III units, ρ(J₁*, N) = −0.59 (p 0.002), but that pools goals.
- **Reading:** g_lag sits at 0.14 [0.11, 0.17] (period pool) across N = 21 → 32. About half of it (0.06–0.10) comes from messages that name the recipient. The swarm does not approach a talk cascade as it grows.


## Replication layer

Period pool (random effects over units): **g_lag = 0.142 [0.111, 0.174]**, J₁* = 0.006 [0.005, 0.008], g_eq (same data) = 0.125, H25 trimmed talk dial = 0.132, H42 world-B n_x = 0.016; named-message part of g_lag = 0.079.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | 21 | 45020 | 0.129 [0.063, 0.202] | 0.006 [0.003, 0.010] | 19.966 | 0.182 | 0.081 | 0.105 |
| 51c | 25 | 107326 | 0.160 [0.118, 0.207] | 0.007 [0.005, 0.009] | 23.782 | 0.079 | 0.084 | 0.000 |
| 51d | 26 | 59928 | 0.075 [0.022, 0.127] | 0.003 [0.001, 0.005] | 24.478 | 0.201 | 0.084 | 0.158 |
| 51e | 27 | 51081 | 0.127 [0.047, 0.215] | 0.005 [0.002, 0.008] | 25.735 | 0.154 | 0.095 | 0.105 |
| 51f | 27 | 71706 | 0.123 [0.040, 0.205] | 0.005 [0.002, 0.008] | 25.706 | 0.104 | 0.088 | 0.158 |
| 51g | 27 | 220023 | 0.147 [0.118, 0.180] | 0.009 [0.007, 0.010] | 17.479 | 0.122 | 0.065 | 0.053 |
| 51h | 27 | 49486 | 0.292 [0.197, 0.393] | 0.013 [0.008, 0.016] | 23.983 | 0.146 | 0.094 | 0.000 |
| 51i | 28 | 19148 | 0.156 [0.020, 0.316] | 0.006 [0.001, 0.013] | 26.885 | 0.030 | 0.062 | 0.000 |
| 51j | 29 | 16807 | 0.196 [0.128, 0.251] | 0.007 [0.005, 0.009] | 27.829 | 0.047 | 0.083 | 0.211 |
| 51k | 30 | 8108 | 0.019 [-0.092, 0.141] | 0.001 [-0.004, 0.006] | 29.348 | 0.083 | 0.067 | 0.158 |
| 51l | 32 | 8571 | 0.152 [0.020, 0.223] | 0.006 [0.001, 0.009] | 30.858 | 0.278 | 0.059 | 0.053 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

### Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).
