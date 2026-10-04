# H08 × NE32: newcomers in isolated rooms, then merged (2026-07-09 → 07-10, inside #51)

**Verdict:** supported
**Role:** native (round 1b, non-holdout; transition exception c)
**Period:** regime III · #51 head (non-holdout) · GPT-5.6 Sol, Terra and Luna join on 2026-07-09 in three separate one-agent rooms (sol, terra, luna) and move into #general after about 1.5–2 h the same day; Grok 4.5 joins on 07-10 in its own onboarding room and moves to #general after about 2.4 h. New agents start with empty memory.

## Why this unit
DQ9's native test for H08 ("context switched on at merge for isolated newcomers"). An agent that has never received a message from j has, under "context is the coupling", no channel through which j can couple to it, except what the scaffold puts in every prompt (system prompt, goal text, any room snapshot). The ledger lists exactly which messages entered each call, so the first moment each old-timer could reach each newcomer is known by construction.

## Prediction
*Written 2026-10-04 06:41 UTC, before any analysis of these agents' turns.*
Units: (newcomer n ∈ {Sol, Terra, Luna, Grok 4.5}, old-timer j) pairs, for old-timers on #51's roster that day. t_rec(n, j) = t_call of n's first ledger call that received an item from j. Responses of n to j: a talk call of n that names j (`chat_mentions_clean`) or whose `reply_pairs` parent was written by j.
- **N32a (no coupling before context):** during isolation, newcomers' talk turns name no old-timer, or at most at the rate they name old-timers they never receive messages from later (≤ 0.02 per talk).
- **N32b (first response after first receipt):** in ≥ 90% of the pairs (n, j) with any response, n's first response to j comes at or after t_rec(n, j).
- **N32c (the jump):** in the first 2 h after the move, the per-call probability that n's talk names or replies to j is higher at calls that received an item from j (that call or the previous two) than at calls that did not, within newcomer-hour cells.
- **Rival:** names come from outside the chat stream (system prompt roster, the goal text, a room-history snapshot shown on joining): then N32a or N32b fails, and those pairs are counted and reported.

**Verdict rule (fixed now):** supported if N32a and N32b hold; failed if N32b fails (< 70% of pairs); mixed otherwise; descriptive if fewer than 10 responding pairs.

## Result
*Run 2026-10-04 (`analysis/ne32_newcomers.py`, with and without `--mentions-only`). Data: `data/processed/H08-context-is-the-coupling/r1b/NE32.json`, `NE32_mentions.json`. Days: 07-09, 07-10, 07-13 → 07-15 (non-holdout).*

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N32a: no naming of old-timers during isolation | the four newcomers made **no** talk calls while isolated (0 of 0) | untestable (vacuous) |
| N32b: first response to j at or after t_rec(n, j), ≥ 90% of responding pairs | mentions only: **35/35** pairs (100%); mentions or reply author: 37/37. 71 of the 84 pairs received their first item from j only *after* the newcomer had already named someone; 24 of those were later named, every time after receipt. The one old-timer never received was never named | **supported** |
| N32c: response rate higher at calls that just received j | mentions: 0.217 (n = 203 call × old-timer cells) vs 0.014 (n = 2,422); newcomer-stratified difference +0.21. Mentions or reply: 0.315 vs 0.016 | supported |
| Rival: names from outside the chat stream (prompt roster, goal text, room snapshot) | 0 pairs named before receipt | rejected here |

- Median first response: 42 min after the move into #general.
- **Caveat:** reply parents must be visible messages, so reply links satisfy N32b by construction; the mention-only run is the informative one. Four agents, one model family (GPT-5.6 ×3, Grok 4.5), one event.

**Verdict: supported** (N32b and N32c; N32a untestable).

## Notes
- 2026-10-04: folder created with the prediction (round 1b native layer, DQ9 cross-index).
