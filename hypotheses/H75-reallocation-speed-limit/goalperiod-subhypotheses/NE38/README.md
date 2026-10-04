# H75 × NE38 (G51 head): single-agent re-allocations — newcomers from scratch and one role reassignment

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** #51 non-holdout head (2026-07-06 → 09-04): the newcomers who join from 07-09 to 09-04 (each starts at ∅ at its first ledger call), and NE38 (2026-07-29 16:51 UTC: Claude Opus 5's role changes from game dev to mathematician; DQ6 role rows). 12-active-hour window per agent.

## Why this period
- Each newcomer and the reassigned agent is a one-agent quench at a known instant. Cadence differs by model, so the cross-newcomer slope of settling time on call rate is the exploratory analogue of NE20 (a cadence-only change; held out).

## Prediction
*Written 2026-10-04 ~20:15 UTC, after the synthetic validation (amendment A1), before running on this period.*
- N2: |ε| ≤ 0.3 across newcomers (point estimate; CI expected wide, n ≈ 10), median newcomer t_i ≤ 10 active h, and NE38's t inside the newcomer range → supported; all three fail → failed; otherwise mixed. Credence 0.4. Note (A1): the synthetic field-limited null gives ε ≈ −0.5 for ensembles with churn; single-agent windows have less churn, so the 0.3 band stays as written.

## Result
*Run 2026-10-04 ~20:50 UTC (`analysis/run.py: native_g51_newcomers`; `data/processed/H75-reallocation-speed-limit/G51/results_native_newcomers.json`).* Agent codes only (roster codes).

| Newcomer (code) | t_i (active h) | calls/h | commits/h | switches in 12 h | repos |
| --- | --- | --- | --- | --- | --- |
| 35 | 0.942 | 131 | 6.5 | 2 | 2 |
| 36 | 0.025 | 70 | 1.9 | 1 | 1 |
| 37 | 0.008 | 114 | 0.3 | 1 | 1 |
| 38 | 2.463 | 158 | 13.7 | 108 | 3 |
| 39 | 0.494 | 58 | 5.2 | 1 | 1 |
| 40 | 0.592 | 132 | 9.8 | 15 | 7 |
| 41 | 0.087 | 65 | 5.1 | 13 | 2 |
| 42 | 0.202 | 92 | 11.2 | 1 | 1 |
| 43 | 0.371 | 59 | 8.8 | 1 | 1 |
| 44 | 0.280 | 155 | 5.2 | 19 | 3 |
| 45 | 0.073 | 94 | 4.5 | 1 | 1 |

- Median newcomer t_i = 0.28 h (range 0.008–2.46 h): most newcomers commit to their settled repo within minutes of their first call.
- ε across newcomers = 1.32 ± 1.25 (n 11); with the commit-rate control 1.04 ± 0.69. Fails |ε| ≤ 0.3 at the point estimate; the CI includes 0 and excludes −1 only in the controlled fit.
- NE38 (code 40, 07-29 reassignment): first commit on its new settled repo after 2.03 active h, 3 switches, 2 repos; inside the newcomer range.

| Check | Observed | Verdict |
| --- | --- | --- |
| \|ε\| ≤ 0.3 | 1.32 | fails |
| median t_i ≤ 10 h | 0.28 h | holds |
| NE38 inside the newcomer range | 2.03 h in [0.008, 2.46] | holds |

**Verdict: mixed.** Single-agent re-allocations are fast (minutes to 2.5 h). The cadence elasticity is not measurable on 11 agents.
