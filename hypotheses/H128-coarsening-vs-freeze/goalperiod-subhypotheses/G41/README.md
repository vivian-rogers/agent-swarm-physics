# H128 × G41: Perform novel research! (2026-05-11 → 05-15)

**Verdict:** mixed
**Role:** exploratory (replication)
**Period:** regime III · mode I · 15 agents · #best/#rest · 5 days. Kickoff code: free (open or objective only).

## Why this period
Free week (novel research), same roster as #39/#40: H75's slow settler (S 5.1; seen).

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
| G41 | free | slow / step | > 20.0 (censored) | 0.00 | -0.27 [-0.48, -0.04] | slow / power, c_m 0.38 {'merge': 12, 'hop_new': 4, 'finish': 16} | 0.021 (τ 0.42, p 0.000) | mixed |

Synthetic validity on this skeleton (A1 rule): valid (Q0 not frozen True, fields freeze True, finish not coarsening True; α identified True).

Data: `data/processed/H128-coarsening-vs-freeze/G41/` (curve, deaths); figure: `../../figures/summary_obs.pdf`.

## Scorecard (period-specific axes)
- **C:** freeze baseline (t_f ≤ 3 h) and shape fits (constant/step/exponential/power, BIC).
- **D:** death kinds (merge vs finish) are unfitted; read share of merges 0.42.
- **F:** real-skeleton synthetic (5 worlds × 60 runs): valid for dw.

## Notes
- 2026-10-04 22:19 UTC: folder and prediction written before any H128 statistic on this period.
- 2026-10-04 22:44 UTC: result filled (verdict mixed).
