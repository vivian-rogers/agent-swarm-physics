# H105 × G12: debate tournament (#11 → #12a): native debate-phase test + primary pair

**Verdict:** mixed
**Role:** native
**Period:** regime I · mode M (team debates) · 7 agents · one room · A = #12a days 2–4 (09-02 … 09-04); F = #11 (08-25 … 08-29). DQ6 `ground_truth_labels` give the debate phases (pre / debate / post) with times.

## Why this period
H10 found agents go on-goal together in #12 (pairwise signal correlation 0.20 → 0.64). The debate rounds are a known, timed external schedule. If the excess occupancy variance is the schedule (rival R5′) and not coupling (R5), regressing occupancy on the schedule removes it.

## Prediction
*Written 2026-10-04 ~20:41 UTC, before running on this period.*
- **N2:** regressing the composition-adjusted occupancy deviation p_t − μ_t on each window's debate-phase share removes ≥ 30% of the excess variance V_A − V_A^pred. Credence 0.4.
- Counts against: < 10% removed.
- If V_A ≤ V_A^pred (no excess), N2 is n/a.

*Replication (primary pair), templated from the card (~20:27 UTC) and Amendment 1 (~20:51 UTC): P1 and P3 descriptive; P2 by the calibrated rule.*

## Result
### Native (N2): mixed (model-dependent)
| Statistic | bge-small | gte-modernbert |
| --- | --- | --- |
| V_A observed / tilt-predicted | 0.121 / 0.247 | 0.112 / 0.031 |
| excess V_A − V_A^pred | −0.125 (none) | +0.081 |
| share of excess removed by the debate-phase share | n/a | 0.50 |
| occupancy coefficient on debate-phase share | +0.99 | +0.84 |

The occupancy rises with the scheduled debate phases in both models (coefficient ≈ +0.9 per unit phase share). Under gte the schedule removes 50% of the excess variance (N2 supported); under bge there is no excess to remove (N2 n/a), because the tilt with the free week's J₂ already predicts more variance than observed. Data: `data/processed/H105-two-state-goal-order/natives/G12.json`.

### Replication (primary pair #11 → #12a): descriptive
| Statistic | bge-small | gte-modernbert |
| --- | --- | --- |
| occupancy p_F → p_A | 0.021 → 0.442 | 0.039 → 0.458 |
| loop gain g₂ F → A | 0.10 → 0.74 | 0.01 → 0.72 |
| ρ_V [90% CI] | −0.71 [−1.23, −0.61] | +1.28 [+0.31, +2.44] |
| P1 rule outcome | failed (variance below the tilt) | failed (variance above the tilt) |
| logit slope s | −0.60 | −0.45 |

- **Collective switching:** g₂ rises from ≈ 0.1 to 0.74 in both models: agents go on-goal together in #12a. The matched bootstrap puts this Δg₂ at the 0.92 quantile of the tilt (H) and 0.87 of R5, so even this large rise is not identifiable as a coupling change.
- **ρ_V flips sign between models** (−0.71 vs +1.28), so P1 is not stable here; the calibrated quantiles are 0.25 (H) and 0.24 (R5).
- **Who moves:** s < 0 in both models (agents with higher free-week on-goal rates move less, as H10's common target). Calibrated P2: s at the 0.14 quantile of H and 0.21 of R2 → inconclusive.
- Day trajectory (p_d, V_d obs / pred): 09-02 0.55, 0.109/0.248; 09-03 0.29, 0.127/0.204; 09-04 0.49, 0.128/0.250. Transverse control: p⊥ 0.024 → 0.008, ρ_V⊥ −0.07.
- Data: `NE34/pairs_all_configs.parquet`, `G12/results.json`.

## Scorecard (period-specific axes)
- G: debate phases from DQ6 ground truth track the occupancy (+0.9 per unit phase share).
- E/H: the scheduled field (R5′) explains half of the excess under gte; the coupling rival cannot be separated from it.

## Notes
