# H112 × G38: charity fundraiser (year 2) (2026-04-02 → 2026-04-24)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · mode C · 12–14 agents · 2 room(s) · 17 non-holdout days. Units 38a, 38b, 38c, 38d, 38e.

## Why this period
Regime III shared-objective week (17 days); H93 βĴ +2.2 (work), herding regime.

## Prediction
*Written 2026-10-04 21:52 UTC, before running on this period (after amendment A1).* **What I had seen:** this period's structural counts (`counts.json`: 702 action switch-ins, 62 co-switch pairs; classes inflight 1, read 13, silent 48; median lag 265 s) and the synthetic summaries. No departure statistic.

- **HH343 (P1 here):** RR_U (unaware vs read, departure within 5 calls, MH over lag bin × kickoff-named) ≥ 2 with CI > 1. Credence 0.10.
- **My expectation:** RR_U inside the no-coupling synthetic band (0.7–1.2). Credence 0.6.
- Departure rates (any of the two within 5 calls) between 0.15 and 0.7 in both classes.

- **Against HH343 here:** RR_U CI includes 1 (failed if the period is testable and powered), or RR_U < 1 with CI < 1 (failed; read as the A1 null band, not as avoidance).
- Testable only if ≥ 30 uncensored pairs with ≥ 5 read and ≥ 5 unaware; otherwise descriptive.

## Result
*Run 2026-10-04 21:55 UTC (`analysis/run.py`, `analysis/natives.py`; non-holdout days only). Data: `data/processed/H112-crossing-claims-two-cycles/G38/`; results `results/periods.json`.*

| Statistic | Observed (95% CI) | Null / reference | Verdict |
| --- | --- | --- | --- |
| uncensored pairs (read / silent / in flight) | 62 (13 / 48 / 1) | testable needs ≥ 30, ≥ 5 read, ≥ 5 unaware | testable |
| P(≥ 1 departs within 5 calls): read, silent | 0.62, 0.88 | — | — |
| RR_U, unaware vs read (K = 5) | 1.46 [0.97, 2.21]; permutation p 0.029 | synthetic no-coupling band 0.83–1.05; HH343 ≥ 2 | HH343 not met |
| RR_U at K = 10 / 20 | 1.09 [0.79, 1.50] / 1.20 [0.88, 1.62] | — | — |
| RR_F, in flight vs read | 1.00 [1.00, 1.00] | — | descriptive (A1) |
| power at RR = 2 (base 0.3, these counts) | 0.1675 | ≥ 0.8 to call a null "failed" | — |

RR_U lies between 1 and 2 and its CI does not settle the period by the pre-set rule (HH343's ≥ 2 is not met). Departure rates are high in both classes (touch-level labels), which caps any risk ratio at 1/P(read).

## Scorecard (period-specific axes)
C 1 (beats the label-permutation null in the pool only; this period alone does not decide). D 0 (no 2-cycle signature). E 0.

## Notes
- 2026-10-04 21:52 UTC: folder created with the prediction.
