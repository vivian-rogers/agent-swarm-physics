# H128 × G44: Finetune your leader! (2026-05-26 → 05-29)

**Verdict:** failed
**Role:** exploratory (native N1; replication rows are not written for the pooled period)
**Period:** regime III · mode C · 17–18 agents · #best (named leader) / #rest (free) · 4 days. Kickoff code: both: #best named (fine-tune a named leader), #rest free.

## Why this period
Two room kickoffs on the same days with different fields: #best is told to fine-tune a named leader, #rest chooses its own goal. Same skeleton, same scaffold: the cleanest named-vs-free pair (H75: #best S 2.5, #rest S 14.5; seen).

## Prediction
*Written 2026-10-04 22:19 UTC, before running H128 on this period.*
- #rest (free): slow settling, t_f > 3 active h, larger A_u than #best; HH: power law with α ≈ 0.3–0.5.
- #best (named): constant or step with t_f ≤ 3 active h.
- Native N1 (credence 0.6): t_f(#rest) > 3 h ≥ t_f(#best) and A_u(#rest) > A_u(#best).
- Verdict rule: supported if both rooms behave as predicted; failed if #rest freezes (t_f ≤ 3 h) or #best does not; mixed otherwise; descriptive if a room is untestable (N_pk < 4 or < 6 hosts).

## Result
*Run 2026-10-04 22:44 UTC (`scheme/build.py`, `analysis/run.py`; non-holdout days; first 16.0 active h).* Primary observable dw = (N_p − 1)/(N_h − 1) (Amendment A1); N_p is the HH-literal secondary.

| Unit | Code | dw class / shape | t_f (active h) | A_u (h) | α̂ on dw [95% boot] | N_p (HH-literal) class / shape; merge share; deaths | dw drift per h (post hoc A2) | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G44best | named | slow / step | > 16.0 (censored) | 8.25 | 0.16 [-0.01, 0.27] | freeze / step, c_m 0.45 {'merge': 5, 'hop_new': 5, 'finish': 1} | -0.040 (τ -0.55, p 0.000) | descriptive |
| G44rest | free | slow / constant | 12.75 (jk SE 0.4) | 0.00 | 0.02 [-0.04, 0.07] | slow / step, c_m 0.14 {'merge': 7, 'hop_new': 23, 'finish': 20} | -0.002 (τ -0.05, p 0.576) | mixed |

Synthetic validity on this skeleton (A1 rule): not valid (Q0 not frozen False, fields freeze False, finish not coarsening True; α identified True).
Native N1: predicted #rest slow with larger A_u than a frozen #best. Observed: #best (named, 4 hosts, below the testability floor) declines slowly (t_f > H, A_u 8.25, drift −0.040/h); #rest (free) stays scattered at dw ≈ 0.92 (A_u 0, drift −0.002/h). N1 fails: the free room never coarsens and the named room is the one that drifts. Caveat (A1): the #best skeleton is untestable and #rest fails synthetic rule (a).
Data: `data/processed/H128-coarsening-vs-freeze/G44best/` (curve, deaths); figure: `../../figures/summary_obs.pdf`.

## Scorecard (period-specific axes)
- **C:** freeze baseline (t_f ≤ 3 h) and shape fits (constant/step/exponential/power, BIC).
- **D:** death kinds (merge vs finish) are unfitted; read share of merges 0.60.
- **F:** real-skeleton synthetic (5 worlds × 60 runs): not valid for dw.

## Notes
- 2026-10-04 22:19 UTC: folder and prediction written before any H128 statistic on this period.
- 2026-10-04 22:44 UTC: result filled (verdict failed).
