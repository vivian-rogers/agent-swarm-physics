# H10 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-20)

**Verdict:** descriptive (F1 mixed, F2 ✗, F3 ✓)
**Role:** exploratory
**Period:** regime I · mode F · 12 agents (+1 −1; the Claude Code agent excluded) · #general only · 5 active days (41 windows). **Split:** 100-turn session cap on 2026-02-20, so the analyzed unit is 31a = 02-16 … 02-19.

## Why this period
The largest regime-I free week, but the week after it (#32) is held out, so #31 → #32 is a confirmatory pair (`../../analysis/confirm.py`). To keep that test blind, round 1 computes **nothing along ĝ₃₂** (whose kickoff text lies in the held-out window). Here #31 is used only (i) to describe a free week's fluctuation structure along directions that are not its successor's goal, and (ii) as the cross-week placebo covariance C for P4 in the regime-I pairs.

## Prediction
*Written 2026-10-03, before running on this period.*
- **F1, single well** along ĝ₁₂ and ĝ₁₇ (other weeks' goals, same regime basis) and along 50 random directions: unimodal F̂, |γ| < 1.
- **F2, weak coupling:** g < 0.5 along every direction used.
- **F3, stationarity:** no daily trend in δm along the directions used.
- **Placebo role:** in P4, C from #31 predicts the #11→#12 and #16→#17 response directions *worse* than each pair's own free-week C (if the soft modes are swarm-specific). If #31's C does as well, the soft modes are generic embedding geometry.
- **Verdict rule:** descriptive.

## Result
Run 2026-10-03 on unit 31a (12 agents, 33 windows), along ĝ₁₂ and ĝ₁₇ (never ĝ₃₂).

| Prediction | Observed along ĝ₁₂ | Observed along ĝ₁₇ | Verdict |
| --- | --- | --- | --- |
| F1 single well | γ = +0.31, 1 component | γ = +0.62, BIC prefers 2 | mixed |
| F2 g < 0.5 | g = 0.71 [0.59, 0.79] | g = 0.55 [0.05, 0.74] | ✗ |
| F3 no drift | slope CI [−0.008, 0.023] | slope CI [−0.029, 0.013] | ✓ |
| transverse | g⊥ = 0.74, R⊥ = 3.9 | g⊥ = 0.74, R⊥ = 3.9 | (same as the random-direction calibration) |
| P4 placebo role | #31's covariance predicts the #11 → #12a response at cos 0.41 and #16 → #17 at 0.15, vs each pair's own C at −0.09 and 0.10 | | the placebo does *not* do worse; P4 is uninformative anyway (Amendment 1) |

Data: `data/processed/H10-goals-are-legendre-pushes/G31/period_g12.json`, `period_g17.json`. Figure: [`figures/shape_and_drift.pdf`](figures/shape_and_drift.pdf). Card: [`../../README.md`](../../README.md).

## Scorecard (period-specific axes)
- **B:** stationarity holds along both directions.
- **C/D:** none. #31 → #32 remains blind for confirmation (`../../analysis/confirm.py`).

## Notes
- 2026-10-03: #31 → #32 reserved for confirmation; ĝ₃₂ is not built in round 1.
