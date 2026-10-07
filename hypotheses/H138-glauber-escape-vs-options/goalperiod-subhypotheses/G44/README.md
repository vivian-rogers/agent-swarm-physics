# H138 × G44: two rooms, two kickoffs, two ownership prices (#44, 2026-05-26 → 2026-06-01)

**Verdict:** descriptive
**Role:** exploratory (replication + native N2)
**Period:** regime III · mode C · 16 agents (#best planned, #rest free) · two rooms · 4 days. The fine-tuned leader (NE31) is present.

## Why this period
Both rooms run on the same days, so calendar, scaffold and nights are shared. The rooms differ in their kickoff and in their ownership price (H94: λ_own #best 10.2 vs #rest 4.1 nats) and in how scattered the work is (H128: the free room stays at domain-wall fraction ≈ 0.92). Work switches: 67 (H11 round 2). A cross-room contrast of the per-call leave hazard at fixed days tests whether escape follows the room's menu.

## Prediction
*Written 2026-10-07 ~09:10 UTC, before running on this period. Seen: H94's and H128's G44 numbers above and the switch total; no q count and no hazard statistic.*
- **N2 (native):** at matched owner status, the per-call hazard ratio #rest/#best equals (q̄_room,rest − 1)/(q̄_room,best − 1) within ×2. Credence 0.2.
- **P1 (replication):** ε̂_q > 0 with CI above 0, pooled over both rooms with a room fixed effect. Credence 0.25 (4 days; may be untestable at ≥ 25 leaves per room).
- Counts against: the hazard ratio outside ×2 or of the wrong sign.

## Result
*Round 1, 2026-10-07 (exploration). Estimator: cloglog hazard per own call, agent effects, active-time spline, agent-cluster sandwich (card Amendment A1). Power from the real-skeleton synthetic (W1 worlds, 200 replicates). The work power at ε_q = 0.5 is below 0.8 in every unit (card A2), so a work null is unpowered.*

| Channel · unit | Leaves | ε̂_q [95% CI] | permutation p | ε̂_q − ε̂_lead [boot CI] | ε̂_Z [CI] | β̂_own [CI] | power at ε 0.5 / 1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| work · 44 | 58 | 0.27 [−5.21, 5.74] | 0.839 | −0.37 [−4.86, 5.26] | 0.10 [−1.09, 1.28] | 3.90 [−1.82, 9.62] | 0.09 / 0.10 |
| attention · 44 | 149 | −1.24 [−4.13, 1.65] | 0.099 | −1.46 [−4.99, 1.64] | −0.39 [−0.72, −0.06] | −0.90 [−1.59, −0.21] | 0.09 / 0.24 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N2: #rest/#best hazard ratio = q_room ratio within ×2, at matched owner status | #best has **15 leaves** (< 25), #rest 43: descriptive. HR 1.97 [0.41, 9.53] (cloglog with room, owner and stay terms; 15 agent clusters). Predicted (10.4/3.1) = 3.32. Ratio 0.59 | **descriptive** (inside ×2, same sign; CI spans 1) |
| P1 (work, both rooms): ε̂_q CI above 0 | 0.27 [−5.21, 5.74] | fails; unpowered (0.09) |
| Attention (secondary) | −1.24 [−4.13, 1.65] | fails; unpowered |

- Period verdict: **descriptive**. Raw leave rates: #best 0.24, #rest 0.35 per 100 own calls. The free room has more open options in the agent's room (q_room 10.4 vs 3.1) and a higher leave rate, as Glauber predicts, but one room has too few leaves to test it.
- H94's prices (#best 10.2, #rest 4.1 nats) would also predict more leaving in #rest; the room contrast cannot separate the menu from the stay field.
- Figure: `figures/n2_rooms.png`.

## Scorecard (period-specific axes)
C 0; E 0 (the cross-room contrast is descriptive: 15 #best leaves); H 0 (menu and stay field not separable).

## Notes
- If either room has < 25 leaves, N2 is reported as descriptive.
