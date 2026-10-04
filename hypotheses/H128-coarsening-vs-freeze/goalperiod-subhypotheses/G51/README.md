# H128 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 09-04 (non-holdout; tail held out))

**Verdict:** mixed
**Role:** exploratory (replication)
**Period:** regime III · mode P · 21–32 agents · #general (+#focus in 51g) · 45 days. Kickoff code: named (assigned artifact).

## Why this period
Private assigned goals (one target per agent); the 51a kickoff, first 20 active hours (2.5 days of 8 h, before NE32).

## Prediction
*Written 2026-10-04 22:19 UTC, before running H128 on this period.*
- Kickoff code: named. Expected: N_p reaches its final level within 3 active h (t_f ≤ 3 h), shape constant or step, no power-law selection (card P2).
- One target per agent: N_p ≈ N_h from the first round; R_d ≈ 1.
- Counts against: power law selected with t_f > 3 h.
- Verdict rule: supported if constant/step with t_f ≤ 3 h; failed if power law selected and t_f > 3 h; mixed otherwise; descriptive if untestable (N_pk < 4, < 6 hosts, or H < 10 h).

## Result
*Run 2026-10-04 22:44 UTC (`scheme/build.py`, `analysis/run.py`; non-holdout days; first 20.0 active h).* Primary observable dw = (N_p − 1)/(N_h − 1) (Amendment A1); N_p is the HH-literal secondary.

| Unit | Code | dw class / shape | t_f (active h) | A_u (h) | α̂ on dw [95% boot] | N_p (HH-literal) class / shape; merge share; deaths | dw drift per h (post hoc A2) | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G51 | named | slow / constant | 7.25 (jk SE 6.7) | 0.00 | -0.00 [-0.03, 0.02] | slow / step, c_m 0.18 {'merge': 6, 'hop_new': 9, 'finish': 18} | 0.001 (τ 0.05, p 0.607) | mixed |

Synthetic validity on this skeleton (A1 rule): valid (Q0 not frozen True, fields freeze True, finish not coarsening True; α identified True).

Data: `data/processed/H128-coarsening-vs-freeze/G51/` (curve, deaths); figure: `../../figures/summary_obs.pdf`.

## Scorecard (period-specific axes)
- **C:** freeze baseline (t_f ≤ 3 h) and shape fits (constant/step/exponential/power, BIC).
- **D:** death kinds (merge vs finish) are unfitted; read share of merges 0.33.
- **F:** real-skeleton synthetic (5 worlds × 60 runs): valid for dw.

## Notes
- 2026-10-04 22:19 UTC: folder and prediction written before any H128 statistic on this period.
- 2026-10-04 22:44 UTC: result filled (verdict mixed).
