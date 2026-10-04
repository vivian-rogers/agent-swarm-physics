# H05 × G51 (#focus, 08-05 → 08-24): a self-selected second room

**Verdict:** n/a
**Verdict (1b):** mixed (the ledger confirms the cut; talk DiD right sign, n.s.)
**Role:** native
**Period:** #51g, regime III, non-holdout (the #51 tail from 09-07 is held out and not used). Gemini 2.5 Pro and Claude Opus 4.8 leave #general for #focus on 08-05 and return around 08-24. The bookends stop the same day (NE43a), so active spins are confounded.

## Why this period
It is the only non-holdout room cut that the agents chose themselves, and it is long: 12 days during the cut. It replicates NE15's C1 off the holdout.

## Prediction
Written 2026-10-04 08:35 UTC (card, R1b-N2): the ledger shows the cut (reads between the #focus pair and #general fall ≥ 90%); the talk κ_x DiD of the cut arm is < 0, expected n.s.

## Result (`analysis/r1b_reads.py`, `analysis/explore_rooms.py` X3 focus_on/off)
| Measure | Fixed bins | + trim |
| --- | --- | --- |
| Cut-arm ledger reads per pair-day, pre → during → post | 95 → 4.4 → 101 (−95%) | 96 → 4.4 → 105 |
| The #focus pair's reads of each other | 124 → 273 → 141 | same |
| Cut-arm talk κ_x DiD (on) | −0.006 (perm p 0.28) | −0.009 (p 0.20) |
| Return (off), add-arm talk κ_x DiD | +0.009 (p 0.12) | −0.001 (p 0.96) |

The two #focus agents read each other twice as much while isolated: attention went to the remaining partner, as at NE42 and NE15.
