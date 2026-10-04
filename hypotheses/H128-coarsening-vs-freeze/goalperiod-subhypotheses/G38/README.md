# H128 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 04-24)

**Verdict:** mixed
**Role:** exploratory (replication)
**Period:** regime III · mode C · 12–14 agents · #best/#rest · 17 days. Kickoff code: free (open or objective only).

## Why this period
Free charity week (choose a charity), 17 days; the first 20 active hours are the replication window.

## Prediction
*Written 2026-10-04 22:19 UTC, before running H128 on this period.*
- Kickoff code: free. HH369 (card P1): N_p falls as a power law after its peak, α̂'s CI overlaps [0.3, 0.5], t_f > 3 active h; merges are ≥ half of project deaths (P4).
- My expectation: slow settling (t_f > 3 h) is likelier than a clean power law; deaths by finish (expiry) may dominate.
- Counts against: a freeze (t_f ≤ 3 h, constant or step).
- Verdict rule: supported if power law selected, α̂ CI overlaps [0.3, 0.5] (where identified) and t_f > 3 h; mixed if slow (t_f > 3 h) but not a power law in the band; failed if frozen (t_f ≤ 3 h); descriptive if untestable (N_pk < 4, < 6 hosts, or H < 10 h).

## Result
*Run 2026-10-04 22:44 UTC (`scheme/build.py`, `analysis/run.py`; non-holdout days; first 20.0 active h).* Primary observable dw = (N_p − 1)/(N_h − 1) (Amendment A1); N_p is the HH-literal secondary.

| Unit | Code | dw class / shape | t_f (active h) | A_u (h) | α̂ on dw [95% boot] | N_p (HH-literal) class / shape; merge share; deaths | dw drift per h (post hoc A2) | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G38 | free | slow / step | 14.75 (jk SE 10.0) | 3.68 | 0.05 [-0.17, 0.22] | slow / power, c_m 0.10 {'merge': 4, 'hop_new': 8, 'finish': 30} | -0.015 (τ -0.17, p 0.033) | mixed |

Synthetic validity on this skeleton (A1 rule): valid (Q0 not frozen True, fields freeze True, finish not coarsening True; α identified False).

Data: `data/processed/H128-coarsening-vs-freeze/G38/` (curve, deaths); figure: `../../figures/summary_obs.pdf`.

## Scorecard (period-specific axes)
- **C:** freeze baseline (t_f ≤ 3 h) and shape fits (constant/step/exponential/power, BIC).
- **D:** death kinds (merge vs finish) are unfitted; read share of merges 0.75.
- **F:** real-skeleton synthetic (5 worlds × 60 runs): valid for dw.

## Notes
- 2026-10-04 22:19 UTC: folder and prediction written before any H128 statistic on this period.
- 2026-10-04 22:44 UTC: result filled (verdict mixed).
