# H112 × G44: #best fine-tunes a leader; #rest own goals (2026-05-26 → 2026-05-29)

**Verdict:** mixed
**Role:** native
**Period:** regime III · mode C · 17–18 agents · 2 room(s) · 4 non-holdout days. Units 44a, 44b.

## Why this period
Native: #best was assigned a team task and #rest chose freely on the same days (H93's G44 arms). An assigned field sets co-switches in #best, so no update-order effect is expected there.

## Prediction
*Written 2026-10-04 21:52 UTC, before running on this period (after amendment A1).* **What I had seen:** this period's structural counts (`counts.json`: 440 action switch-ins, 89 co-switch pairs; classes inflight 2, read 14, silent 73; median lag 213 s) and the synthetic summaries. No departure statistic.

- **HH343 (P1 here):** RR_U (unaware vs read, departure within 5 calls, MH over lag bin × kickoff-named) ≥ 2 with CI > 1. Credence 0.10.
- **My expectation:** RR_U inside the no-coupling synthetic band (0.7–1.2). Credence 0.6.
- Departure rates (any of the two within 5 calls) between 0.15 and 0.7 in both classes.
- **Native N3 (assigned vs free arms):** RR_U in the free #rest arm ≥ RR_U in the assigned #best arm; the #best arm RR_U is within the no-coupling band [0.7, 1.2]. Credence 0.35. Rooms from `rooms_timeline` at the second switch.
- **Against HH343 here:** RR_U CI includes 1 (failed if the period is testable and powered), or RR_U < 1 with CI < 1 (failed; read as the A1 null band, not as avoidance).
- Testable only if ≥ 30 uncensored pairs with ≥ 5 read and ≥ 5 unaware; otherwise descriptive.

## Result
*Run 2026-10-04 21:55 UTC (`analysis/run.py`, `analysis/natives.py`; non-holdout days only). Data: `data/processed/H112-crossing-claims-two-cycles/G44/`; results `results/periods.json`.*

| Statistic | Observed (95% CI) | Null / reference | Verdict |
| --- | --- | --- | --- |
| uncensored pairs (read / silent / in flight) | 87 (13 / 72 / 2) | testable needs ≥ 30, ≥ 5 read, ≥ 5 unaware | testable |
| P(≥ 1 departs within 5 calls): read, silent | 0.62, 0.71 | — | — |
| RR_U, unaware vs read (K = 5) | 1.22 [0.79, 1.87]; permutation p 0.220 | synthetic no-coupling band 0.83–1.05; HH343 ≥ 2 | HH343 not met |
| RR_U at K = 10 / 20 | 1.37 [0.89, 2.13] / 1.14 [0.88, 1.47] | — | — |
| RR_F, in flight vs read | 1.36 [0.88, 2.09] | — | descriptive (A1) |
| power at RR = 2 (base 0.3, these counts) | 0.1975 | ≥ 0.8 to call a null "failed" | — |

**Native N3 (assigned vs free arms, by the second mover's room):** #best (assigned) 12 pairs, all unaware (0 read): no contrast; departure share 0.42. #rest (free) 75 pairs (13 read): RR_U 1.27 [0.83, 1.95], read 0.62 vs unaware 0.77. Predicted RR_U(#rest) ≥ RR_U(#best) with #best inside the null band: **descriptive** (no read pairs in #best).

RR_U lies between 1 and 2 and its CI does not settle the period by the pre-set rule (HH343's ≥ 2 is not met). Departure rates are high in both classes (touch-level labels), which caps any risk ratio at 1/P(read).

## Scorecard (period-specific axes)
C 1 (beats the label-permutation null in the pool only; this period alone does not decide). D 0 (no 2-cycle signature). E 0.

## Notes
- 2026-10-04 21:52 UTC: folder created with the prediction.
