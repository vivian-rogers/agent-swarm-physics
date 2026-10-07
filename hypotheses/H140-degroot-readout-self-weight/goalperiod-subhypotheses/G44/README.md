# H140 × G44: regime-III shared-goal period #44 (2026-05-26 → 05-29)

**Verdict:** descriptive
**Role:** exploratory (replication)
**Period:** regime III · computer-use context segments · 18 agents · two rooms · 4 days, split at roster joins (44a, 44b). Fit units: units 44a, 44b (`period_units`).

## Why this period
A non-reserved regime-III period with context segments, so s_self exists. It is one more point for the replication layer (O1–O4). Units with < 300 scored talk calls enter only through the random-effects pool (card, exception (d)).

## Prediction
*Copied from the card and dated 2026-10-07 08:55 UTC (system clock), before running on this period. Seen: H113's #44 values (card "What I had seen"); the synthetic results on skeletons 51c, 51g, #38, #41 (no real H140 statistic).*
- **P1:** ŵ₁ ∈ [0.5, 1.5] with CI above 0. Credence 0.15.
- **P2:** â ∈ [0.15, 0.40], CI excluding 1 (scored only if the read − in-flight contrast CI > 0 and r < 0.7). Credence 0.6.
- **P3:** ŵ₂ (call-gap term) > 0 with CI. Credence 0.5.
- **P4:** γ̂_F / γ̂₁ ≤ 0.5 and read − in-flight contrast > 0. Credence 0.65.
- Counts against: the card's kill clauses on this unit (per-unit verdicts are descriptive for the kill; the pool decides).

## Result
Data: `data/processed/H140-degroot-readout-self-weight/G44/`, results `results/units_G44.json`. Run 2026-10-07 (exploration data; reserved days never enter the scheme). Estimator: Amendment A1 spec (primary) and the registered spec; agent-day cluster bootstrap, 300 draws.

Every unit has < 300 scored talk calls (131 (44a) + 245 (44b) rows), so the period enters only the random-effects pool (card exception (d)); no per-unit verdict.

| Observable | Observed (bge A1) |
| --- | --- |
| ŵ₁ | 44a −0.58 [−3.39, 0.70]; 44b −0.35 [−1.87, 0.55]; DL pool −0.40 [−1.42, 0.62] |
| â | 44a 0.38 [0.02, 1.24] (identified, bge); 44b 0.32 [−0.50, 1.40] (identified in gte only) |

The predictions are not scored here.

## Scorecard (period-specific axes)
C, D, H: 0 (descriptive only).
