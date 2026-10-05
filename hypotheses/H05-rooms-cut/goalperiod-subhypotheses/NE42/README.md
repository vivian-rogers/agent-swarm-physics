# H05 × NE42: the #best/#rest A-B-A (merge 05-04, split 05-11), with ledger read counts

**Verdict:** supported
**Verdict (1b):** supported (HH248 holds; stay pairs recouple at the split)
**Verdict (2):** mixed (artifacts split with the rooms; the coupling jump exceeds dilution)
**Role:** native
**Period:** #39 → #40 (merged in #universe-coordination; GPT-5 left in #rest and excluded) → #41; regime III; non-holdout.

## Why this period
It is the only non-holdout reversal at a fixed roster, so the channel (and the ledger read counts) is switched on and then off for the same pairs. This makes it the natural intervention on reads for HH248 ("rooms are only a read-out filter").

## Prediction
Written 2026-10-04 08:35 UTC, before running (card, "Round-1b predictions for the new tests": R1b-HH248, R1b-N3).
- (HH248) Given log(1 + ledger reads), co-location adds no talk coupling.
- (N3) Stay pairs' reads per partner rise at the split; so does their talk κ_x, relative to the merge change; MF J_in on the #39 partition is higher in #41 than in #40.

## Result (`analysis/r1b_reads.py`; `data/processed/H05-rooms-cut/r1b/r1b_reads.json`)
| Test | Fixed bins | + DQ8 trim |
| --- | --- | --- |
| HH248: β(co-location) without → with reads (pooled regime III, talk κ_x) | +0.0123 (z 5.1) → +0.0013 (z 0.2); δ(reads) z 2.1 | +0.0131 (z 4.4) → +0.0008 (z 0.1); δ z 2.2 |
| N3 reads per stay pair: #39 / #40 / #41 | 31 / 56 / 68 per pair-day; split +12.5 [6.3, 18.7] | split +15.8 [9.7, 22.1] |
| N3 talk κ_x of the 42 stay pairs | +0.011 / +0.002 / +0.024; split − merge **+0.032 [0.017, 0.048]** | +0.030 [0.008, 0.052] |
| N3 MF J_in (#39 partition) | 0.17 / −0.02 / 0.06 [0.01, 0.08] | 0.12 / −0.01 / 0.07 |

Co-location and log reads correlate 0.82, so HH248's mediation test has little leverage. The #40 merged week also carries a shared objective (goal confound).

## Notes
- The cut-arm DiDs of round 1 (X3 merge and split) are in the card's round-1b table: the split DiD is now significant (κ_x −0.020, p 0.027).

## Round 2 (2026-10-05)
Predictions (card, "Round 2", written 2026-10-05 03:25 UTC): R1-P1 cut pairs' co-editing falls ≥ 50% at the split; R2-P3 the merge drop of stay pairs' talk κ_x is no larger than dilution predicts (N_room^−0.45: ×0.85 at the merge, ×1 at #41 vs #39). R2-P3 is not blind (the round-1b levels were known).

- R1-P1: cut pairs co-edit share 0.00 (#39) → **0.56** (#40 merged) → **0.00** (#41): **supported**. Rooms and artifacts move together.
- R2-P3: stay pairs (39) κ_x 0.0106 → 0.0004 → 0.0226; dilution predicts 0.0093 at #40. Excess merge drop +0.0089 [0.0007, 0.0168]; #41 − #39 = +0.012 [0.003, 0.021]: **failed**. The jump is too large for dilution; #40's shared objective (a goal field) is the likely rest.
- Source: `analysis/r2_run.py`, `data/processed/H05-rooms-cut/r2/r2_results.json`.
