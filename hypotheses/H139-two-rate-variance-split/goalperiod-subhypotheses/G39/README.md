# H139 × G39: #39 (2026-04-27 → 2026-05-01)

**Verdict:** n/a (inconclusive: below resolution). S1 fired before real data; P1 and P2 are untestable here.
**Role:** exploratory (replication; shared-goal transfer of H130's two rates)
**Period:** regime III · 15 agents · two rooms · 5 days (unit 39). Non-reserved.

## Why this period
A non-reserved regime-III shared-goal period with ledger reads. It tests whether the variance split transfers from #51's private roles (H130-R4). Units with < 3 days are descriptive.

## Prediction
*Copied 2026-10-07 after the run from the card's registered predictions (written 09:15–10:00 UTC, before any real-data statistic). The card asked for this folder before the run; it was not made then. No prediction was changed.*
- **P1:** Q_k = Â_k / A_k^pred, 90% CI inside [0.5, 2]. Untestable if A_min > 2 A_k^pred (S1).
- **P3:** f_s ≥ 0.8.
- **P5:** the constrained two-rate fit beats the one-rate fit out of fold.
- Inputs: J_K re-estimated here with H130's read jump; γ_kick 0.15 (Amendment A1.2).

## Result
*Run 2026-10-07 14:32 UTC (exploratory, non-reserved). Primary variant `style_resid_period` × bge, drive-corrected. S1 (A_min > 2 A_k^pred) was fixed as the decision before real data (card, Amendment A1). Data: `data/processed/H139-two-rate-variance-split/G39/` and `results/units_G39.parquet`. Figures: the card's `figures/`.*

| Unit | Days | r̄ /call | J_K used | A_k^pred | A_min (synthetic) | A_min (real scale, post hoc) | Â_k [95% CI] | f_s | two-rate beats one (OOF) | γ_s /call | P1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 39 | 5 | 0.22 | 0.048 | 0.0019 | > 3 | 0.326 | -0.066 [-0.323, 0.062] | 1.26 | True | 0.0193 | untestable (S1) |

J_K (H130 read jump, re-estimated): 39 0.048. S1 holds with these inputs: every upper 95% bound of J_K lies below J*.
P3 and P5 are non-diagnostic at this resolution (card, A1.5).

## Scorecard (period-specific axes)
C 0, D 0, F 1 (synthetic on this unit), I 0.

## Notes
- Read rate per call is 0.19–0.59 in #37–#44, below #51's 0.74–1.20, so A_k^pred is smaller here.
