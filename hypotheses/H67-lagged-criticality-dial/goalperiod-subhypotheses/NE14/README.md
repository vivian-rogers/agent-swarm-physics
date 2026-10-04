# H67 × NE14: regime II → III inside goal #36 (2026-03-23 → 03-27)

**Verdict:** descriptive
**Role:** native (exploratory)
**Period:** goal #36 (interact with outside agents) · two rooms (#best / #rest) · 12 agents · units 36a (regime II, 1 day), 36b (NE14 perma-computer-use + NE41 forced erasures, 2 days), 36c (NE16 memory fix, 2 days).

## Why this period
The same goal, roster and rooms cross the scaffold switch. The call cadence changes about 5× (scheduled chat-mode calls about every 74 s → chained computer-use calls about every 13 s, with timer pauses). A coupling that runs on the call clock (H40: per-call coupling is cadence-free in regimes II–III) should keep its per-read jump J₁* and its loop gain g_lag. The equal-time 1-min dial depends on how many responses land inside the same minute, so it should move with cadence.

## Prediction
*Written 2026-10-04 19:35 UTC, before running on this period. Seen: H25's P7a (talk dial +0.05 across the 03-24 switch, CI spanning 0) and H42/H50's regime medians; no H67 number.*
- **N14a:** |log(g_lag(36b ∪ 36c) / g_lag(36a))| < log 2 (the lagged gain changes by less than a factor 2). [0.45]
- **N14b:** the ratio g_eq / g_lag rises from 36a to 36b ∪ 36c (faster calls put more of the response inside one minute). [0.55]
- **Counts against the call-clock reading:** g_lag changes by more than a factor 2 while g_eq/g_lag does not rise.
- Caveat written now: 36a is one day (12 agents); its CI will be wide, so a "within factor 2" pass may be uninformative. The verdict is *descriptive* if the 36a CI width exceeds the 36a estimate twice.

## Result
*Run 2026-10-04 ~20:20 UTC.*

| Statistic | 36a (regime II, 1 day) | 36b ∪ 36c (regime III, 4 days) |
| --- | --- | --- |
| g_lag [95%] | −0.060 [−0.146, 0.030] | 0.118 [0.062, 0.175] (random effects) |
| g_eq (same data) | 0.048 | 0.158 |
| median call interval | 13.7 s | 12.0 s |

- **N14a:** not scorable as a ratio: 36a's g_lag is consistent with 0 and its CI width (0.18) exceeds twice its estimate, so the pre-set rule makes the native **descriptive**.
- **N14b:** not scorable (the 36a ratio is undefined).
- **What the data show:** the premise was wrong. Regime II (#33–#36a) already runs chained computer-use calls (median interval 13.7 s vs 12.0 s after NE14), so NE14 is not a cadence change. The lagged gain switches on at the boundary (0 → 0.12) while cadence stays fixed. This matches H42 and H50: read-out talk coupling is a regime-III property.

