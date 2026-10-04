# H112 × G18: reduce global poverty (2025-10-20 → 2025-10-31)

**Verdict:** mixed
**Role:** replication
**Period:** regime I · mode C · 7–8 agents · 1 room(s) · 10 non-holdout days. Units 18a, 18b, 18c.

## Why this period
Regime I with the most claim-mediated co-switches outside regime III (52 pairs, 25 read); a check that the contrast does not depend on the computer-use scaffold.

## Prediction
*Written 2026-10-04 21:52 UTC, before running on this period (after amendment A1).* **What I had seen:** this period's structural counts (`counts.json`: 222 action switch-ins, 52 co-switch pairs; classes read 25, silent 27; median lag 90 s) and the synthetic summaries. No departure statistic.

- **HH343 (P1 here):** RR_U (unaware vs read, departure within 5 calls, MH over lag bin × kickoff-named) ≥ 2 with CI > 1. Credence 0.10.
- **My expectation:** RR_U inside the no-coupling synthetic band (0.7–1.2). Credence 0.6.
- Departure rates (any of the two within 5 calls) between 0.15 and 0.7 in both classes.

- **Against HH343 here:** RR_U CI includes 1 (failed if the period is testable and powered), or RR_U < 1 with CI < 1 (failed; read as the A1 null band, not as avoidance).
- Testable only if ≥ 30 uncensored pairs with ≥ 5 read and ≥ 5 unaware; otherwise descriptive.

## Result
*Run 2026-10-04 21:55 UTC (`analysis/run.py`, `analysis/natives.py`; non-holdout days only). Data: `data/processed/H112-crossing-claims-two-cycles/G18/`; results `results/periods.json`.*

| Statistic | Observed (95% CI) | Null / reference | Verdict |
| --- | --- | --- | --- |
| uncensored pairs (read / silent / in flight) | 50 (25 / 25 / 0) | testable needs ≥ 30, ≥ 5 read, ≥ 5 unaware | testable |
| P(≥ 1 departs within 5 calls): read, silent | 0.36, 0.24 | — | — |
| RR_U, unaware vs read (K = 5) | 0.82 [0.33, 2.07]; permutation p 0.757 | synthetic no-coupling band 0.83–1.05; HH343 ≥ 2 | HH343 not met |
| RR_U at K = 10 / 20 | 0.84 [0.35, 2.04] / 0.77 [0.41, 1.43] | — | — |
| RR_F, in flight vs read | n.e. | — | descriptive (A1) |
| power at RR = 2 (base 0.3, these counts) | 0.49 | ≥ 0.8 to call a null "failed" | — |

RR_U lies between 1 and 2 and its CI does not settle the period by the pre-set rule (HH343's ≥ 2 is not met). Departure rates are high in both classes (touch-level labels), which caps any risk ratio at 1/P(read).

## Scorecard (period-specific axes)
C 1 (beats the label-permutation null in the pool only; this period alone does not decide). D 0 (no 2-cycle signature). E 0.

## Notes
- 2026-10-04 21:52 UTC: folder created with the prediction.
