# H43 × G04: human-driven regime-I goal period (2025-05-15 → 2025-06-18)

**Verdict:** failed
**Role:** native (also carries the replication-layer row)
**Period:** regime I · 4 agents · one room (#general) · 25 non-holdout days in units 4a (05-15 → 05-21), 4b, 4c (05-23 → 06-18), 4d. The native test uses 4a and 4c; 4b and 4d are single days around roster changes and an outage.

## Why this period
The most human-message-driven period in the data: 1,713 human messages (335 naming an agent) to 4 agents, in the 2025 public-chat era, with no nudger. Two features are unique to it:
- **Continuous human trains:** humans post every ~1 min in bursts, so second messages arrive at every spacing from seconds to minutes.
- **Scheduled read-out:** regime-I chat-mode calls are *scheduled, not message-triggered* (DQ1: start-to-start cadence median 74 s; 45% of calls carry no new message). Whether a human message is read at this call or the next is set by the scheduler's phase, which makes the timing of the second kick close to exogenous.

Structural constraint (A2, found before any outcome): only 2% of calls are idle and the 30-min quiet rule leaves 32 primers. The native test therefore uses a 5-min quiet rule (265 human primers, 258 second messages) and busy-recipient outcomes: O2 (talks within 5 min) and O2c (the receiving call itself talks, i.e. the next action is a reply).

## Prediction
*Written 2026-10-04, before running on this period (card P9 as amended in A2).*
- **P9a:** human messages have E1 > 0 on O2 and on O2c (day-bootstrap CI above 0).
- **P9b:** R ≤ 0.3 for second messages read within 2 min of the first, and R ≥ 0.7 for δ in (5, 30] min.
- **P9c:** δ½ within a factor 2 of the launched-episode median L̃. The idle-launched episodes are few here, so L̃ may be undefined; P9c is then not scored.
- **Replication row (templated, 30-min quiet rule):** as for every period; expected descriptive (structure: 32 primers).
- **Against:** R ≈ 1 at δ ≤ 2 min (agents reply to every message, not to the burst), or no first-message effect.

## Result
Run 2026-10-04 with `analysis/run_native.py --test G04` (B = 300; units 4a+4c; 5-min quiet rule) and `analysis/run_period.py --period G04` (30-min rule); numbers in `data/processed/H43-kick-refractory-window/native/G04.json` and `G04/results.json`.

**Native (P9), human-message trains:** 4,152 human receiving calls → 265 primers (238 busy at read), 236 second messages (100 within 2 min, 68 at 2–5, 51 at 5–15, 14 at 15–30 min); 31 batched.

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P9a E1 > 0 on O2 and O2c | O2 0.47 [0.10, 0.65] (F 0.85 vs 0.75); O2c 0.73 [0.33, 0.94] (the receiving call replies: 0.55 vs 0.26) | **supported** |
| P9b R ≤ 0.3 at δ ≤ 2 min; R ≥ 0.7 at δ ∈ (5, 30] | δ ≤ 2: **R = 1.38 [0.54, 4.65]** (O2), **1.46 [0.78, 2.51]** (O2c); 2–5: 0.90 / 1.16; (5, 30]: 0.44 [0.13, 1.86] / 0.60 [0.27, 1.64] | **failed** (no short-spacing refractoriness; the second message in a train is at least as effective as the first) |
| P9c δ½ within ×2 of L̃ | δ½ = 0 (fit depth a = 0.04–0.24); L̃ = 24 min (26 idle-launched episodes) | **failed** |

Batched (two human messages read by the same call): R = 0.40 [−0.22, 1.35] on O2c (23 cases). Split halves (odd/even days) give R(0–15) = 0.97 and 1.23 (O2c).

**Replication row (templated, 30-min quiet rule):** H 28 primers / 30 second messages, E1 = 0.52 [−0.21, 1.13] (n.s.) → not testable; A underpowered. Templated verdict: descriptive.

Verdict: **failed**. In the most human-driven period, agents reply to a second human message read by a later call as readily as to the first. The only reduction is for messages read together in one call.
