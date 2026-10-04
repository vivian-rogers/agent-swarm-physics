# H48 × NE32: GPT-5.6 Sol, Terra and Luna start in isolated rooms (2026-07-09)

**Verdict:** n/a
**Role:** native
**Period:** inside #51 (regime III, head). The three GPT-5.6 agents joined on 07-09 in their own rooms (#sol, #terra, #luna) for about 1.5–2 h each and then moved to #general the same day; Grok 4.5 had a ~2.4 h onboarding room on 07-10 (a fourth isolated arm). Not held out. Exception (c): the transition (isolation → merge) is the object.

## Why this period
Isolation switches read-out off by construction: in its own room a newcomer can read no agent. H48's clock should therefore start at the merge, not at the join: no assimilation toward the incumbents during isolation, then assimilation after the merge at the rate other newcomers show from their join. The field rival (newcomer settles onto its role on its own clock) predicts convergence starting at the join, isolation or not.

## Prediction
*Written 2026-10-04 ~07:10 UTC, before running settling on these days.*
- **N4a (primary):** for the isolated newcomers, the assimilation gap does not shrink during isolation: mean gap in the isolation window minus mean gap in the first isolation half ≥ −0.02 (no closing), while it shrinks within the first 2 active hours after the merge (post-merge 2-h mean below the isolation mean) in ≥ 3 of 4 isolated newcomers.
- **N4b:** measured from the merge, the isolated newcomers' τ_a lies inside the range of the non-isolated newcomers' τ_a measured from their joins.
- **Against:** the gap closes during isolation as fast as after the merge (field clock from the join).
- **Credence:** 0.4. Isolation lasted only 1.5–2.4 h, so each newcomer has few statements in it; the test may be unpowered (reported as such if < 4 statements per newcomer in isolation).

## Result
| Native prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| Isolation check | the ledger shows 0 agent messages read by any isolated arm before its merge (Sol 1.96 h, Terra 1.61 h, Luna 1.55 h, Grok 4.5 2.49 h of isolation) | – | confirmed |
| N4a (primary): no closing during isolation; closing within 2 h after the merge, in ≥ 3/4 arms | only Grok 4.5 produced ≥ 4 statements in isolation (16); Sol 1, Terra 0, Luna 0. Grok, bge: gap rose during isolation (−0.11 → +0.08) and fell after the merge (−0.31); gte: gap fell during isolation (−0.01 → −0.12) and fell further after the merge (−0.26) | – | **n/a (1/4 arms powered; models disagree)** |
| N4b: τ_a from the merge inside the non-isolated newcomers' range | no decaying fit detected for any arm (see G51) | – | n/a |

**Reading.** The design is clean (read-out is switched off by construction, as the ledger confirms), but the isolation lasted under 2.5 hours and three of the four arms said almost nothing in it. Combined with G51 (newcomers individuate rather than assimilate), there is no assimilation clock to start. Data: `data/processed/H48-settling-mixing-time/NE32/` (`isolated.parquet`, `series.parquet`, `natives.json`).

## Scorecard (period-specific axes)
- **G:** isolation of read-out confirmed in the ledger. **E:** not scored (unpowered).

## Notes
- Agent messages read during isolation are counted from the ledger (expected ≈ 0 agent items; human/operator onboarding items are allowed).
- 2026-10-04: the ledger's first call for Terra and Luna comes after their move to #general, so join times use `rooms_timeline` (onboarding-room entry), not the first ledger call.
