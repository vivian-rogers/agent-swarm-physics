# H81 × NE33 (+NE32): Batch joins inside #51 (2026-07-09/10 and 2026-09-03/04)

**Verdict:** failed
**Role:** native
**Period:** regime III, goal #51 · NE32: GPT-5.6 Sol, Terra, Luna join on 07-09 in isolated rooms (closed 07-10), Grok 4.5 joins 07-10 · NE33: Muse Spark 1.3 and Gemini 3.8 Flash join 09-03, GPT-6 Astra 09-04 · 25 → 32 agents.

## Why this period
HH293 predicts that the village residual shifts at roster events more than composition alone predicts. For agents present on both sides of a join day (stayers), composition predicts no change at all. A coherent jump of the stayers at a batch join, beyond ordinary #51 day boundaries, would be the village reacting as a whole.

## Prediction
*Written 2026-10-04 20:05 UTC (card), copied here 2026-10-04 20:18 UTC, before running on this period.*
- Statistic: the stayers' coherent jump J_s = |mean_i Δ_i| / √(Σ_i |Δ_i|² / N²) with Δ_i = Π(v_{i,d} − v_{i,d−1}), at the boundaries 07-09 → 07-10 (merge with NE32 newcomers, Grok 4.5 joins), 07-08 → 07-09, 09-02 → 09-03 and 09-03 → 09-04, as a percentile among all other #51 within-period day boundaries.
- **Prediction:** percentile ≥ 0.95 for at least one event (NE32 merge or NE33), ≥ 0.8 for the other.
- **Against:** both events < 0.9. Prior 0.35.

## Result
*Run 2026-10-04 20:27 UTC (`analysis/natives.py`).* Percentile of the stayers' coherent jump J_s among 36 other #51 within-period day boundaries.

| Boundary (to day) | Event | J_s bge | percentile bge | J_s gte | percentile gte |
| --- | --- | --- | --- | --- | --- |
| 07-08 → 07-09 | NE32 newcomers join (isolated) | 1.55 | 0.86 | 1.54 | 0.78 |
| 07-09 → 07-10 | NE32 merge; Grok 4.5 joins | 1.60 | 0.89 | 1.50 | 0.72 |
| 09-02 → 09-03 | NE33: two agents join | 1.51 | 0.83 | 1.39 | 0.53 |
| 09-03 → 09-04 | NE33: GPT-6 Astra joins | 1.12 | 0.17 | 1.19 | 0.14 |

Placebo median J_s 1.28 (bge), 1.38 (gte). **N2 failed:** no event reaches 0.9 in either model. Batch joins do not move the incumbents' content more than an ordinary #51 day boundary. The card's O4 finds the same over all 22 within-goal roster events (pooled percentile 0.08 / 0.14).

## Scorecard (period-specific axes)
- E: roster interventions do not shift the culture residual beyond ordinary day-to-day change.

## Notes
- NE32's newcomers were isolated on 07-09: incumbents could not read them until 07-10, so 07-09 → 07-10 is the exposure boundary.
