# H112 × G51: maximize your private assigned role (2026-07-06 → 2026-09-04)

**Verdict:** mixed
**Role:** native
**Period:** regime III · mode I/K · 21–32 agents · 2 room(s) · 45 non-holdout days. Units 51a, 51b, 51c, 51d, 51e, 51f, 51g, 51h, 51i, 51j, 51k, 51l.

## Why this period
Native (also replication): the private-role week in which H93 found avoidance (βĴ −11.7 [−19.0, −4.4]); the Little 2-cycle needs J < 0, so HH343's effect should be largest here. Units 51a–51l (non-holdout).

## Prediction
*Written 2026-10-04 21:52 UTC, before running on this period (after amendment A1).* **What I had seen:** this period's structural counts (`counts.json`: 10877 action switch-ins, 1499 co-switch pairs; classes inflight 11, read 225, silent 1263; median lag 266 s) and the synthetic summaries. No departure statistic.

- **HH343 (P1 here):** RR_U (unaware vs read, departure within 5 calls, MH over lag bin × kickoff-named) ≥ 2 with CI > 1. Credence 0.10.
- **My expectation:** RR_U inside the no-coupling synthetic band (0.7–1.2). Credence 0.6.
- Departure rates (any of the two within 5 calls) between 0.15 and 0.7 in both classes.
- **Native N2 (post-read onset, mechanism):** among co-switches where the partner's claim is read after the switch, departures cluster in the 3 calls after that read compared with the 3 calls before it (rate ratio > 1, CI > 1). Credence 0.25.
- **Native N1 (phase sign, with G42):** RR_U here ≥ 1.5 × the pooled RR_U of the shared weeks (#31, #36, #38, #41) (P4). Credence 0.25. The H112 model with read-gated avoidance predicts the opposite direction (RR_U < 1, synthetic W1: 0.80).
- **Against HH343 here:** RR_U CI includes 1 (failed if the period is testable and powered), or RR_U < 1 with CI < 1 (failed; read as the A1 null band, not as avoidance).
- Testable only if ≥ 30 uncensored pairs with ≥ 5 read and ≥ 5 unaware; otherwise descriptive.

## Result
*Run 2026-10-04 21:55 UTC (`analysis/run.py`, `analysis/natives.py`; non-holdout days only). Data: `data/processed/H112-crossing-claims-two-cycles/G51/`; results `results/periods.json`.*

| Statistic | Observed (95% CI) | Null / reference | Verdict |
| --- | --- | --- | --- |
| uncensored pairs (read / silent / in flight) | 1487 (225 / 1251 / 11) | testable needs ≥ 30, ≥ 5 read, ≥ 5 unaware | testable |
| P(≥ 1 departs within 5 calls): read, silent | 0.80, 0.90 | — | — |
| RR_U, unaware vs read (K = 5) | 1.12 [1.05, 1.20]; permutation p 0.000 | synthetic no-coupling band 0.83–1.05; HH343 ≥ 2 | HH343 not met |
| RR_U at K = 10 / 20 | 1.05 [1.00, 1.10] / 1.02 [0.98, 1.05] | — | — |
| RR_F, in flight vs read | 0.88 [0.58, 1.32] | — | descriptive (A1) |
| power at RR = 2 (base 0.3, these counts) | 1.0 | ≥ 0.8 to call a null "failed" | — |

**Native N2 (post-read onset):** 82 agent-pair reads with the agent still on P three calls before the read; departures in the 3 calls before the first read of the partner's claim: 19; in the 3 calls after: 15; ratio 0.79 [0.37, 1.64]. Predicted > 1 with CI > 1: **failed** (no departure onset at the read).
**Native N1 (phase sign, P4):** RR_U in own-role weeks (#42 + #51) 1.12 [1.05, 1.20] vs shared weeks (#31, #36, #38, #41) 1.27 [1.07, 1.52]; ratio 0.88 [0.73, 1.06]. Predicted ≥ 1.5: **failed**.

RR_U lies between 1 and 2 and its CI does not settle the period by the pre-set rule (HH343's ≥ 2 is not met). Departure rates are high in both classes (touch-level labels), which caps any risk ratio at 1/P(read).

## Scorecard (period-specific axes)
C 1 (beats the label-permutation null in the pool only; this period alone does not decide). D 0 (no 2-cycle signature). E 0.

## Notes
- 2026-10-04 21:52 UTC: folder created with the prediction.
