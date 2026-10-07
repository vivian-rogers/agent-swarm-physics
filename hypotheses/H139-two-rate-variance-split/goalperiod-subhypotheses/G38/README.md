# H139 × G38: the long shared week (#38, 2026-04-02 → 2026-04-27)

**Verdict:** pending
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
Not run.

## Scorecard (period-specific axes)
C, D, F, I: not run (all 0).

## Notes
- Room-specific kickoffs: the drive correction is done per room (cross-agent covariance within the agent's room).
