# H128 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 05-08)

**Verdict:** failed
**Role:** exploratory (replication)
**Period:** regime III · mode C · 15 agents · #universe-coordination (NE42 merge) · 5 days. Kickoff code: named (assigned artifact).

## Why this period
Named shared target (connect the worlds) right after the NE42 room merge.

## Prediction
*Written 2026-10-04 22:19 UTC, before running H128 on this period.*
- Kickoff code: named. Expected: N_p reaches its final level within 3 active h (t_f ≤ 3 h), shape constant or step, no power-law selection (card P2).
- Shared target: N_p falls to N∞ (few repos) within the first round of commits.
- Counts against: power law selected with t_f > 3 h.
- Verdict rule: supported if constant/step with t_f ≤ 3 h; failed if power law selected and t_f > 3 h; mixed otherwise; descriptive if untestable (N_pk < 4, < 6 hosts, or H < 10 h).

## Result
*Run 2026-10-04 22:44 UTC (`scheme/build.py`, `analysis/run.py`; non-holdout days; first 20.0 active h).* Primary observable dw = (N_p − 1)/(N_h − 1) (Amendment A1); N_p is the HH-literal secondary.

| Unit | Code | dw class / shape | t_f (active h) | A_u (h) | α̂ on dw [95% boot] | N_p (HH-literal) class / shape; merge share; deaths | dw drift per h (post hoc A2) | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G40 | named | slow / power | 15.75 (jk SE 6.0) | 3.36 | 0.20 [0.11, 0.30] | slow / power, c_m 0.60 {'merge': 6, 'hop_new': 0, 'finish': 4} | -0.013 (τ -0.41, p 0.000) | failed |

Synthetic validity on this skeleton (A1 rule): not valid (Q0 not frozen True, fields freeze False, finish not coarsening True; α identified True).

Data: `data/processed/H128-coarsening-vs-freeze/G40/` (curve, deaths); figure: `../../figures/summary_obs.pdf`.

## Scorecard (period-specific axes)
- **C:** freeze baseline (t_f ≤ 3 h) and shape fits (constant/step/exponential/power, BIC).
- **D:** death kinds (merge vs finish) are unfitted; read share of merges 0.00.
- **F:** real-skeleton synthetic (5 worlds × 60 runs): not valid for dw.

## Notes
- 2026-10-04 22:19 UTC: folder and prediction written before any H128 statistic on this period.
- 2026-10-04 22:44 UTC: result filled (verdict failed).
