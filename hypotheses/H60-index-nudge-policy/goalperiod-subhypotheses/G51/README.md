# H60 × G51: index nudge policy (2026-07-06 → 2026-08-20)

**Verdict:** failed
**Role:** replication
**Period:** regime III · 27 agents · 34 days with the nudger on (07-06 → 08-20; NE43 after). Cross-fit halves: interleaved days.

## Why this period
Replication layer: the common policy evaluation on every period with ≥ 500 idle gates and ≥ 50 gates that read a nudge to the agent. Only G51 and G38 qualify.

## Prediction
*Written 2026-10-04, before running (card P1–P8; A1 before real data).*
Supported if V(index)/V(logged) ≥ 2.3 with CI lower bound > 1 and V(index)/V(once-early) > 1 with CI lower bound > 1 on active calls. Expected (P1/P2): not met [credences 0.3, 0.35].

## Result
`analysis/run_period.py`; numbers in `data/processed/H60-index-nudge-policy/G51/results.json`. Values are cross-fitted direct-method means of the predicted nudge effect over the gates each policy picks, at the logged budget; CIs from day-block bootstrap draws (200 for active calls, 100 for binary outcomes).

**active calls in 30 min (primary)** — 16506 gates, 404 nudged, mean outcome 37.05; heterogeneity (θ_a = θ_k = θ_r = 0) p = 0.000368; mean effect at nudged gates 7.20; verdict rule: failed.

| Policy | value per nudge [95% CI] | ratio to logged [95% CI] |
| --- | --- | --- |
| logged | 7.094 [4.85, 10.55] | 1 |
| random | 10.389 [6.68, 15.60] | 1.46 [1.22, 1.67] |
| once_early | 11.029 [7.20, 16.14] | 1.55 [1.25, 1.81] |
| index_ak | 7.819 [-1.41, 24.11] | 1.10 |
| index | 7.664 [-2.19, 24.96] | 1.08 [-0.30, 3.44] |
| index_once | 10.573 [2.91, 25.31] | 1.49 [0.46, 3.42] |

index / once-early 0.69 [-0.22, 2.12]; index / index(a,k) 0.98 [0.51, 3.24].

**sustained escape (prob.)** — 17310 gates, 428 nudged, mean outcome 0.48; heterogeneity (θ_a = θ_k = θ_r = 0) p = 0.00199; mean effect at nudged gates 0.24; verdict rule: mixed.

| Policy | value per nudge [95% CI] | ratio to logged [95% CI] |
| --- | --- | --- |
| logged | 0.241 [0.20, 0.31] | 1 |
| random | 0.242 [0.20, 0.29] | 1.00 [0.86, 1.15] |
| once_early | 0.322 [0.27, 0.38] | 1.34 [1.10, 1.58] |
| index_ak | 0.586 [0.38, 0.67] | 2.43 |
| index | 0.569 [0.27, 0.68] | 2.36 [1.07, 2.99] |
| index_once | 0.314 [0.16, 0.39] | 1.30 [0.67, 1.63] |

index / once-early 1.77 [0.84, 2.11]; index / index(a,k) 0.97 [0.66, 1.13].

**glance (prob.)** — 17361 gates, 429 nudged, mean outcome 0.75; heterogeneity (θ_a = θ_k = θ_r = 0) p = 0.0328; mean effect at nudged gates 0.23; verdict rule: mixed.

| Policy | value per nudge [95% CI] | ratio to logged [95% CI] |
| --- | --- | --- |
| logged | 0.233 [0.17, 0.29] | 1 |
| random | 0.131 [0.08, 0.15] | 0.57 [0.45, 0.65] |
| once_early | 0.094 [0.06, 0.12] | 0.40 [0.28, 0.51] |
| index_ak | 0.524 [0.23, 0.59] | 2.25 |
| index | 0.527 [0.24, 0.57] | 2.26 [1.23, 2.49] |
| index_once | 0.157 [0.01, 0.22] | 0.68 [0.05, 0.98] |

index / once-early 5.60 [2.87, 7.94]; index / index(a,k) 1.00 [0.83, 1.20].

Verdict (primary outcome): **failed**.

## Scorecard (period-specific axes)
- C: policy values are cross-fitted on held-out day halves.
- H: rivals R0 (flat), R1 (logged near-optimal), R2 (once-early optimal) are scored by the ratios above; R3 (selection) is not excluded by this estimator (synthetic S3).

