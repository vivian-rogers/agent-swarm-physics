# H112 × G36: interact with outside agents (2026-03-23 → 2026-03-27)

**Verdict:** mixed
**Role:** replication
**Period:** regime II · mode C · 12 agents · 2 room(s) · 5 non-holdout days. Units 36a, 36b, 36c.

## Why this period
Regime II/III boundary week with many action switch-ins (182 pairs); H93 βĴ +1.9 (work).

## Prediction
*Written 2026-10-04 21:52 UTC, before running on this period (after amendment A1).* **What I had seen:** this period's structural counts (`counts.json`: 1130 action switch-ins, 182 co-switch pairs; classes inflight 3, read 19, silent 160; median lag 210 s) and the synthetic summaries. No departure statistic.

- **HH343 (P1 here):** RR_U (unaware vs read, departure within 5 calls, MH over lag bin × kickoff-named) ≥ 2 with CI > 1. Credence 0.10.
- **My expectation:** RR_U inside the no-coupling synthetic band (0.7–1.2). Credence 0.6.
- Departure rates (any of the two within 5 calls) between 0.15 and 0.7 in both classes.

- **Against HH343 here:** RR_U CI includes 1 (failed if the period is testable and powered), or RR_U < 1 with CI < 1 (failed; read as the A1 null band, not as avoidance).
- Testable only if ≥ 30 uncensored pairs with ≥ 5 read and ≥ 5 unaware; otherwise descriptive.

## Result
*Run 2026-10-04 21:55 UTC (`analysis/run.py`, `analysis/natives.py`; non-holdout days only). Data: `data/processed/H112-crossing-claims-two-cycles/G36/`; results `results/periods.json`.*

| Statistic | Observed (95% CI) | Null / reference | Verdict |
| --- | --- | --- | --- |
| uncensored pairs (read / silent / in flight) | 180 (19 / 158 / 3) | testable needs ≥ 30, ≥ 5 read, ≥ 5 unaware | testable |
| P(≥ 1 departs within 5 calls): read, silent | 0.79, 0.91 | — | — |
| RR_U, unaware vs read (K = 5) | 1.16 [0.91, 1.48]; permutation p 0.044 | synthetic no-coupling band 0.83–1.05; HH343 ≥ 2 | HH343 not met |
| RR_U at K = 10 / 20 | 1.14 [0.93, 1.39] / 1.01 [0.90, 1.13] | — | — |
| RR_F, in flight vs read | 1.30 [1.00, 1.68] | — | descriptive (A1) |
| power at RR = 2 (base 0.3, these counts) | 0.4725 | ≥ 0.8 to call a null "failed" | — |

RR_U lies between 1 and 2 and its CI does not settle the period by the pre-set rule (HH343's ≥ 2 is not met). Departure rates are high in both classes (touch-level labels), which caps any risk ratio at 1/P(read).

## Scorecard (period-specific axes)
C 1 (beats the label-permutation null in the pool only; this period alone does not decide). D 0 (no 2-cycle signature). E 0.

## Notes
- 2026-10-04 21:52 UTC: folder created with the prediction.
