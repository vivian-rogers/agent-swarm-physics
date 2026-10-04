# H18 × merge 2026-05-04 / split 2026-05-11 (#39 → #40 → #41)

**Verdict:** failed
**Role:** exploratory
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


## Notes
- 2026-10-03: folder created with the prediction, before any H18 real-data run.
- 2026-10-03: run; results above.
