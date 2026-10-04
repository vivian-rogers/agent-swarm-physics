# H83 × G38: newcomers joining goal period #38 (2026-04-02 → 2026-04-24)

**Verdict:** supported
**Role:** native (exploratory)
**Period:** regime III · up to 14 agents · units 38a, 38b, 38c, 38d, 38e · non-holdout days 17. Joins: Claude Opus 4.7 (2026-04-17), Kimi K2.6 (2026-04-22).

## Why this period
#38 has two rooms (#best, #rest) with at least two veterans each on 04-20 → 04-24, and two newcomers arrive (Claude Opus 4.7 on 04-17, Kimi K2.6 on 04-22). A newcomer reads only its own room (H05, H41).

## Prediction
*Written 2026-10-04 20:34 UTC, before running on this period (Amendment A1.6).*
- **Why native:** #38 has two rooms (#best, #rest) with at least two veterans each on 04-20 → 04-24, and two newcomers arrive (Claude Opus 4.7 on 04-17, Kimi K2.6 on 04-22). A newcomer reads only its own room (H05, H41).
- **N2 prediction:** R_new = mean over the newcomers' agent-days of [alignment with own-room veterans − alignment with the other room's veterans] is > 0, with a day-and-agent bootstrap 95% CI above 0: convergence follows the read population. Descriptive: R_new / R_vet (veterans' own-room preference on the same days).
- *Counts against:* R_new ≤ 0 (the newcomer aligns with the whole village alike: a field, not reading).
- Kimi K2.6 posts about 3 statements a day, so Opus 4.7 carries most of the statistic. Both joins also enter the card-level replication.

## Result
*Run 2026-10-04 20:36 UTC (`analysis/replication.py`, `analysis/natives.py`) → `data/processed/H83-enculturation-of-newcomers/replication/replication.json`, `natives/natives.json`.*

| Join | Ḡ_E | ΔG (bge) | ΔG (gte) | ΔK | ΔS (style) | veteran items read, days 1–7 | templated |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Claude Opus 4.7 | -0.102 | +0.009 | +0.057 | -0.093 | -6.312 | 352 | supported |
| Kimi K2.6 | -0.027 | +0.010 | -0.038 | -0.024 | +22.304 | 169 | supported |

**N2 (two rooms, 04-20 → 04-24, both rooms with ≥ 2 veterans).**

| Statistic | bge | gte |
| --- | --- | --- |
| R_new (own-room minus other-room alignment, newcomers) | +0.178 [+0.099, +0.262] | +0.181 [+0.126, +0.242] |
| R_vet (veterans, same days) | +0.161 | +0.148 |
| R_new / R_vet | 1.11 | 1.22 |

- 7 newcomer agent-days (37 statements by Opus 4.7, 11 by Kimi K2.6); 54 veteran agent-days.
- **Verdict: supported.** From their first days the newcomers align with the veterans of the room they read, as strongly as the veterans do (ratio 1.1–1.2). Room alignment is acquired at once, not over two weeks: it is conversation shared through reading (plus the room's own topic), not a slow culture. A room-specific field beyond the projected room kickoff is not excluded.

## Scorecard (period-specific axes)
- G (ground truth): 1. Room membership (structural) predicts which veterans a newcomer aligns with.
- E: 1 (rooms route the convergence; no slow component seen).
