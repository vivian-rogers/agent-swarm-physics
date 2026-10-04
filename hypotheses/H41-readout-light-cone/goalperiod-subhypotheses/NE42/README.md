# H41 × NE42: #best/#rest merge and split, A-B-A on graph distance (#39 → #40 → #41)

**Verdict:** supported
**Verdict (1b):** supported (unchanged; the partition reads the full rooms timeline; 82× and 863× identical)
**Role:** native (exploratory)
**Boundaries:** 2026-05-04 merge (#39 → #40), 2026-05-11 split (#40 → #41). Periods #39, #40, #41 (all non-holdout, regime III).

## Why this natural experiment
**Native test across a natural experiment (exception (c): the transition is the object).** On 2026-05-04 #best and #rest were merged into #universe-coordination (GPT-5 stayed alone in #rest) and on 05-11 split back to the same partition. Hop distance between the two former groups drops from ≥ 2 (or ∞) on the read-out graph to 1 and back. Groups = room in #39 (just before the merge) and, for #41, room just after the split. Goal confound: #40 (connect worlds) had a shared cross-world objective.

## Prediction
*Written 2026-10-04 ~06:00 UTC (card, "Native tests"), before any real-data run.*
- **NE42-a:** the cross-group adoption hazard per at-risk talk call (2 h horizon) in #40 is ≥ 3× its value in both #39 and #41.
- **NE42-b:** cross-group acausal share ≥ 70% in #39 and #41; in #40 within 0.05 of the within-group acausal share.
- **NE42-c:** within-group cycles per hop change by < 30% across the three periods (the merge changes distance, not cadence).
- **Verdict:** supported if a and b hold; failed if a fails; mixed otherwise. Prior 0.55.

## Result
Run 2026-10-04 (`analysis/native.py`). **Verdict: supported** (checks {'a': True, 'b': True, 'c': False}).

| Period | cross-group hazard per talk call (2 h) | within-group hazard | ratio | cross-group acausal share | within-group acausal | within-group cycles per hop |
| --- | --- | --- | --- | --- | --- | --- |
| G39 | 0.0000 (n 28818) | 0.0011 (n 164288) | 0.030 [0.010, 0.105] | 1.00 (n 8) | 0.01 | 62 |
| G40 | 0.0029 (n 243112) | 0.0020 (n 418885) | 1.406 [1.234, 1.658] | 0.02 (n 823) | 0.03 | 20 |
| G41 | 0.0000 (n 301726) | 0.0029 (n 593877) | 0.001 [0.000, 0.004] | 1.00 (n 13) | 0.02 | 11 |

- **NE42-a:** cross-group hazard #40 / #39 = 82.38 [20.56, 222.69]; #40 / #41 = 862.56 [186.06, 2365.31] (prediction ≥ 3 for both): pass.
- **NE42-b:** pass. **NE42-c:** fail.

## Scorecard (period-specific axes)
- E (interventional): the merge/split A-B-A on hop distance.

## Notes
- Data: `data/processed/H41-readout-light-cone/G39/`, `G40/`, `G41/`; results in `results/native.json`.
