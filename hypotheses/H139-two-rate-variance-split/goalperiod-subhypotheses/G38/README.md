# H139 × G38: the long shared week (#38, 2026-04-02 → 2026-04-27)

**Verdict:** n/a (inconclusive: below resolution). S1 fired before real data; P1 and P2 are untestable here (38a, 38b, 38e; 38c and 38d are descriptive).
**Role:** exploratory (replication; transfer of H130's two rates to a shared goal)
**Period:** regime III · mode C · 12 agents · two rooms (#best / #rest, room-specific kickoffs) · 17 days. Units from `period_units`.

## Why this period
The longest non-reserved regime-III shared-goal week. Wells are weaker in shared weeks (H98: random-field share R 0.24–0.53 in #38–#41 vs 0.67–0.73 in #51), and H130-R4 asks whether the two rates transfer. Two rooms give two read rates for agents in the same days.

## Prediction
*Written 2026-10-07 ~10:00 UTC, before running on this period. Seen: H98's and H130's numbers; no #38 read count, kick or autocovariance statistic.*
- Inputs first: J_K and γ_kick re-estimated here with H130's A1 estimators (read-minus-in-flight jump; sender-specific distributed lag).
- **P1:** Q_k = Â_k / A_k^pred has 90% CI inside [0.5, 2]. Credence 0.1. If A_min > 2 A_k^pred (synthetic S1), P1 is untestable here.
- **P3:** f_s ≥ 0.8. Credence 0.55 (weaker wells than #51).
- **P5:** the two-rate fit beats the one-rate fit out of fold. Credence 0.4.
- Counts against: Q_k outside [0.5, 2] with CI excluding 1 (resolved units only).

## Result
*Run 2026-10-07 14:32 UTC (exploratory, non-reserved). Primary variant `style_resid_period` × bge, drive-corrected. S1 (A_min > 2 A_k^pred) was fixed as the decision before real data (card, Amendment A1). Data: `data/processed/H139-two-rate-variance-split/G38/` and `results/units_G38.parquet`. Figures: the card's `figures/`.*

| Unit | Days | r̄ /call | J_K used | A_k^pred | A_min (synthetic) | A_min (real scale, post hoc) | Â_k [95% CI] | f_s | two-rate beats one (OOF) | γ_s /call | P1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 38a | 8 | 0.21 | 0.076 | 0.0044 | 1.25 | 0.141 | -0.005 [-0.138, 0.040] | 1.04 | False | 0.0091 | untestable (S1) |
| 38b | 3 | 0.22 | 0.081 | 0.0051 | 2.95 | 0.423 | -0.221 [-0.436, -0.035] | -10.41 | True | 0.0412 | untestable (S1) |
| 38c | 1 | 0.22 | 0.135 | 0.0145 | — | — | 0.089 [-0.183, 0.211] | 0.70 | None | 0.0234 | descriptive (< 3 days) |
| 38d | 2 | 0.17 | -0.004 | 0.0000 | — | — | -0.344 [-0.576, 0.048] | 5.66 | True | 0.0498 | descriptive (< 3 days) |
| 38e | 3 | 0.19 | 0.024 | 0.0004 | > 3 | 0.499 | 0.217 [-0.267, 0.299] | 0.53 | True | 0.0051 | untestable (S1) |

J_K re-estimated with H130's read jump: 38a 0.076, 38b 0.081, 38e 0.024 (upper 95% bounds ≤ 0.16; J* for testability 0.90–1.49). γ_kick not re-estimated (0.15; A1.2). The drive correction is per room class (#best, #rest, cross-room).

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 Q_k 90% CI in [0.5, 2] | untestable (S1 in 38a, 38b, 38e) | untestable → inconclusive |
| P3 f_s ≥ 0.8 | 38a 1.04, 38b −10.4, 38e 0.53 | 1/3; non-diagnostic |
| P5 two-rate beats one out of fold | 38a no, 38b yes, 38e yes | 2/3; non-diagnostic |

## Scorecard (period-specific axes)
C 0, D 0, F 1 (synthetic on 38a, 38b, 38e), I 0 (nothing resolved to transfer).

## Notes
- Room-specific kickoffs: the drive correction is done per room (cross-agent covariance within the agent's room).
