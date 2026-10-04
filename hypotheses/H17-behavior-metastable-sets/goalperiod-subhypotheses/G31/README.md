# H17 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-23)

**Verdict:** mixed (CK fails)
**Verdict (1b):** descriptive (Jev v3.1 soft-state replication; by the card's D3 rule soft P3b and the soft CK are not identifiable, so no verdict; the round-1 action-class verdict above stands)
**Role:** replication (exploratory)
**Period:** regime I · mode F (free / none) · N = 12 at start · 5 active days.

## Why this period
Regime-I free-choice period (about nine agents converged on one task): the undriven regime-I reference for P4d.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions (`../../README.md`, "Prediction") as they apply here; states = H14 coarse 6-state minute grid, pooled MSM over present agent-days, τ_c = 5 min:
- **CK (P2):** the crisp-set CK test passes at τ_c = 5 min (max |Δ| < 0.05 for k ≤ 4).
- **P3b (sets beyond sticky states):** t2\* above the N2 sojourn-null 95th percentile and t2\*/median(N2) ≥ 1.25.
- **P8:** the MSM beats R1 (sticky-only) and M0 on held-out days at τ_c.
- **P3a:** t2\* above the N1 shuffled floor.
- **P5:** per-agent I² of ln t2 ≥ 0.5 (if ≥ 3 agents qualify).
- **P4c (regime part):** t2\* above the median of the regime-III periods (session on/off makes a slow two-set process).
- **Regime-I set identity (credence 0.6):** the m = 2 split separates in-session computer work (browse/type/shell) from out-of-session states (chat/idle/session events).
- **P4d:** this free-choice period is not the fastest (smallest t2\*) of its regime. Descriptive.
- **NE11 (02-20, 100-turn session cap) inside the period:** not split; noted as a caveat.

Verdict rule (card): **supported** if CK passes, P3b holds and P8 holds; **mixed** if exactly one of CK or P3b fails; **failed** if both fail.

## Result
*Run 2026-10-03* (`analysis/run_period.py`; numbers in `data/processed/H17-behavior-metastable-sets/G31/result.json`; figure `figures/its_ck.pdf`).

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2 CK passes at τ_c (max \|Δ\| < 0.05, k ≤ 4) | max \|Δ\| = 0.196; bootstrap-significant: yes | — | fail |
| P2 ITS plateau by τ ≤ 15 min | τ\* = – | — | no plateau |
| P3a t2\* > N1 | t2\* = 6.3 min [5.6, 7.0] | N1 p95 4.7 | pass |
| P3b t2\* > N2 p95 and ratio ≥ 1.25 | ratio t2\*/N2 median = 1.28 | N2 median 4.9, p95 5.0; N3 median 3.4 | pass |
| P3c m ∈ {2,3}, crispness ≥ 0.75, t2/t3 ≥ 2 | m = 2, crispness 0.87, t2/t3 = 2.2 | — | pass |
| sets (m = 2 split) | [['browse', 'type'], ['shell', 'chat', 'idle', 'consolidate']] | — | descriptive |
| sets (m = 2) | [['browse', 'type'], ['shell', 'chat', 'idle', 'consolidate']] | — | descriptive |
| R1 sticky-only t2 at τ_c | t2\*/t2_R1 = 1.51 | t2_R1 = 4.1 | descriptive |
| P8 MSM beats R1 and M0 on held-out days | ΔLL/pair vs R1 = 0.0555 (5/5 folds); vs M0 = 0.1215 | — | pass |
| order 2 vs 1 (τ = 1) | ΔLL/transition = 0.0482 | — | order 2 better |
| P5 per-agent I² of ln t2 | I² = 0.89 (12 agents; block-bootstrap SEs); own/shrink beats pooled for 0.92 of agents | — | pass |
| P6 committor asymmetry max \|δ\| | 0.009 (CI excl. 0: no); cores ['type', 'shell'] | 0 under detailed balance | descriptive |
| P7 σ(τ=1) > N2 p95; σ_macro/σ_micro < 0.5 | σ = 0.0819 nats/min; macro share 0.01 | N2 p95 0.0022 | descriptive |
| mixing time t_mix(¼) | 10 min | — | descriptive |
| R3 half-day t2\* (first / second half) | 6.3 / 6.2 | — | descriptive |
| robustness: 5-min windows (hard / soft counts / shifted = n/a) | 8.4 / 6.5 / – min | — | descriptive |
| robustness: records (≈5-min lag) | t2 ≈ 10.0 min | — | descriptive |
| stuckness covariates | error share 0.098; output 5.02/agent-h; idle share 0.25 | — | for P4b |

**Post hoc (boundary idle):** 2% of idle minutes lie in the leading/trailing idle run of an agent-day; without them t2\* = 6.3 min (N2 median 4.9), m = 2 split [['browse', 'type'], ['shell', 'chat', 'idle', 'consolidate']].
**Per-agent t2 (τ_c):** 17: 2, 12: 2, 21: 3, 13: 3, 20: 3, 18: 3, 16: 4, 10: 4, 14: 6, 0: 7, 15: 7, 6: 10 min (agent codes from `roster.parquet`); lab η² = 0.64 (perm p = 0.04).
**Within-period stuckness (per agent, n = 12):** ρ(t2, error share) = +0.25; ρ(t2, output rate) = -0.09; ρ(t2, idle share) = -0.08.

## Scorecard (period-specific axes)
| Axis | Evidence | Score |
| --- | --- | --- |
| B assumptions | CK max \|Δ\| 0.196 (fail); ITS rise t2(15)/t2(1) = 4.9; plateau: none; order 2 better by 0.048 nats; halves 6/6 min | 0 |
| C adequacy | MSM vs R1 ΔLL/pair +0.0555, vs M0 +0.122 (day-blocked) | 2 |
| D unfitted | t2\*/N2 = 1.28 (sets beyond sticky states: yes); trimmed t2\*/N2 = 1.27 | 1 |
| G ground truth | slow set = [['browse', 'type'], ['shell', 'chat', 'idle', 'consolidate']]; 2% of idle minutes are boundary runs (scaffold/schedule) | 1 |

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods): Jev v3.1 states lumped to 6 macro states (work, inquire, fix, talk, wait = monitor_wait + idle + absent, maint), shifted estimator at τ = 5 min; covariates from real failures instead of `actions.error`. Prediction: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H17-behavior-metastable-sets/r1b/G31.json`.*

| Statistic | Round 1 (action classes) | Round 1b (v3) |
| --- | --- | --- |
| t2\* (min) | 6.3 | raw 185, bias-corrected 176, equal-n 185 |
| in-span windows / agents | – | 2652 / 12 |
| m = 2 slow split | (see Result above) | wait vs work+inquire+fix+talk+maint |
| soft CK max \|Δ\| (no power) | – | 0.025 |
| argmax MSM beats M0 and R1 (P8) | – | False |
| failure share of computer-use turns | stderr 0.098 | real 0.051 |
| mean p_blocked / output per in-span hour | – | 0.273 / 5.37 |

Reading: the v3 slowest mode here is hour-scale (agent-day mixture, R2/R3); see the card for the cross-period tests (P4b-1b, P4c-1b), which failed.
