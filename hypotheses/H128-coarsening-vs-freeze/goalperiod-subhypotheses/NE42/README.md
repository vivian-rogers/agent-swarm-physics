# H128 × NE42: rooms merge with a named shared target (05-04), then split with a free goal (05-11)

**Verdict:** failed
**Role:** exploratory (native N2)
**Period:** regime III · #39 → #40 → #41 · 15 agents (same roster) · rooms #best/#rest → #universe-coordination → #best/#rest · 3 × 5 days. Event study across two boundaries (exception (c): the transition is the object).

## Why this period
NE42 is an A-B-A on a fixed roster. The 05-04 boundary combines a room merge with a named shared target ("connect your worlds"); the 05-11 boundary combines a split with a free goal ("novel research"). With labels carried across each boundary, the project count starts from the previous week's frozen state, so the test is how fast the count reaches its new level after a named vs a free quench. The merge and the goal change are confounded (catalog note); the named/free contrast is the object here.

## Prediction
*Written 2026-10-04 22:19 UTC, before running H128 on this window.*
- Initial condition: host labels carried from the previous week's last day (variant 6 of the scheme).
- 05-04 (merge + named shared target): N_p reaches its new final level within 3 active h (t_f ≤ 3 h).
- 05-11 (split + free): t_f > 3 active h.
- Native N2 (credence 0.45): both hold.
- Verdict rule: supported if both hold; failed if the free boundary freezes (t_f ≤ 3 h) or the named one does not; mixed otherwise.

## Result
*Run 2026-10-04 22:44 UTC (`scheme/build.py`, `analysis/run.py`; non-holdout days; first 20.0 active h).* Primary observable dw = (N_p − 1)/(N_h − 1) (Amendment A1); N_p is the HH-literal secondary.

| Unit | Code | dw class / shape | t_f (active h) | A_u (h) | α̂ on dw [95% boot] | N_p (HH-literal) class / shape; merge share; deaths | dw drift per h (post hoc A2) | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NE42_merge | named | slow / power | 15.75 | 1.90 | 0.26 [0.19, 0.35] | slow / power, c_m 0.72 {'merge': 13, 'hop_new': 1, 'finish': 4} | -0.014 (τ -0.46, p 0.000) | failed |
| NE42_split | free | slow / step | > 20.0 (censored) | 0.00 | -0.27 [-0.48, -0.07] | slow / power, c_m 0.38 {'merge': 12, 'hop_new': 4, 'finish': 16} | 0.021 (τ 0.42, p 0.000) | mixed |

Synthetic validity on this skeleton (A1 rule): not valid (Q0 not frozen True, fields freeze False, finish not coarsening True; α identified True).
Labels carried across the boundaries. Pre-boundary dw (last 4 h of #39) 1.00; of #40 0.20. The named merge boundary (05-04) does not freeze: dw falls slowly from 1 to ≈ 0.2 over 16 active h with a power-law shape (α̂ 0.26), the only coarsening-like curve in the dataset; merges carry 0.72 of project deaths. The free split boundary (05-11) fragments: dw rises from 0.3 to 0.6 (drift +0.021/h). N2 fails as written (both slow), and the direction is the reverse of HH369: a shared target coarsens, a free goal fragments.
Data: `data/processed/H128-coarsening-vs-freeze/NE42_merge/` (curve, deaths); figure: `../../figures/summary_obs.pdf`.

## Scorecard (period-specific axes)
- **C:** freeze baseline (t_f ≤ 3 h) and shape fits (constant/step/exponential/power, BIC).
- **D:** death kinds (merge vs finish) are unfitted; read share of merges –.
- **F:** real-skeleton synthetic (5 worlds × 60 runs): not valid for dw.

## Notes
- 2026-10-04 22:19 UTC: folder and prediction written before any H128 statistic on this window.
- 2026-10-04 22:44 UTC: result filled (verdict failed).
