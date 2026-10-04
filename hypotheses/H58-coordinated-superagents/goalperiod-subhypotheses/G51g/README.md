# H58 × G51g: #51 #focus room (08-05 -> 08-24): a self-selected channel cut (2026-07-09 → 2026-08-24)

**Verdict:** descriptive
**Role:** native
**Period:** regime III · units 51b, 51c · 33 non-holdout days. Units are H01 round 2's (card F1).

## Why this period
A channel cut inside the stationary #51 head: from 08-05 some agents work in a separate #focus room (chat visibility follows rooms), with the goal, hours and roster fixed. If coordination is held in artifacts, it should survive the cut; if it is carried by chat, split pairs should lose it.

## Prediction
*Written 2026-10-04, before the #focus analysis (card N3).* **Observable:** pair coordination gain on the pair's joint artifacts, before (51b, 07-09 → 08-04) and during the #focus era (51c, 08-05 → 08-24), for pairs split by the cut (one member mostly in #focus, the other in #general) vs pairs kept together; DiD with a pair bootstrap. Qualifying 51c units that contain members of both rooms. **Prediction (card):** DiD ≥ −0.5 × the split pairs' pre-cut mean (coordination is artifact-held and survives a channel cut); qualifying 51c units span both rooms. **Falsified if** DiD < −0.5 × pre mean with the CI below. **Caveats:** #focus is self-selected; very few agents moved (the rooms table shows two agents with > 50% of their 51c bins in #focus), so n is small. **My prior:** little coordination to lose; DiD ≈ 0 and uninformative.

## Result
Data: `data/processed/H58-coordinated-superagents/results/` (units/*.json, replication.json, natives.json, reacq.json); pipeline `analysis/run.py`, `natives.py`, `reacq.py`.

- #focus agents (> 50% of 51c bins in #focus): Gemini 2.5 Pro, Claude Opus 4.8.
- Pairs with a joint-artifact gain in both 51b and 51c: 80 (11 split by the cut, 69 kept together).
- Split pairs: -0.008 → -0.001; kept pairs: +0.005 → +0.020 bits per working member-bin.
- DiD (split − kept) -0.008, 95% bootstrap CI [-0.029, +0.013].
- Qualifying 51c units: 0; spanning both rooms: 0.

**Verdict rule (card N3):** falsified if DiD < −0.5 × the split pairs' pre mean with the CI below 0. With 11 split pairs the test is weak; fewer than 10 split pairs, or no pre-cut coordination to lose (split pairs' pre mean ≤ 0.01 bits), → descriptive.

## Scorecard (period-specific axes)
- **E** (interventional): the prediction did not hold or was not testable.
- **G**: rooms and the A-B-A dates are known; the file-level and room assignments come from logged fields.
- **F**: 5-day units have low synthetic power (A2).

## Notes
- 2026-10-04: prediction written by `period_folders.py --predict` before the run; results filled by `--results`.
