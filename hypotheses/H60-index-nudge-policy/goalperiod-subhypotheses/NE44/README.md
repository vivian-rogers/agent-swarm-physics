# H60 × NE44: the index's shape across the pause-default change (regime III, 2026-03-30 → 05-29 vs #51)

**Verdict:** failed
**Role:** native
**Period:** pre = G37–G44 pooled (2583 gates, 86 nudged; agent-within-period fixed effects); post = G51 (nudger-on days). Exception (c): the transition is the object.

## Why this period
Before 06-11 a pause without a duration slept 12 h; after it, 5 min. H35 found the nudge effect rising with trap age before (G38 +1.18) and falling after (G51 −0.32). If so, the index must be refitted after a scaffold change.

## Prediction
*Written 2026-10-04, before running (card N2).*
θ_k (nudge × ln k, active calls) ≥ 0 before and < 0 after [0.45].

## Result
`analysis/native.py`; `data/processed/H60-index-nudge-policy/native/native.json` (B = 200).

| Term | pre-06-11 [95% CI] | G51 [95% CI] |
| --- | --- | --- |
| M | 11.82 [6.00, 19.10] | 7.20 [5.04, 9.78] |
| M_la | -1.30 [-8.72, 6.41] | -1.84 [-5.30, 1.60] |
| M_lk | -2.96 [-10.74, 5.60] | -1.71 [-6.22, 3.10] |
| M_lr | 0.15 [-6.78, 5.23] | 0.90 [-1.16, 3.58] |

Prediction fails: the k slope is negative on both sides and neither CI excludes 0.

