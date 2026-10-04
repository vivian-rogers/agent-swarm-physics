# H93 × G38: Choose a charity and raise money (year 2) (2026-04-02 → 04-24)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · mode C · 12–14 agents · #best / #rest (room-specific kickoffs) · 17 days. Units 38a–38e (NE36, NE17, joins, NE18, join).

## Why this period
The longest two-room regime-III period with dense git; the best powered single period for βJ (M4 power 0.95 at βJ = 3), so a null here is informative.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts from the scheme (`counts.json`: choice events, options, named options per channel) and, where simulated, the synthetic power of M4 on this period's skeleton. No real βJ, P_multi or m.

- M0 > 0 (CI > 0) in work and attention (0.7).
- M4: βĴ CI includes 0, or 0 < βĴ < 2 (0.6).
- P_multi < 0.5 (0.8); m (work) 0.3–0.6.
- Against: βĴ(M4) ≥ 3 with CI > 0.

## Result
*Run 2026-10-04 (non-holdout days only). Data: `data/processed/H93-brock-durlauf-project-choice/G38/`; results `.../results/G38.json`.*

| Channel | events (testable units) | βĴ M0 (naive) | βĴ M2 | **βĴ M4 (validated)** | kickoff-free | cross-lab | read share | m | max P_multi | γ_c (ratio) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| work | 183 (38a) | +3.14 [+2.49, +3.79] | +2.71 [+1.90, +3.52] | **+2.22 [+1.36, +3.07]** | +4.10 [+2.49, +5.70] | +3.31 [+2.27, +4.35] | +2.91 [+1.93, +3.89] | 0.58 | 0.00 | 5.5 (+0.40) |
| attention | 371 (38a, 38b, 38e) | +4.23 [+2.15, +6.31] | +1.82 [-1.56, +5.19] | **+0.55 [-2.29, +3.38]** | +8.31 [+5.49, +11.14] | -1.05 [-5.50, +3.41] | +1.20 [-2.52, +4.92] | 0.41 | 0.00 | 6.5 (+0.45) |

βĴ in nats per unit share (95% Wald CI; DL pool over testable units where the period has several). γ_c: smallest coupling at which the fitted fields of the largest unit support two stable equilibria; ratio = βĴ/γ_c. Null: the M4 false-positive rate is ≤ 0.10 under static fitness spread but 0.12–1.00 under fast repo bursts (card A2), so a positive βĴ is a share coefficient, not proof of J.

M0 > 0 in both channels as predicted. Work βĴ(M4) +2.22 [1.36, 3.07], just above the predicted < 2; attention +0.55 [−2.29, 3.38] as predicted. P_multi = 0 in every unit; βĴ/γ_c 0.40 (work). The most powered period (0.95) sees a real but subcritical share coefficient.

## Scorecard (period-specific axes)
- C: 1. F: 2 (power 0.95, coverage 0.85–0.95 in the static worlds).

## Notes
- 2026-10-04: folder created by the round-1 agent. Predictions use the M4 estimator (card amendment A1, written before any real fit).
