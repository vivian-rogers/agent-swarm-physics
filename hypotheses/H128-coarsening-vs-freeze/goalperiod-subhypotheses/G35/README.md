# H128 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 03-20)

**Verdict:** mixed
**Role:** exploratory (replication)
**Period:** regime II · mode C · 12 agents · #best/#rest · 5 days. Kickoff code: named (assigned artifact).

## Why this period
Named target inherited from #34 (test the RPG): a shared-field freeze is expected.

## Prediction
*Written 2026-10-04 22:19 UTC, before running H128 on this period.*
- Kickoff code: named. Expected: N_p reaches its final level within 3 active h (t_f ≤ 3 h), shape constant or step, no power-law selection (card P2).
- Shared target: N_p falls to N∞ (few repos) within the first round of commits.
- Counts against: power law selected with t_f > 3 h.
- Verdict rule: supported if constant/step with t_f ≤ 3 h; failed if power law selected and t_f > 3 h; mixed otherwise; descriptive if untestable (N_pk < 4, < 6 hosts, or H < 10 h).

## Result
*Run 2026-10-04 22:44 UTC (`scheme/build.py`, `analysis/run.py`; non-holdout days; first 19.8 active h).* Primary observable dw = (N_p − 1)/(N_h − 1) (Amendment A1); N_p is the HH-literal secondary.

| Unit | Code | dw class / shape | t_f (active h) | A_u (h) | α̂ on dw [95% boot] | N_p (HH-literal) class / shape; merge share; deaths | dw drift per h (post hoc A2) | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G35 | named | slow / exponential | > 19.8 (censored) | 0.72 | 0.25 [0.15, 0.33] | freeze / step, c_m 0.00 {'merge': 0, 'hop_new': 0, 'finish': 7} | -0.004 (τ -0.15, p 0.068) | mixed |

Synthetic validity on this skeleton (A1 rule): valid (Q0 not frozen True, fields freeze True, finish not coarsening True; α identified True).

Data: `data/processed/H128-coarsening-vs-freeze/G35/` (curve, deaths); figure: `../../figures/summary_obs.pdf`.

## Scorecard (period-specific axes)
- **C:** freeze baseline (t_f ≤ 3 h) and shape fits (constant/step/exponential/power, BIC).
- **D:** death kinds (merge vs finish) are unfitted; read share of merges –.
- **F:** real-skeleton synthetic (5 worlds × 60 runs): valid for dw.

## Notes
- 2026-10-04 22:19 UTC: folder and prediction written before any H128 statistic on this period.
- 2026-10-04 22:44 UTC: result filled (verdict mixed).
