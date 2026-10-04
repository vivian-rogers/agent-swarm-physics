# H86 × NE43: operator bookends stop (2026-08-05), nudges stop (2026-08-21), inside G51

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** regime III; units 51f (07-29 → 08-04), 51g (08-05 → 08-21, two rooms: #general and #focus), 51h–51i (08-24 → 08-31); 26–28 agents.

## Why this period
Two operator drives switch off one after the other while the runner keeps its schedule: a test of what the gauge attributes to the operator.

## Prediction
*Written 2026-10-04 20:05 UTC in the card.* (i) Bookends stop: c_×,raw changes by less than its 95% CI (the runner, not the bookends, drives the day edges). (ii) Nudges stop: c_×,trim does not change (CI includes 0) while c_T,trim rises (idle agents stay idle longer: private variance). *Against:* a c_×,raw drop beyond its CI at 08-05; a c_×,trim change beyond its CI at 08-21.

## Result
*Run 2026-10-04 20:18 UTC (`analysis/natives.py`; daily statistics, day bootstrap of side means).*

| Contrast | before | after | difference [95% CI] | days |
| --- | --- | --- | --- | --- |
| c_× raw, bookends stop (51f → 51g) | 0.0088 | 0.0097 | 0.0009 [-0.0034, 0.0056] | 5 / 13 |
| c_× trimmed, bookends stop | 0.0051 | 0.0082 | 0.0032 [-0.0020, 0.0087] | 5 / 13 |
| c_× trimmed, nudges stop (51g → 51h, 51i) | 0.0082 | 0.0037 | -0.0046 [-0.0111, 0.0026] | 13 / 5 |
| c_T trimmed, nudges stop | -0.0435 | -0.0351 | 0.0084 [-0.0335, 0.0465] | 13 / 5 |
| φ trimmed, nudges stop | 0.0451 | 0.0273 | -0.0178 [-0.0623, 0.0284] | 13 / 5 |

- (i) passes: the raw shared field does not move when the bookends stop (+0.001 [−0.003, +0.006]).
- (ii) the shared part passes (c_×,trim −0.005 [−0.011, +0.003]); the private part fails: c_T,trim does not rise (+0.008 [−0.034, +0.047]).
- **Verdict: mixed.** The gauge assigns nothing to the operator's bookends or nudges; the predicted private-variance signature of the nudge stop is absent. 51g also adds the #focus room (a confound for (ii)).

## Scorecard (period-specific axes)
- E (interventional): two operator interventions leave the shared-field gauge unchanged, as the scheduler reading predicts.
