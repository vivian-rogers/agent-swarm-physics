# H31 × NE42: room merge and split at a fixed roster, #39 → #40 → #41 (2026-04-27 → 2026-05-15)

**Verdict:** mixed
**Verdict (1b):** mixed (native: λ₂ up at merge, not down at split)
**Role:** native (round 1b; transition exception c: the merge and split are the object)
**Period:** regime III · #39 (two rooms, #best and #rest; own worlds) → #40 (14 agents merged into #universe-coordination on 05-04; GPT-5 alone in #rest) → #41 (split back on 05-11; two rooms) · N ≈ 15 · 15 active days in all (5 per period).

## Why this unit
DQ9 cross-index: H31 → NE42. An A-B-A in room structure at a fixed roster: the merge puts 14 agents in one broadcast room, which raises the exposure graph's weighted spectral gap (λ₂ ∝ N × message rate in a broadcast room), and the split lowers it again. Model D (diffusion, τ ∝ 1/λ₂) then predicts faster consensus in #40 than in #39 and #41. The confound is that the goal changes at the same boundaries (own worlds → connect them → novel research): the design compares predictors across the boundary and reports consensus descriptively.

## Prediction
*Written 2026-10-04 07:26 UTC, before computing anything on the round-1b data.* What I had seen: round 1's per-period results (#39: no project consensus, own worlds; #40: the hub frozen at the kickoff; #41: #rest τ 4.0 and 13.5 h; round-1 λ₂ values per block); H53's note that #40's hub was link-seeded 2.4 min into the kickoff.

- **NE42-a (structure, A-B-A):** with ledger visibility, the merged room's λ₂^w,sym in #40 exceeds that of every room block in #39 and in #41 (ratio ≥ 1.5 to the larger one), and the reading rate u does not fall. Model D then predicts τ(#40) < τ(#39), τ(#41).
- **NE42-b (consensus, attention):** #40's consensus is field-set: the hub is frozen or instant (first window), so no gradual τ exists in #40 to test D's speed-up; #39 has no consensus; #41 has ≥ 1 gradual event. Verdict on D across NE42: inconclusive (no gradual event in the B phase).
- **NE42-c (consensus, work space):** #39 has no work consensus (own worlds); in #40 the hub reaches a work majority, but later than in attention (not frozen; τ ≥ 1 h from its first commit), so attention leads work.
- **What would count against D:** gradual consensus in #40 that is no faster than in #39/#41 despite the λ₂ jump.

## Result
`analysis/round1b.py` → `data/processed/H31-consensus-time-spectral-gap/r1b/round1b_summary.json` (`NE42`). Predictors with ledger visibility (whole block-period).

| Period | Room | N_b | msgs / active h | reading rate u (1/h) | λ₂^w,sym (1/h; round 1) | E-P attention (frozen / instant / gradual; τ) | E-P work |
| --- | --- | --- | --- | --- | --- | --- | --- |
| #39 (A) | #best | 4 | 6.2 | 3.7 | 4.4 (4.5) | none (8 projects) | none |
| #39 (A) | #rest | 11 | 36.7 | 20.3 | 19.5 (19.5) | none | none |
| #40 (B) | #universe-coordination | 14 | 85.2 | 38.6 | **46.7** (46.8) | hub frozen (1 / 0 / 0) | hub frozen (1 / 0 / 0) |
| #41 (A) | #best | 4 | 23.9 | 13.7 | 18.1 (18.1) | 1 / 0 / 0 | 1 / 0 / 0 |
| #41 (A) | #rest | 11 | 82.6 | 39.9 | **44.2** (44.2) | 1 / 0 / 2; τ 13.5, 4.0 h | 1 / 0 / 2; τ 5.5, 2.0 h |

| Test | Prediction | Observed | Verdict |
| --- | --- | --- | --- |
| NE42-a λ₂ A-B-A | #40 exceeds every #39 and #41 block by ≥ 1.5× | 2.40× the larger #39 room, but only 1.06× #41's #rest (its message rate rose to #40's level after the split) | **failed** (merge side only) |
| NE42-b attention consensus | #40 field-set (frozen or instant); #39 none; #41 ≥ 1 gradual | as predicted | **supported**; D untestable |
| NE42-c work consensus | #39 none; #40 hub reaches a work majority later than in attention (τ ≥ 1 h) | #39 none; the #40 hub is frozen in work too (majority of committers in the first window with ≥ 3 committers) | **partly** |

**Reading.** Merging the worlds into one room roughly doubled message volume per agent and so the weighted spectral gap, but splitting back did not undo it: #41's research room kept #40's chattiness. The only #40 consensus, the universe hub, was seeded at the kickoff (H53: link 2.4 min in; H27: half the room mentioned it within 4 min, and half the room committed to it within 19 min), so it is field-set in both attention and work. NE42 therefore gives no leverage on the λ₂ law: the B phase has no gradual consensus to compare. As an intervention on λ₂ it is also confounded: the post-split rooms did not return to the pre-merge rate.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| E interventional | 0 | the λ₂ step is real at the merge but not reversed at the split, and there is no gradual consensus in the B phase |
| G ground truth | 1 | the hub frozen at the kickoff in both channels matches H53's link seeding and the goal text |

## Notes
- 2026-10-04: folder created for round 1b (native layer).
