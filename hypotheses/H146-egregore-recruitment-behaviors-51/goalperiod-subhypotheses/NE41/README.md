# H146 × NE41: forced context erasures of pattern hosts in #51 (07-06 → 09-04)

**Verdict:** mixed
**Role:** exploratory
**Period:** #51 non-reserved days; forced erasures F (`reset_forced`, not first of day) and placebo calls P (ctx_pos 20, no reset in the next 10 calls), agent × unit strata. The test spans the whole period because erasures occur every day (exception (c): the event is the object).

## Why this period
A forced erasure removes a host's context while the pattern lives on in other hosts and in artifacts. If the pattern is held above its hosts (egregore condition 2), the host re-expresses it after a wipe about as often as after a placebo call, and faster when it re-reads K-carrying items or K artifacts.

## Prediction
*Written 2026-10-09, before running (card P4, P5-wipe; Amendment A1.7, A1.8).*
- P4: HR(F vs P) of re-expression within calls 1–20 ≥ 0.8; K2 fires if < 0.5. Read-gated (R+) re-expression after call 10 faster than R− (HR CI above 1), where powered (all candidates but the byte game).
- P5-wipe: named K messages from other hosts in the 2 h after a wipe vs a placebo call, RR > 1.2 with CI above 1 (powered for every candidate).

## Result
*Round 1, 2026-10-09.* Host events per memeplex (K14 excluded): 2,648–13,049 forced wipes and 3,777–17,280 placebo calls.

| Prediction | Observed (95% CI) | Null | Verdict |
| --- | --- | --- | --- |
| P4 HR ≥ 0.8 (K2 if < 0.5) | median 0.90 over 14 memeplexes, range 0.78 (K06 [0.67, 0.92]) to 1.11; candidates 0.81–1.19 | pseudo-patterns: median 0.89 (5–95% 0.77–1.01) | supported; generic |
| P4 read-gated faster | HR(R+ vs R−) CI above 1 for 10/15 memeplexes (1.21–2.34) | post hoc pseudo: median 1.39, 98% > 1; no memeplex beyond | supported as written; generic (post hoc) |
| P5 repair after wipe | RR 0.95–1.07, none with CI above 1 (power 1.00 at RR 1.5) | placebo calls | failed |

A host wipe does not erase a pattern: the host re-expresses it at ~0.9 of the placebo rate, and faster when it reads it again. Any frequency-matched set of elements behaves the same way, so this is how the village's vocabulary survives wipes, not a property of the memeplexes. Other hosts do not send more K messages to a wiped host.


## Scorecard (period-specific axes)
- E interventional 1: wipes are exogenous to the pattern (scheduler-forced), with placebo calls at matched position.
- C adequacy 0: no memeplex differs from its pseudo-patterns.

## Notes
- Forced wipes arrive with a chat backlog (88% at call 1, `infra/README.md`); the R+ flag counts K-carrying items read at calls 1–10, so a backlog read counts as a re-supply.
