# H98 × G51: private roles (2026-07-06 → 09-04, non-holdout)

**Verdict:** mixed
**Role:** exploratory (replication + native)
**Period:** regime III · mode: private goals · 21–32 agents · #general, plus #focus 08-05 → 08-21 · 44 non-holdout days. Shared `period_units` splits 51a–51l (roster joins, NE32, NE38, room changes, NE33). The tail 09-07 → 09-21 is held out.

## Why this period
The only period with private, individually assigned roles: a quenched random field per agent, written down in role texts. H22 found real, mostly positive couplings, rival homophily and no collective switching.

## Prediction
*Written 2026-10-04 20:23 UTC (card P1–P7), before running.* Replication units with ≥ 4 days: 51c, 51d, 51f, 51g, 51h. Niche units (≥ 3 days): 51a, 51c, 51d, 51e, 51f, 51g, 51h.
- R in each counted unit above every contrast unit (38a, 39, 40, 41); RE mean R ≥ 0.6.
- b_ex > 0 (CI) in ≥ 3/5 counted units; b_ex < 0.5 everywhere.
- W_P inside the shift-null 90% band and BC < 0.555 in each counted unit.
- Pooled β_n > 0; mediation gap G CI includes 0 with T̂_SR > 0; β_n keeps ≥ 70% after reads and replies.

### Native: the #focus room split (08-05)
*Written 2026-10-04 20:25 UTC, before running.* On 08-05 two agents (6, author; 29, performance coach) moved to #focus until 08-21 (51g); 51f (07-29 → 08-04) is the before unit. The RF model says the room carries the mean-field pull and the role carries the field.
- **G51-Na (field unchanged).** Each mover's static-field change |φ(51g) − φ(51f)| lies below the 90th percentile of the stayers' changes. Credence 0.6.
- **G51-Nb (pull follows the room).** Each mover's agent-level pull toward the #general mean (window states, cross-day-surrogate corrected) falls from 51f to 51g (Δb < 0 for both movers), while the stayers' median Δb is within ±0.05. Credence 0.45 (2 agents; sign test only).
- Counts against: movers' fields jump (above the stayers' 90th percentile), or movers' pull toward #general does not fall.
- Confound: 08-05 is also the day the operator bookends stop (NE43a).

## Result
*Run 2026-10-04 20:46 UTC. Primary variant style_resid_period × bge; gte in brackets. Data: `data/processed/H98-random-field-51/results/units.parquet`, `natives.json`.*

| Unit | Days | R [95% CI] | b_ex [95% CI] | W (p) | BC | β_n (jackknife SE) | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 51c | 5 | 0.73 [0.65, 0.75] | 0.26 [0.22, 0.33] | 1.90 (0.087) [1.19] | 0.43 | 0.040 (0.044) | supported |
| 51d | 5 | 0.67 [0.59, 0.70] | 0.31 [0.23, 0.37] | 3.05 (0.007) [3.09, 0.008] | 0.31 | 0.129 (0.124) | failed (W) |
| 51f | 5 | 0.69 [0.59, 0.71] | 0.23 [0.17, 0.29] | 0.73 (0.62) | 0.38 | 0.102 (0.096) | supported |
| 51g | 13 | 0.70 [0.61, 0.73] | 0.30 [0.26, 0.32] | 1.61 (0.048) [1.83, 0.010] | 0.51 | 0.108 (0.068) | failed (W) |
| 51h | 4 | 0.72 [0.64, 0.74] | 0.25 [0.14, 0.38] | 0.88 (0.45) | 0.20 | 0.247 (0.133) | supported |
| 51a (niche only) | 3 | 0.66 | 0.44 | – | – | −0.024 (0.082) | descriptive |
| 51e (niche only) | 3 | 0.70 | 0.36 | – | – | 0.048 (0.076) | descriptive |

- Pooled over the 7 niche units: β_n 0.064 [0.009, 0.118] (p 0.022), G −0.034 [−0.095, 0.028], T_SR 0.028 [0.003, 0.054]; gte β_n 0.010 [−0.056, 0.076].
- Reads and replies: β_n 0.084 → 0.025 (30% kept).
- Role share of the random field R²_role 0.05–0.14 (p ≤ 0.001 in 7/7). Mean soft stance 0.51–0.64; stance niche slope 0.019 [−0.066, 0.103].
- q_∞ 0.43–0.55 and memory M 0.51–0.72 (H22's values reproduce on the shared units).
- Post hoc: 51d's W excess comes from 07-17 (q_self 0.51, mean overlap 0.46; Kimi K3 joined); 51g's from a slow rise of the mean overlap (0.44 → 0.53 over 13 days).

### Native: #focus room split
- **Na (field unchanged):** movers' static-field change at the stayers' 88th percentile (both movers; primary). Variants: 84–96th. Passes in the primary variant only.
- **Nb (pull follows the room):** agent 29's pull toward #general falls 0.42 → 0.01 (lowest change of all 25 agents, all four variants). Agent 6: 0.07 → 0.10 (primary), −0.12 / +0.09 / −0.08 in the variants. Stayers' median change +0.10 (primary; outside ±0.05), +0.00 / +0.09 / +0.02 in the variants.
- **Native verdict: mixed.** One mover's pull vanishes when it leaves the room; the other had almost no pull to lose.

## Scorecard (period-specific axes)
- C: b_ex beats the cross-day surrogate in 5/5 units; the independent-agent P(q) fails in 2/5.
- D: the niche slope predicts the rival excess (bge only).
- E: #focus split mixed.
- G: role texts explain 5–14% of the random field.
