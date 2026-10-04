# H92 × G51: private roles, the long era (2026-07-06 → 2026-09-04, non-holdout part)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** regime III · mode I/K (private roles) · 21 → 32 agents · #general, plus #focus in 51g (08-05 → 08-21) · units 51a–51l; the longest are 51c, 51d (5 days) and 51g (13 days). The #51 tail is held out.

## Why this period
The only units long enough for an expanding training window to grow from 1 to 12 days at N ≈ 25–27. Random-matrix noise in a raw pair correlation falls as 1/T, so the gain from cleaning should shrink as the training window grows. 51g also has two rooms (#general, #focus), a second mode that a uniform-mode shrinkage cannot represent.

## Prediction
*Written 2026-10-04 ~20:12 UTC, before running on this period. Credences in brackets.*
- **N1a (RMT scaling).** Over the target days of 51c, 51d and 51g, Spearman(r_raw, number of training days) < 0 in content (both models) [0.6].
- **N1b (beyond a uniform mode).** E5 (RMT-clip, calibrated edge) has a lower mean MSE than E4 (Ledoit–Wolf constant correlation) in ≥ 2/3 of the #51 units with ≥ 2 target days, content [0.35]; in 51g's talk channel [0.5].
- **N1c (rooms in 51g).** The realized talk room contrast (mean within-room minus between-room pair correlation) is > 0 on ≥ 2/3 of 51g's target days [0.6], and E5's contrast error is ≤ E2's on ≥ 2/3 of them [0.5].
- **Counts against:** N1a ≥ 0 (cleaning gains do not fall with training length) and N1b fails.
- **Verdict rule:** *supported* if N1a and N1b (content) hold; *failed* if both fail; *mixed* otherwise.

## Result
*Run 2026-10-04 ~20:38 UTC.* Gain r = 1 − MSE(clip)/MSE(rival), expanding training window.

| Prediction | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| N1a gain over raw falls with training days (51c, 51d, 51g) | Spearman −0.69 (bge), −0.90 (gte), n 20; gte gain 0.26 at 1 day → 0.02 at 12 days | < 0 | pass |
| N1b clip beats LW constant correlation in ≥ 2/3 of #51 units (content) | 4/7 (bge), 5/7 (gte); MSE differences ≤ 3% in every unit | ≥ 2/3 both models | fail |
| N1b talk in 51g | clip MSE above LW-CC; talk: clip beats LW-CC in 0/6 #51 units | – | fail |
| N1c 51g talk room contrast > 0 on ≥ 2/3 days; clip error ≤ raw on ≥ 2/3 | 7/12 (0.58) and 7/12 (0.58); realized 0.008, raw 0.006, clip 0.005 | – | fail (the #focus room block is weak in talk) |

The gain from cleaning falls toward zero as the training window grows, as the 1/T noise law predicts. At 12 days of N ≈ 25 the raw matrix is almost as good as the cleaned one.

**Replication numbers (common estimator):** 33 target days, median N 24; gain over raw 0.20 (bge) / 0.19 (gte); over LW-CC +0.01 / +0.02; clip is the best estimator in both models.

Data: `data/processed/H92-rmt-cleaned-forecast/native/results.json`, `periods.parquet`.

## Scorecard (period-specific axes)
- D (unfitted predictions): 2. The scaling of the gain with training length is the random-matrix signature, not fitted.
- H (comparative): 1. Clip and constant-correlation shrinkage tie within 3%.
