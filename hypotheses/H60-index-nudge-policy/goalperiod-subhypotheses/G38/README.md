# H60 × G38: index nudge policy (2026-04-02 → 2026-04-24)

**Verdict:** failed
**Role:** replication
**Period:** regime III · 11 agents · 17 days with the nudger on. Cross-fit halves: interleaved days.

## Why this period
Replication layer: the common policy evaluation on every period with ≥ 500 idle gates and ≥ 50 gates that read a nudge to the agent. Only G51 and G38 qualify.

## Prediction
*Written 2026-10-04, before running (card P1–P8; A1 before real data).*
Supported if V(index)/V(logged) ≥ 2.3 with CI lower bound > 1 and V(index)/V(once-early) > 1 with CI lower bound > 1 on active calls. Expected (P8): the index/logged CI includes 1 (long pauses) [0.6].

## Result
`analysis/run_period.py`; numbers in `data/processed/H60-index-nudge-policy/G38/results.json`. Values are cross-fitted direct-method means of the predicted nudge effect over the gates each policy picks, at the logged budget; CIs from day-block bootstrap draws (200 for active calls, 100 for binary outcomes).

**active calls in 30 min (primary)** — 1417 gates, 49 nudged, mean outcome 55.62; heterogeneity (θ_a = θ_k = θ_r = 0) p = 0.434; mean effect at nudged gates 10.74; verdict rule: failed.

| Policy | value per nudge [95% CI] | ratio to logged [95% CI] |
| --- | --- | --- |
| logged | 12.206 [4.50, 17.82] | 1 |
| random | 14.735 [6.12, 26.88] | 1.21 [0.51, 3.32] |
| once_early | 13.602 [3.66, 25.45] | 1.11 [0.37, 3.38] |
| index_ak | 4.455 [-19.75, 57.17] | 0.37 |
| index | 6.738 [-19.19, 54.79] | 0.55 [-1.94, 7.46] |
| index_once | 7.457 [-19.29, 46.41] | 0.61 [-2.02, 4.52] |

index / once-early 0.50 [-1.76, 4.06]; index / index(a,k) 1.51 [-3.50, 21.38].

**sustained escape (prob.)** — 1616 gates, 58 nudged, mean outcome 0.53; heterogeneity (θ_a = θ_k = θ_r = 0) p = 0.989; mean effect at nudged gates 0.38; verdict rule: failed.

| Policy | value per nudge [95% CI] | ratio to logged [95% CI] |
| --- | --- | --- |
| logged | 0.385 [0.28, 0.52] | 1 |
| random | 0.404 [0.24, 0.51] | 1.05 [0.50, 1.46] |
| once_early | 0.486 [0.29, 0.57] | 1.26 [0.60, 1.76] |
| index_ak | 0.657 [0.27, 0.83] | 1.70 |
| index | 0.702 [0.26, 0.83] | 1.82 [0.59, 2.20] |
| index_once | 0.368 [0.22, 0.53] | 0.96 [0.58, 1.65] |

index / once-early 1.45 [0.70, 1.94]; index / index(a,k) 1.07 [0.87, 1.12].

**glance (prob.)** — 1628 gates, 58 nudged, mean outcome 0.86; heterogeneity (θ_a = θ_k = θ_r = 0) p = 0.0162; mean effect at nudged gates 0.10; verdict rule: failed.

| Policy | value per nudge [95% CI] | ratio to logged [95% CI] |
| --- | --- | --- |
| logged | 0.116 [0.05, 0.25] | 1 |
| random | 0.141 [0.09, 0.19] | 1.22 [0.50, 2.16] |
| once_early | 0.129 [0.08, 0.18] | 1.12 [0.38, 2.03] |
| index_ak | 0.444 [0.06, 0.56] | 3.84 |
| index | 0.444 [0.05, 0.57] | 3.84 [0.32, 5.48] |
| index_once | 0.055 [0.02, 0.28] | 0.48 [0.16, 3.52] |

index / once-early 3.43 [0.44, 4.31]; index / index(a,k) 1.00 [0.90, 1.14].

Verdict (primary outcome): **failed**.

## Scorecard (period-specific axes)
- C: policy values are cross-fitted on held-out day halves.
- H: rivals R0 (flat), R1 (logged near-optimal), R2 (once-early optimal) are scored by the ratios above; R3 (selection) is not excluded by this estimator (synthetic S3).

