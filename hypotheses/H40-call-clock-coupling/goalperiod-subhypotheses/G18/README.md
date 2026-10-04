# H40 × G18: Reduce global poverty as much as you can (2025-10-20 → 2025-10-31)

**Verdict:** failed
**Role:** native (exploratory); the replication estimator is reported here too
**Period:** regime I · 8 agents · #general · 10 days · units 18a, 18b, 18c · 45,599 read-out items · 2,276 replies within 30 min. The non-holdout period with the most chat-mode calls (8,200).

## Why this period
In regime I, chat-mode calls are scheduled (not message-triggered; DQ1), so the jitter in their spacing is exogenous to any one message. If the reply hazard per chat call grows with the span of the call, the clock is wall time; if not, it is the call clock.

## Prediction
*Written 2026-10-04 ~06:10 UTC (card N3), before any H40 statistic on G18.* η within scheduled chat-mode calls has its CI inside [−0.3, 0.3]. No prediction for the chat vs computer-use contrast.

## Result
| Test | Observed (95% CI) | Prediction | Verdict |
| --- | --- | --- | --- |
| **N3** η within chat-mode calls | +0.81 [+0.68, +0.95] | inside [−0.3, 0.3] | **failed** |
| η₁ (read-out wait) at chat-mode read-outs | +0.17 [+0.10, +0.24] | — | wait adds hazard |
| η, computer-use calls | +0.48 [+0.22, +0.75] | — | also positive |
| Chat vs computer-use per-call hazard (log HR) | +1.47 [+1.11, +1.84] (×4.4) | descriptive | chat calls carry the replies |
| Chat-mode start-to-start interval | median 32 s (IQR 21–68 s) | | |
| Replication: η (all calls) | +0.75 ± 0.06 | CI < 0.5 | failed |
| Held-out Δ log-lik (call − wall) | +0.0066 | > 0 | call clock still beats the pure wall clock |
| Between-agent s (21 agent-units) | +0.49 [−0.24, +1.22] | | uninformative |
| Model-free slopes on log rate: per-call β(10); per-hour P(5 min) | +1.27 [+0.01, +2.54]; +1.68 [+0.25, +3.12] | | |
| ε(5 / 30 min) | 0.37 / 0.31 | | |
| Robustness of η: any p_reply ≥ 0.5; addressing; certain items; jitter | +0.82; +0.57; +0.62; +0.68, +0.69 | | robust |
| Post hoc: η in chat mode with spans < 128 s only | +0.86 ± 0.08 | | not hidden calls in long gaps |

**Reading.** In the regime-I chat scaffold the reply hazard per scheduled call grows almost in proportion to the call's span (η ≈ 0.8): close to a wall clock. Latency-placed starts are not the cause (logged Gemini chat calls in #24–#31 give the same sign; see the card), nor are unlogged calls in long gaps (short spans give the same η). Candidate mechanisms (round 2): long chat calls are long generations by engaged agents (endogenous cadence), or the scheduler's spacing depends on chat state.

Data: `results/G18.json`, `native/N3_G18.json`, `posthoc/short_span.json`.

## Scorecard (period-specific axes)
- **C/H:** the call clock beats the pure wall clock on held-out days, but the free-η model sits near the wall clock; H40 fails here.
- **E:** the exogenous-jitter design failed its prediction.
- **F:** synthetic recovery on G18's own schedule: η bias ≤ 0.02 (S1–S3).
