# H112 × G41: novel research (2026-05-11 → 2026-05-15)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · mode I · 15 agents · 2 room(s) · 5 non-holdout days. Units 41.

## Why this period
Regime III shared research week; H93's strongest positive coupling (+3.9 work, +4.5 attention).

## Prediction
*Written 2026-10-04 21:52 UTC, before running on this period (after amendment A1).* **What I had seen:** this period's structural counts (`counts.json`: 277 action switch-ins, 57 co-switch pairs; classes inflight 1, read 9, silent 47; median lag 321 s) and the synthetic summaries. No departure statistic.

- **HH343 (P1 here):** RR_U (unaware vs read, departure within 5 calls, MH over lag bin × kickoff-named) ≥ 2 with CI > 1. Credence 0.10.
- **My expectation:** RR_U inside the no-coupling synthetic band (0.7–1.2). Credence 0.6.
- Departure rates (any of the two within 5 calls) between 0.15 and 0.7 in both classes.

- **Against HH343 here:** RR_U CI includes 1 (failed if the period is testable and powered), or RR_U < 1 with CI < 1 (failed; read as the A1 null band, not as avoidance).
- Testable only if ≥ 30 uncensored pairs with ≥ 5 read and ≥ 5 unaware; otherwise descriptive.

## Result
*Run 2026-10-04 21:55 UTC (`analysis/run.py`, `analysis/natives.py`; non-holdout days only). Data: `data/processed/H112-crossing-claims-two-cycles/G41/`; results `results/periods.json`.*

| Statistic | Observed (95% CI) | Null / reference | Verdict |
| --- | --- | --- | --- |
| uncensored pairs (read / silent / in flight) | 56 (9 / 46 / 1) | testable needs ≥ 30, ≥ 5 read, ≥ 5 unaware | testable |
| P(≥ 1 departs within 5 calls): read, silent | 0.78, 0.74 | — | — |
| RR_U, unaware vs read (K = 5) | 0.86 [0.61, 1.22]; permutation p 0.739 | synthetic no-coupling band 0.83–1.05; HH343 ≥ 2 | HH343 not met |
| RR_U at K = 10 / 20 | 1.10 [0.70, 1.73] / 1.14 [0.85, 1.53] | — | — |
| RR_F, in flight vs read | 2.00 [0.75, 5.33] | — | descriptive (A1) |
| power at RR = 2 (base 0.3, these counts) | 0.0125 | ≥ 0.8 to call a null "failed" | — |

RR_U lies between 1 and 2 and its CI does not settle the period by the pre-set rule (HH343's ≥ 2 is not met). Departure rates are high in both classes (touch-level labels), which caps any risk ratio at 1/P(read).

## Scorecard (period-specific axes)
C 1 (beats the label-permutation null in the pool only; this period alone does not decide). D 0 (no 2-cycle signature). E 0.

## Notes
- 2026-10-04 21:52 UTC: folder created with the prediction.
