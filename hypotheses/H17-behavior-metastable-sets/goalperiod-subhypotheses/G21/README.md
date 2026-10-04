# H17 × G21: Forecast the abilities and effects of AI (2025-12-01 → 2025-12-08)

**Verdict:** mixed (CK fails)
**Verdict (1b):** descriptive (Jev v3.1 soft-state replication; by the card's D3 rule soft P3b and the soft CK are not identifiable, so no verdict; the round-1 action-class verdict above stands)
**Role:** exploratory
**Period:** regime I · mode I (each agent its own objective) · N = 8 at start · 5 active days.

## Why this period
Regime-I comparison period (one room, discrete computer sessions): sets the regime-I distribution of t2* for P4c and for the #32 confirmation (P9).

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions (`../../README.md`, "Prediction") as they apply here; states = H14 coarse 6-state minute grid, pooled MSM over present agent-days, τ_c = 5 min:
- **CK (P2):** the crisp-set CK test passes at τ_c = 5 min (max |Δ| < 0.05 for k ≤ 4).
- **P3b (sets beyond sticky states):** t2\* above the N2 sojourn-null 95th percentile and t2\*/median(N2) ≥ 1.25.
- **P8:** the MSM beats R1 (sticky-only) and M0 on held-out days at τ_c.
- **P3a:** t2\* above the N1 shuffled floor.
- **P5:** per-agent I² of ln t2 ≥ 0.5 (if ≥ 3 agents qualify).
- **P4c (regime part):** t2\* above the median of the regime-III periods (session on/off makes a slow two-set process).
- **Regime-I set identity (credence 0.6):** the m = 2 split separates in-session computer work (browse/type/shell) from out-of-session states (chat/idle/session events).
- **P10 (NE07, axis E; added 2026-10-03 before running):** t2\* on 12-04 → 12-05 (after the "don't do nothing" prompt) below t2\* on 12-01 → 12-03; agent-day bootstrap CI of the difference excludes 0. Credence 0.35.

Verdict rule (card): **supported** if CK passes, P3b holds and P8 holds; **mixed** if exactly one of CK or P3b fails; **failed** if both fail.

## Result
*Run 2026-10-03* (`analysis/run_period.py`; numbers in `data/processed/H17-behavior-metastable-sets/G21/result.json`; figure `figures/its_ck.pdf`).

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2 CK passes at τ_c (max \|Δ\| < 0.05, k ≤ 4) | max \|Δ\| = 0.163; bootstrap-significant: yes | — | fail |
| P2 ITS plateau by τ ≤ 15 min | τ\* = 1.00 | — | pass |
| P3a t2\* > N1 | t2\* = 5.5 min [4.6, 6.4] | N1 p95 3.8 | pass |
| P3b t2\* > N2 p95 and ratio ≥ 1.25 | ratio t2\*/N2 median = 1.36 | N2 median 4.0, p95 4.2; N3 median 4.0 | pass |
| P3c m ∈ {2,3}, crispness ≥ 0.75, t2/t3 ≥ 2 | m = 2, crispness 0.86, t2/t3 = 1.8 | — | fail |
| sets (m = 2 split) | [['shell', 'chat', 'idle'], ['browse', 'type', 'consolidate']] | — | descriptive |
| sets (m = 2) | [['shell', 'chat', 'idle'], ['browse', 'type', 'consolidate']] | — | descriptive |
| R1 sticky-only t2 at τ_c | t2\*/t2_R1 = 1.33 | t2_R1 = 4.1 | descriptive |
| P8 MSM beats R1 and M0 on held-out days | ΔLL/pair vs R1 = 0.0309 (4/5 folds); vs M0 = 0.1118 | — | pass |
| order 2 vs 1 (τ = 1) | ΔLL/transition = 0.0519 | — | order 2 better |
| P5 per-agent I² of ln t2 | I² = 0.91 (9 agents; block-bootstrap SEs); own/shrink beats pooled for 1.00 of agents | — | pass |
| P6 committor asymmetry max \|δ\| | 0.041 (CI excl. 0: no); cores ['shell', 'type'] | 0 under detailed balance | descriptive |
| P7 σ(τ=1) > N2 p95; σ_macro/σ_micro < 0.5 | σ = 0.0397 nats/min; macro share 0.08 | N2 p95 0.0036 | descriptive |
| mixing time t_mix(¼) | 10 min | — | descriptive |
| R3 half-day t2\* (first / second half) | 3.9 / 7.1 | — | descriptive |
| robustness: 5-min windows (hard / soft counts / shifted = n/a) | 7.4 / 5.9 / – min | — | descriptive |
| robustness: records (≈5-min lag) | t2 ≈ 12.2 min | — | descriptive |
| stuckness covariates | error share 0.012; output 0.01/agent-h; idle share 0.27 | — | for P4b |

**NE07 split at 2025-12-04:** t2\* before 4.2 min [3.1, 5.6] (24 agent-days) vs after 7.1 [6.0, 8.6] (18); difference +2.9 min, 95% CI [+1.0, +4.9]; idle share 0.21 → 0.36.
**Post hoc (boundary idle):** 3% of idle minutes lie in the leading/trailing idle run of an agent-day; without them t2\* = 5.4 min (N2 median 4.0), m = 2 split [['shell', 'chat', 'idle'], ['browse', 'type', 'consolidate']].
**Per-agent t2 (τ_c):** 10: 2, 17: 2, 13: 4, 14: 5, 12: 5, 15: 6, 0: 6, 6: 6, 16: 6 min (agent codes from `roster.parquet`); lab η² = 0.68 (perm p = 0.09).
**Within-period stuckness (per agent, n = 9):** ρ(t2, error share) = -0.27; ρ(t2, output rate) = -0.41; ρ(t2, idle share) = +0.18.

## Scorecard (period-specific axes)
| Axis | Evidence | Score |
| --- | --- | --- |
| B assumptions | CK max \|Δ\| 0.163 (fail); ITS rise t2(15)/t2(1) = 3.9; plateau: 1.0; order 2 better by 0.052 nats; halves 4/7 min | 0 |
| C adequacy | MSM vs R1 ΔLL/pair +0.0309, vs M0 +0.112 (day-blocked) | 2 |
| D unfitted | t2\*/N2 = 1.36 (sets beyond sticky states: yes); trimmed t2\*/N2 = 1.35 | 1 |
| G ground truth | slow set = [['shell', 'chat', 'idle'], ['browse', 'type', 'consolidate']]; 3% of idle minutes are boundary runs (scaffold/schedule) | 1 |

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods): Jev v3.1 states lumped to 6 macro states (work, inquire, fix, talk, wait = monitor_wait + idle + absent, maint), shifted estimator at τ = 5 min; covariates from real failures instead of `actions.error`. Prediction: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H17-behavior-metastable-sets/r1b/G21.json`.*

| Statistic | Round 1 (action classes) | Round 1b (v3) |
| --- | --- | --- |
| t2\* (min) | 5.5 | raw 61, bias-corrected 43, equal-n 61 |
| in-span windows / agents | – | 1966 / 9 |
| m = 2 slow split | (see Result above) | work+inquire+fix+maint vs talk+wait |
| soft CK max \|Δ\| (no power) | – | 0.003 |
| argmax MSM beats M0 and R1 (P8) | – | False |
| failure share of computer-use turns | stderr 0.012 | real 0.008 |
| mean p_blocked / output per in-span hour | – | 0.399 / 0.00 |

Reading: the v3 slowest mode here is tens of minutes; see the card for the cross-period tests (P4b-1b, P4c-1b), which failed.
