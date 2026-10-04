# H112 × G42: YouTube channels (2026-05-18 → 2026-05-22)

**Verdict:** descriptive
**Role:** native
**Period:** regime III · mode I · 15–16 agents · 2 room(s) · 5 non-holdout days. Units 42a, 42b.

## Why this period
Native: the other own-role week with H93 avoidance (βĴ −5.9 work). Only 7 co-switch pairs, all silent: descriptive by the testability rule; it enters the phase contrast (P4) only through the pool.

## Prediction
*Written 2026-10-04 21:52 UTC, before running on this period (after amendment A1).* **What I had seen:** this period's structural counts (`counts.json`: 93 action switch-ins, 7 co-switch pairs; classes silent 7; median lag 351 s) and the synthetic summaries. No departure statistic.

- **HH343 (P1 here):** RR_U (unaware vs read, departure within 5 calls, MH over lag bin × kickoff-named) ≥ 2 with CI > 1. Credence 0.10.
- **My expectation:** RR_U inside the no-coupling synthetic band (0.7–1.2). Credence 0.6.
- Departure rates (any of the two within 5 calls) between 0.15 and 0.7 in both classes.
- With 7 pairs (all silent) no contrast is computable; departure rates are reported descriptively.
- **Against HH343 here:** RR_U CI includes 1 (failed if the period is testable and powered), or RR_U < 1 with CI < 1 (failed; read as the A1 null band, not as avoidance).
- Testable only if ≥ 30 uncensored pairs with ≥ 5 read and ≥ 5 unaware; otherwise descriptive.

## Result
*Run 2026-10-04 21:55 UTC (`analysis/run.py`, `analysis/natives.py`; non-holdout days only). Data: `data/processed/H112-crossing-claims-two-cycles/G42/`; results `results/periods.json`.*

| Statistic | Observed (95% CI) | Null / reference | Verdict |
| --- | --- | --- | --- |
| uncensored pairs (read / silent / in flight) | 7 (0 / 7 / 0) | testable needs ≥ 30, ≥ 5 read, ≥ 5 unaware | descriptive |
| P(≥ 1 departs within 5 calls): read, silent | n.e., 0.86 | — | — |
| RR_U, unaware vs read (K = 5) | n.e.; permutation p nan | synthetic no-coupling band 0.83–1.05; HH343 ≥ 2 | HH343 not met |
| RR_U at K = 10 / 20 | n.e. / n.e. | — | — |
| RR_F, in flight vs read | n.e. | — | descriptive (A1) |
| power at RR = 2 (base 0.3, these counts) | n.e. | ≥ 0.8 to call a null "failed" | — |

Descriptive: 7 pairs, all silent; ≥ 1 departs in 0.86, both depart in 0.57. No contrast is computable.

Not testable by the pre-set rule. Departure rates are high in both classes (touch-level labels), which caps any risk ratio at 1/P(read).

## Scorecard (period-specific axes)
None informed (descriptive).

## Notes
- 2026-10-04 21:52 UTC: folder created with the prediction.
