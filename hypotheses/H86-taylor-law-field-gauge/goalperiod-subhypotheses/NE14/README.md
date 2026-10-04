# H86 × NE14: regime II → III, the always-on computer-use runner (2026-03-24), G35–G37

**Verdict:** failed
**Role:** native (exploratory)
**Period:** units 35, 36a (regime II) and 36b, 36c, 37 (regime III); 12 agents throughout.

## Why this period
H38 found that the regime-III runner's daily start and stop carries 70–80% of co-activation; the switch should add scheduler covariance on raw grids and none on trimmed grids.

## Prediction
*Written 2026-10-04 20:05 UTC in the card.* c_×,raw (activity) rises across the boundary (III − II, day-bootstrap CI > 0); the trimmed change is less than half of the raw change. Placebos 35 → 36a and 36c → 37 move c_×,raw by less than the NE14 change. *Against:* the trimmed change ≥ the raw change.

## Result
*Run 2026-10-04 20:18 UTC (`analysis/natives.py`; daily c_× on 15-min activity bins; day bootstrap of side means, 4,000 draws).*

| Contrast | before | after | difference [95% CI] | days |
| --- | --- | --- | --- | --- |
| c_× raw: II (35, 36a) → III (36b, 36c, 37) | 0.0059 | 0.3148 | 0.3089 [-0.0068, 0.9299] | 6 / 7 |
| c_× raw placebo 35 → 36a | 0.0069 | 0.0009 | -0.0060 [-0.0084, -0.0029] | 5 / 1 |
| c_× raw placebo 36b/c → 37 | 0.0100 | 0.7213 | 0.7114 [-0.0219, 2.1558] | 4 / 3 |
| c_× trimmed: II → III | 0.0056 | 0.0070 | 0.0013 [-0.0072, 0.0114] | 6 / 7 |
| c_× trimmed placebo 36b/c → 37 | 0.0092 | 0.0039 | -0.0053 [-0.0222, 0.0096] | 4 / 3 |
| φ trimmed: II → III | 0.1464 | 0.0744 | -0.0720 [-0.1819, 0.0474] | 6 / 7 |

- The raw rise (+0.31) is one day: 2026-03-31 (G37), whose window holds a 513-min all-silent gap (`infra/README.md` known issue), gives c_×,raw = 2.17; every other regime-III day is ≤ 0.03, like regime II. The CI includes 0, and the III → III placebo is larger.
- The trimmed grid is flat across the boundary (+0.001 [−0.007, +0.011]), as predicted.
- **Verdict: failed** for the raw clause (no boundary-specific scheduler jump in count covariance). The "against" condition is not met: trimming removes what raw grids add. Raw c_× is a detector of village-off gaps inside windows.

## Scorecard (period-specific axes)
- E (interventional): the regime switch does not change the shared-field gauge on trimmed grids; the raw gauge reacts to off-gaps, not to the runner.
