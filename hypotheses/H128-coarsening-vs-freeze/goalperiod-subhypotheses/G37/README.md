# H128 × G37: Pick your own goal! (2026-03-30 → 04-01)

**Verdict:** mixed
**Role:** exploratory (replication, native N3)
**Period:** regime III · mode F · 12 agents · #best/#rest (identical kickoff) · 3 days. Kickoff code: free (open or objective only).

## Why this period
Free week with two rooms that got identical kickoff text: also native N3 (two replicas of one free quench).

## Prediction
*Written 2026-10-04 22:19 UTC, before running H128 on this period.*
- Kickoff code: free. HH369 (card P1): N_p falls as a power law after its peak, α̂'s CI overlaps [0.3, 0.5], t_f > 3 active h; merges are ≥ half of project deaths (P4).
- My expectation: slow settling (t_f > 3 h) is likelier than a clean power law; deaths by finish (expiry) may dominate.
- Counts against: a freeze (t_f ≤ 3 h, constant or step).
- Verdict rule: supported if power law selected, α̂ CI overlaps [0.3, 0.5] (where identified) and t_f > 3 h; mixed if slow (t_f > 3 h) but not a power law in the band; failed if frozen (t_f ≤ 3 h); descriptive if untestable (N_pk < 4, < 6 hosts, or H < 10 h).
- Native N3 (credence 0.5): the two rooms get the same class (both slow or both frozen) and |t_f(#best) − t_f(#rest)| ≤ 3 h.

## Result
*Run 2026-10-04 22:44 UTC (`scheme/build.py`, `analysis/run.py`; non-holdout days; first 20.0 active h).* Primary observable dw = (N_p − 1)/(N_h − 1) (Amendment A1); N_p is the HH-literal secondary.

| Unit | Code | dw class / shape | t_f (active h) | A_u (h) | α̂ on dw [95% boot] | N_p (HH-literal) class / shape; merge share; deaths | dw drift per h (post hoc A2) | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G37 | free | slow / step | > 20.0 (censored) | -6.19 | 0.02 [-0.32, 0.24] | slow / step, c_m 0.00 {'merge': 0, 'hop_new': 3, 'finish': 22} | 0.011 (τ 0.20, p 0.021) | mixed |
| G37best | free | dw undefined (< 2 committing hosts) | | | | | | descriptive |
| G37rest | free | freeze / step | 0.25 (jk SE 0.3) | -3.34 | 0.02 [-0.42, 0.31] | slow / step, c_m 0.00 {'merge': 0, 'hop_new': 3, 'finish': 11} | 0.010 (τ 0.11, p 0.188) | failed |

Synthetic validity on this skeleton (A1 rule): valid (Q0 not frozen True, fields freeze True, finish not coarsening True; α identified True).
Native N3 (room replicas): #best room has < 2 committing hosts, so dw is undefined there; N3 is descriptive (A1). #rest alone: freeze, t_f 0.25 h.
Data: `data/processed/H128-coarsening-vs-freeze/G37/` (curve, deaths); figure: `../../figures/summary_obs.pdf`.

## Scorecard (period-specific axes)
- **C:** freeze baseline (t_f ≤ 3 h) and shape fits (constant/step/exponential/power, BIC).
- **D:** death kinds (merge vs finish) are unfitted; read share of merges –.
- **F:** real-skeleton synthetic (5 worlds × 60 runs): valid for dw.

## Notes
- 2026-10-04 22:19 UTC: folder and prediction written before any H128 statistic on this period.
- 2026-10-04 22:44 UTC: result filled (verdict mixed).
