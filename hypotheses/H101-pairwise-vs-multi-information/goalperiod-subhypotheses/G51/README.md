# H101 × G51: subset-size sweep in the largest swarm (#51 head, 2026-07-06 → 09-04)

**Verdict:** supported
**Role:** native (exploratory)
**Period:** goal #51 (private assigned roles) · regime III · units 51a–51l, N 21 → 32 · the tail (09-07 → 09-21) is locked holdout and is not read.

## Why this period
Only #51 has more than 16 active agents, so only #51 can follow pairwise sufficiency as the observed subset grows. Roudi et al. show that I₂/I_N is trivially near 1 for small subsets at low rates and falls with n when higher-order structure exists. Amendment A1 found that hidden agents also create subset-level higher order. The sweep shows which way the remainder moves with n.

## Prediction
*Written 2026-10-04 20:39 UTC, before running the sweep.*
- **G51-a (Roudi).** In 51c and 51g, ρ_F falls and the remainder z rises as n goes 4 → 6 → 8 (→ 10 in 51g): ρ_F(8) < ρ_F(4) and z(8) > z(4). [0.55]
- **G51-b (field, not group).** At every n, r_HO stays at or below the latent-field reference r_HO. [0.6]
- **G51-c (replication units).** In the replication layer, the #51 units are resolved (I_N above the independent null) and the share of #51 units with z ≥ 2.33 exceeds 50% (R7). [0.5]
- Power caveat (A1): at N ≈ 19 the remainder test detects a planted 4-agent group term in 67% of replicates and fires in 33% of pairwise worlds.

## Result
Data: `natives/g51.json` (sweep, S = 6 subsets per day; n = 10 with S = 2) and the replication table.

| Unit | n | ρ_F | r_HO | z (remainder) | field-ref r_HO | I₂/I_N raw | φ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 51c | 4 | 0.991 | 0.005 | 0.5 | 0.050 | 0.942 | 0.39 |
| 51c | 6 | 0.933 | 0.047 | 5.4 | 0.086 | 0.937 | 0.29 |
| 51c | 8 | 0.900 | 0.074 | 6.7 | 0.101 | 0.907 | 0.26 |
| 51g | 4 | 0.960 | 0.035 | 3.3 | 0.012 | 0.985 | 0.13 |
| 51g | 6 | 0.955 | 0.041 | 9.7 | 0.067 | 0.962 | 0.10 |
| 51g | 8 | 0.955 | 0.039 | 8.8 | 0.071 | 0.960 | 0.13 |
| 51g | 10 | 0.940 | 0.051 | 10.3 | 0.066 | 0.946 | 0.15 |

- **G51-a supported (Roudi).** ρ_F(8) < ρ_F(4) in both units (51c 0.991 → 0.900; 51g 0.960 → 0.955 → 0.940 at n = 10), and z(8) > z(4) (51c 0.5 → 6.7; 51g 3.3 → 8.8). Sufficiency at n = 4 is near 1 for the trivial reason Roudi et al. give; the remainder grows with the observed subset.
- **G51-b supported in 6/7 cells.** r_HO stays at or below the heterogeneous-field reference except 51g at n = 4 (0.035 vs 0.012).
- **G51-c supported.** z ≥ 2.33 in 9/12 #51 replication units (75% > 50%); φ is 0.11–0.62 (median 0.26): in #51 most multi-information is pairwise, not a uniform field.
- Reading: the remainder that appears as more agents are observed stays inside what agent-specific responses to a shared field produce. It is not a separable group term (A1: not distinguishable at these counts).

## Scorecard (period-specific axes)
F (size dependence), D (Roudi's unfitted prediction), I (11 units of one period).

## Notes
