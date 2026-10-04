# H128 × G33: Discuss, debate, and act on your views about the Pentagon-AI news (2026-03-02 → 03-04)

**Verdict:** failed
**Role:** exploratory (replication)
**Period:** regime II · mode C · 11 agents · #general · 3 days. Kickoff code: free (open or objective only).

## Why this period
Short free week (3 days, 12 active h).

## Prediction
*Written 2026-10-04 22:19 UTC, before running H128 on this period.*
- Kickoff code: free. HH369 (card P1): N_p falls as a power law after its peak, α̂'s CI overlaps [0.3, 0.5], t_f > 3 active h; merges are ≥ half of project deaths (P4).
- My expectation: slow settling (t_f > 3 h) is likelier than a clean power law; deaths by finish (expiry) may dominate.
- Counts against: a freeze (t_f ≤ 3 h, constant or step).
- Verdict rule: supported if power law selected, α̂ CI overlaps [0.3, 0.5] (where identified) and t_f > 3 h; mixed if slow (t_f > 3 h) but not a power law in the band; failed if frozen (t_f ≤ 3 h); descriptive if untestable (N_pk < 4, < 6 hosts, or H < 10 h).

## Result
*Run 2026-10-04 22:44 UTC (`scheme/build.py`, `analysis/run.py`; non-holdout days; first 11.8 active h).* Primary observable dw = (N_p − 1)/(N_h − 1) (Amendment A1); N_p is the HH-literal secondary.

| Unit | Code | dw class / shape | t_f (active h) | A_u (h) | α̂ on dw [95% boot] | N_p (HH-literal) class / shape; merge share; deaths | dw drift per h (post hoc A2) | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G33 | free | freeze / step | 0.50 (jk SE 12.0) | -31.40 | -1.17 [-1.23, -0.58] | freeze / step, c_m 0.22 {'merge': 2, 'hop_new': 2, 'finish': 5} | 0.014 (τ 0.45, p 0.000) | failed |

Synthetic validity on this skeleton (A1 rule): valid (Q0 not frozen True, fields freeze True, finish not coarsening True; α identified True).

Data: `data/processed/H128-coarsening-vs-freeze/G33/` (curve, deaths); figure: `../../figures/summary_obs.pdf`.

## Scorecard (period-specific axes)
- **C:** freeze baseline (t_f ≤ 3 h) and shape fits (constant/step/exponential/power, BIC).
- **D:** death kinds (merge vs finish) are unfitted; read share of merges 1.00.
- **F:** real-skeleton synthetic (5 worlds × 60 runs): valid for dw.

## Notes
- 2026-10-04 22:19 UTC: folder and prediction written before any H128 statistic on this period.
- 2026-10-04 22:44 UTC: result filled (verdict failed).
