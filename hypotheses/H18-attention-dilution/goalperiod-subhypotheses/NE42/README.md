# H18 × merge 2026-05-04 / split 2026-05-11 (#39 → #40 → #41)

**Verdict:** failed
**Verdict (1b):** failed (round 1b native, 2026-10-04: k rises ×1.48/×1.44 in #40, but per-pair reply uptake is higher than in #39 and lower than in #41; k does absorb the #40 contrast in the joint fit; round-1 verdict kept above)
**Role:** native (round 1b, non-holdout; transition exception c; round 1 ran it as exploratory)
**Period:** regime III. On 05-04 (start of #40) #best and #rest merged into #universe-coordination, except GPT-5, left alone in #rest; on 05-11 (start of #41) they split back to the same partition. An A-B-A. Both boundaries coincide with goal changes (#39 mode I → #40 mode C → #41 mode I), so this is direction-only evidence. **No NE ID exists for this event yet** (proposed in the round-1 report); the folder is named `NE42` so that `infra/overview/build_overview.py` does not pick up a made-up number. Rename it when an ID is assigned.

## Why this event
The merge roughly doubles the room each agent reads, so under a fixed budget its k per turn should rise and its per-pair uptake fall, then recover after the split, with the total S per turn unchanged (HH90's row-sum conservation).

## Prediction
*Written 2026-10-03, before any H18 real-data run.*
- For agents merged on 05-04 (not GPT-5): k̄ per talk turn higher in #40 than in #39 and in #41.
- Per-pair uptake p̄ (and the agent-level mean of fitted θ_{i,d}·h at each period's k) lower in #40 than in #39 **and** lower than in #41; the drop is within ×2 of the k̄ ratio.
- S per talk turn changes by < 30% between sides.
- Within-period β̂ similar on all three sides (|Δβ| < 0.4).
- Counts against: per-pair uptake does not fall in #40 in both comparisons, or S scales with k.

## Result
*Run 2026-10-03 (`analysis/spanning.py`; `data/processed/H18-attention-dilution/spanning.json`; figure `figures/merge.pdf`).* Agents merged on 05-04 and present on all three sides: n = 13 (GPT-5 excluded).

| Side | k̄ per talk turn | per-pair uptake p̄ | S per talk turn | β̂ (within side) | units |
| --- | --- | --- | --- | --- | --- |
| #39 (two rooms) | 7.4 | 0.091 | 0.31 | 0.62 | 2270 |
| #40 (merged) | 10.9 | 0.117 | 0.54 | 0.58 | 6911 |
| #41 (split back) | 7.6 | 0.237 | 0.79 | 0.65 | 5777 |

Day-bootstrap ratios of p̄:
- #40/#39 = 1.29 [0.76, 2.07];
- #40/#41 = 0.49 [0.36, 0.66].

Per agent: p̄ in #40 above its #39 value for 6/13 agents, and above its #41 value for 2/13.

| Prediction | Observed | Verdict |
| --- | --- | --- |
| k̄ higher in #40 than in #39 and #41 | ×1.48 and ×1.43 | pass |
| per-pair uptake lower in #40 than both | higher than #39, lower than #41 | **fail** |
| S per turn within ±30% | 1.71× and 0.68× | **fail** |
| β̂ similar on all sides (\|Δ\| < 0.4) | spread 0.06 | pass |

**Reading.** The *within-period* dilution exponent is stable across the merge. But the *level* of addressing changes far more between goal weeks (#41's research week addressed peers 2–3× more often) than k does. With goal changes on both boundaries, a merge-driven drop in per-pair uptake cannot be seen against week-to-week goal effects. Direction-only evidence, as warned; the prediction fails.


## Round 1b prediction (native, improved data)
*Written 2026-10-04 06:36 UTC, before the round-1b run on this unit.* Same A-B-A, now on the context ledger (k = items received since the previous talk call) with reply labels (`reply_pairs.parent`, primary) and mentions (secondary), and with a design only this A-B-A allows: one joint fit over the three sides with agent×day propensities and a side effect, so that the side contrast can be read with and without k.
- **N2a:** for the agents merged on 05-04 (not GPT-5), ledger k̄ per talk turn is ≥ 1.3× higher in #40 than in #39 and in #41.
- **N2b:** per-pair reply uptake p̄ in #40 is lower than in #39 **and** lower than in #41.
- **N2c (k explains the side effect):** in a joint M_pow fit (#39 + #40 + #41, agent×day propensities fitted without side terms, then side effects estimated on the residual log-propensities), the #40-vs-flanks log-uptake contrast shrinks by ≥ 50% when k enters.
- Counts against: N2b fails (as round 1's mention version did: uptake followed the goal week, not k).
- Prior credence (Claude, 2026-10-04): 0.3 (round 1 failed on the same event; reply labels remove mention noise but not the goal confound).

**Verdict rule (fixed now):** supported if N2a and N2b hold; failed if N2b fails; mixed if N2b holds but N2c does not.

## Round 1b result (native, 2026-10-04)
*Run `analysis/r1b_native.py` on the ledger scheme (`data/processed/H18-attention-dilution/r1b/native.json`). 13 merged agents (GPT-5 excluded). Cells: k̄ per talk · per-pair uptake p̄ · senders responded to per talk S · within-side β̂.*

| Response | #39 | #40 (merged) | #41 | p̄ ratio #40/#39 / #40/#41 (day bootstrap) | N2c: #40 vs flanks, log-propensity, without k → with k |
| --- | --- | --- | --- | --- | --- |
| reply parent (primary) | 7.4 · 0.048 · 0.16 · 1.02 | 11.0 · 0.062 · 0.28 · 0.82 | 7.6 · 0.145 · 0.48 · 0.90 | 1.29 [0.86, 1.88] / 0.42 [0.32, 0.54] | -0.24 [-0.47, -0.10] → -0.03 [-0.27, 0.11] (86% shrink) |
| mention | 7.4 · 0.092 · 0.32 · 0.63 | 11.0 · 0.117 · 0.54 · 0.58 | 7.6 · 0.240 · 0.80 · 0.65 | 1.28 [0.76, 2.13] / 0.49 [0.36, 0.66] | -0.34 [-0.68, -0.08] → -0.16 [-0.54, 0.11] (53% shrink) |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N2a: k̄ ≥ 1.3× in #40 vs both flanks | ×1.48 and ×1.44 | pass |
| N2b: per-pair reply uptake lower in #40 than in #39 and #41 | higher than #39 (1.29, CI includes 1), lower than #41 (0.42) | **fail** |
| N2c: the #40 contrast shrinks ≥ 50% once k enters the joint fit | replies: −0.24 → −0.03 (86%); mentions: −0.34 → −0.16 (53%) | pass |

- **Reading:** with agent×day propensities fitted jointly over the three weeks, the merged week's per-message uptake *is* lower than its flanks' at fixed propensity, and k explains most of that gap. But the raw per-pair rates follow the goal week (#41's research week replies 2–3× more), so the pre-registered raw comparison still fails, as in round 1.

**Verdict (1b): failed** (N2b, as pre-registered; N2c passes).

## Notes
- 2026-10-03: folder created with the prediction, before any H18 real-data run.
- 2026-10-03: run; results above.
