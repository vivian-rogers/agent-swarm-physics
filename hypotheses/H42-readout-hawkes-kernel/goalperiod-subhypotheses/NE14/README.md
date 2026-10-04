# H42 × NE14: The call clock changes at the regime II → III boundary; does the read-out kernel's weight stay put?

**Verdict:** failed (the call-clock kernel weight shifts more than the exponential one across the boundary; A's timescale moves against the read-out lag)
**Role:** native (exploratory, non-holdout; across the boundary)
**Period:** NE14 (consolidate + pause tools, perma-computer-use; the regime boundary on 2026-03-24). Units on the regime-II side: #35 (5 days), #36a (1 day); regime-III side: #36b, #36c (2 days each), #37 (3 days). Named exception (c): the boundary is the object; each unit is fitted on its own and only fitted parameters are compared.

## Why this period
NE14 is the non-holdout stand-in for the brief's NE20 (one tool call per turn), which sits in the locked holdout. At NE14 the call clock changes for everyone: regime-II agents make scheduled chat-mode calls about every 74 s plus computer-use sessions; regime-III agents make chained computer-use calls about every 13 s with timer pauses. A kernel defined on the recipient's call clock should keep its per-message weight when the time base changes. A kernel in wall-clock time from the message's arrival has to move its timescale and weight to follow the read-out delay.

## Prediction
*Written 2026-10-04 07:45 UTC, before running any of these units through the pipeline. Disclosed: #37 was fitted once while testing the batch runner (world pr B n_cross 0.22, world B 0.03, world A A 0.03); no other unit here was fitted.*
- **N2a:** across the boundary (median of the regime-II units vs median of the regime-III units), |Δ log n_cross| is smaller for world B's B than for world A's A.
- **N2b:** world A's fitted A kernel mean timescale (contribution-weighted over the 10–300 s grid) moves in the same direction as the units' mean read-out lag.
- **N2c:** in world B, B ≥ A_g on held-out likelihood on both sides (units with ≥ 2 days).
- **Counts against:** N2a reversed (B's weight shifts more than A's), or A's timescale moving against the read-out lag.
- **Confounds:** NE41 (forced erasure) and NE16 start inside the same week; the goal changes from #35 to #36 to #37; N is 5 units, so this is descriptive at best.

## Result
| unit | side | days | msgs | read-out lag median / mean (s) | world B n_x(B) | world A n_x(A) | A mean τ (s) | world B gain(B), mnats/event | B − A_g held out |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 35 | II | 5 | 2079 | 13 / 41 | 0.010 | 0.091 | 54 | −0.4 | −4.5 |
| 36a | II | 1 | 465 | 17 / 44 | 0.005 | 0.000 | 109 | – | – |
| 36b | III | 2 | 564 | 20 / 108 | 0.010 | 0.000 | 110 | −5.3 | +6.8 |
| 36c | III | 2 | 552 | 16 / 62 | 0.052 | 0.081 | 30 | +20.2 | −26.5 |
| 37 | III | 3 | 698 | 18 / 116 | 0.027 | 0.032 | 30 | +4.8 | −4.8 |

| prediction | observed | verdict |
| --- | --- | --- |
| N2a \|Δ log n_x\| smaller for world-B B than world-A A | B: 0.007 → 0.027 (\|Δlog\| 1.27); A: 0.045 → 0.032 (0.36) | **failed** |
| N2b A's timescale follows the read-out lag | lag mean 43 → 108 s; A's τ 81 → 30 s | **failed** (opposite) |
| N2c B ≥ A_g held out on both sides | true only in 36b (1 of 4) | **failed** |

- **Reading:** the read-out kernel is *not* invariant to the change of call clock. In the call-clock world, talk excitation per message rises from ≈ 0.007 to ≈ 0.03 when regime III starts; the exponential kernel's weight barely moves while its timescale shortens.
- **Interpretation (post hoc):** regime-II chat-mode calls are scheduled and talk at them is driven by call type, not by what was read (as in G19). Regime-III computer-use calls read messages mid-task, and a little talk becomes message-driven.
- **Power:** 5 units, 13 days, goal changes at both boundaries (#35 → #36 → #37), NE41 and NE16 in the same week. Descriptive.
