# H50 × NE43: #51 lever switch-offs: bookends off after 08-04, nudges off after 08-20 (2026-07-29 → 2026-09-04, non-holdout; segments A 07-29..08-04, B 08-05..08-20, C 08-21..09-04)

**Verdict:** mixed (core supported: the nudge path is gone after 08-20, peer coupling and the day-start field persist; two locked numeric bounds missed on the trim variant)
**Role:** native
**Period:** 2026-07-29 → 2026-09-04, non-holdout; segments A 07-29..08-04, B 08-05..08-20, C 08-21..09-04.

## Why this period
The `automated` speaker carries two inputs that switch off at different dates (found in the H50 scheme build): the daily pause/resume bookends (last on 08-04) and the nudges (last on 08-20). The scaffold's daily start and stop continue. So the input paths can be removed one at a time while the peer channel stays: an intervention on the transfer function (axis E). Confounds: the #focus room split starts 08-05 (A vs B); the rooms merge back on 08-24 (inside C); roster joins 08-28, 09-01, 09-03, 09-04.

## Prediction
*Written 2026-10-04 07:00 UTC, before running this test.*
- (i) The nudge path is present in B (nudge→target gate in talk or act, onset hop ≥ 2) and absent in C; its share of activity co-movement in B is small: Δf_F(nudge classes) < 0.05 (nudges hit one agent at a time).
- (ii) Scaffold, not message: the day-start step response is unchanged when the bookend messages stop (A vs B): dispersion of agents' first calls of the day changes by < 50%, and the activity edge kernel G30 keeps its sign and stays within its A-segment CI.
- (iii) The peer read-out jump J₁ (talk) in C lies within the B 95% CI or within ±50% of B.
- (iv) Edge-trimmed activity per-pair co-movement ρ̄ (trim variant) in C within ±25% of B.
- *Against:* ρ̄ falls by > 25% from B to C (the nudger carried co-movement), or J₁ collapses in C, or the edge step disappears with the bookends (agents started by the message).

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/NE43/` (`NE43A/B/C.json`, `native.json`). Figure: [`figures/NE43_switchoffs.pdf`](figures/NE43_switchoffs.pdf). Segments: A = 5 days, N = 27; B = 12 days, N = 27; C = 11 days, N = 32.

| prediction | observed | verdict |
| --- | --- | --- |
| (i) nudge path present in B, gone in C | nudge → target, talk J₁ = 0.213 [CI lo 0.068], onset hop 1; C has no nudges | yes |
| (i) nudge share of activity co-movement in B < 0.05 | Δf_F(nudge classes): span 0.028, trim 0.083, talk 0.022 | partly (span, talk yes; trim no) |
| (ii) day-start step unchanged when the bookends stop (A → B) | first-call onset IQR 21.7 s → 22.5 s (ratio 1.03; 1.6 → 1.9 call cycles); activity edge G30 6.37 [4.06, 9.62] → 5.46 [3.83, 7.23] → C 6.31 [5.62, 7.01] | yes |
| (iii) peer J₁ in C within B's CI or ±50% | B 0.019 [0.013, 0.024], C 0.013 [0.009, 0.018]; ratio 0.69 | yes (±50%) |
| (iv) edge-trimmed activity ρ̄ in C within ±25% of B | trim 0.0088 → 0.0125 (ratio 1.41); span 0.0152 → 0.0140; full 0.0620 → 0.0660 | no on the locked variant (rose 41% from a near-zero base); span and full within ±10% |

**Reading.** The nudger is a targeted field: a nudged agent talks more at the call that reads the nudge (hop 1), but nudges move one agent at a time and carry at most a few percent of activity co-movement, so switching them off leaves co-movement where it was (it did not fall; the trim variant even rose from a near-zero base). The daily bookend messages are announcements, not inputs: when they stop (A → B) agents still start within about 22 s of each other (1.6–1.9 call cycles) and the day-start step response keeps its size. The scaffold, not the message, starts agents. Peer coupling persists without either lever (C's jump is 0.69 × B's, inside ±50%). Against: Δf_F(nudge) on the trim variant is 0.08, above the 0.05 bound, and the trim ρ̄ bound is missed in the direction opposite to the 'against' clause. Confounds: #focus split on 08-05 (A vs B), merge on 08-24 and roster joins in C. A's J₁ is lower (0.009) than B's (0.019).

## Scorecard (period-specific axes)
- **E (interventional):** two input switch-offs inside one period. The model's predictions (nudge path vanishes, coupling persists, schedule field persists without its message) hold qualitatively; two numeric bounds missed on the trim variant.
- **G (ground truth):** the bookend stop date (08-04) and nudge stop date (08-20) are read off the data; the scaffold keeps starting agents at 16:01 UTC every day.
## Notes
