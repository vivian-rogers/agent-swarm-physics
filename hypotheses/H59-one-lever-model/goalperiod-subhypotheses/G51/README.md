# H59 × G51: private roles, #51 head (2026-07-06 → 09-04, non-holdout days)

**Verdict:** failed
**Role:** replication
**Period:** regime III · 21–32 agents · #general (+ #focus from 08-05) · 45 non-holdout days. Nudges until 2026-08-20 (NE43); the tail from 09-07 is held out.

## Why this period
The only period with all four point-kick classes: nudges (720 receiving calls, leading-@ target), broadcast human messages (1,569), named human messages (92) and @-mentions (31,873). It is where leave-one-class-out can be run four ways.

## Prediction
*Templated from the card (P1, P2–P5, written 2026-10-04 before any outcome fit; amendment A1 after the synthetic, before real data).* Every powered class has T = S_H59/S_free ≥ 0.8 and S_H59 > 0 (CI); counts against: T < 0.5 with S_free − S_H59 CI > 0. Expectation stated in advance: nudges are the likeliest failure. A1: Hm and Hu are expected to be uninformative here even if the lever is real.

## Result
`data/processed/H59-one-lever-model/G51/results.json`, `loco_split.json`. Skill = held-out-day log-likelihood gain over the inert model (nats); 5 day folds; 95% day-bootstrap CIs.

| Class (receiving calls) | κ (catalytic) | h (field) | d (median read-out) | S_delay / S_H59 / S_dir / S_free | T | Cell |
| --- | --- | --- | --- | --- | --- | --- |
| N nudge (720) | 0.33 [0.01, 0.55] | 3.97 [2.99, 5.05] | 107 s | 201 / 199 / 222 / 422 | 0.47; free − H59 [136, 325] | **fail** |
| Hu human, broadcast (1,569) | −0.12 [−0.39, 0.06] | 1.77 [0.82, 2.54] | 51 s | −62 / 11 / 12 / 21 | 0.55 | uninformative (S_free CI includes 0) |
| Hm human, named (92) | 0.60 [−0.11, 1.31] | 4.39 [2.16, 5.46] | 20 s | 26 / 21 / 19 / 6 | – | uninformative |
| A @-mention (31,873) | 0.14 [0.11, 0.18] | 3.77 [3.47, 4.05] | 21 s | 3,515 / 4,441 / 4,824 / 6,150 | 0.72; free − H59 [1,466, 1,924] | mixed |

- Shared direction θ = 72.7° [70.9, 74.1] (mostly toward talk); kernel K = 1, 0.44, 0.17, 0.10, 0.06, 0.09 over lag bins 0, 1, 2, 3–5, 6–10, 11–30 calls.
- **R_delay is rejected for the message classes** (A: H59 − delay [620, 1,305]; Hu [12, 130]) but **not for nudges** (−1.8 [−8.6, 5.3]): a nudge's amplitude is the pooled one.
- **Post hoc split (rows read 0–2 calls ago vs 3–30):** at the read-out, H59 keeps 80% (N) and 77% (A) of the free fit's skill; in the tail it keeps 0% (N: 0.1 vs 174) and < 0 (A: −24 vs 376). The nudge's free fit has a persistent tail (W→I and W→T +0.3 to +0.5, T→W −0.5 over lags 3–30) on top of a huge pre-read term (W→I +3.3): the nudger fires at agents that just went idle and stay idle-prone, so the tail is plausibly selection, not lever.
- **Inbox decay (P4):** none for nudges (stale/fresh 1.09 [0.89, 1.28]) and mentions (1.03 [0.98, 1.07]); broadcast human messages lose about half (0.57 [0.17, 0.96]).
- At the receiving call, nudges and mentions look alike in the free fit (I→T +2.9 for both; I→W +1.6 vs +0.8).

## Scorecard (period-specific axes)
C 1 (beats the inert model and R_delay on held-out days; loses to class-specific fits) · D 1 (read-out part transfers, full window does not) · G 1 (signs as in the lever table; d reproduces RE-V1's 108 s) · H 1 · I 0.

## Notes
- Baseline has agent and day fixed effects, run length, Markov-2 state, time of day, chatter and bookends; it is fitted once with free kick dummies and held fixed (as an offset) in the kick fits and bootstraps.
