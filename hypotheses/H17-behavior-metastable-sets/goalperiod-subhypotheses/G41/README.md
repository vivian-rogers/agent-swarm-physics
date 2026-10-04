# H17 × G41: Perform novel research! (2026-05-11 → 2026-05-18)

**Verdict:** mixed (CK fails)
**Verdict (1b):** descriptive (Jev v3.1 soft-state replication; by the card's D3 rule soft P3b and the soft CK are not identifiable, so no verdict; the round-1 action-class verdict above stands)
**Role:** exploratory
**Period:** regime III · mode I (each agent its own objective) · N = 15 at start · 5 active days.

## Why this period
A regime-III non-holdout period: one of the 8 periods for the primary tests (P3b, Holm across periods) and for P4.

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions (`../../README.md`, "Prediction") as they apply here; states = H14 coarse 6-state minute grid, pooled MSM over present agent-days, τ_c = 5 min:
- **CK (P2):** the crisp-set CK test passes at τ_c = 5 min (max |Δ| < 0.05 for k ≤ 4).
- **P3b (sets beyond sticky states):** t2\* above the N2 sojourn-null 95th percentile and t2\*/median(N2) ≥ 1.25.
- **P8:** the MSM beats R1 (sticky-only) and M0 on held-out days at τ_c.
- **P3a:** t2\* above the N1 shuffled floor.
- **P5:** per-agent I² of ln t2 ≥ 0.5 (if ≥ 3 agents qualify).
- **P3d:** idle sits in a set of its own (alone or with consolidate) in the m = 2 split.
- **P3e:** 5 ≤ t2\* ≤ 60 active minutes.
- **P6:** max |δ_i| ≥ 0.1 with a bootstrap CI excluding 0; if the m = 2 cores are a work state and idle, chat has q⁺ > 0.5 and 1 − q⁻ < 0.5.
- **P7:** σ(τ = 1) above the N2 95th percentile; σ_macro/σ_micro (m = 3) < 0.5.

Verdict rule (card): **supported** if CK passes, P3b holds and P8 holds; **mixed** if exactly one of CK or P3b fails; **failed** if both fail.

## Result
*Run 2026-10-03* (`analysis/run_period.py`; numbers in `data/processed/H17-behavior-metastable-sets/G41/result.json`; figure `figures/its_ck.pdf`).

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2 CK passes at τ_c (max \|Δ\| < 0.05, k ≤ 4) | max \|Δ\| = 0.284; bootstrap-significant: yes | — | fail |
| P2 ITS plateau by τ ≤ 15 min | τ\* = – | — | no plateau |
| P3a t2\* > N1 | t2\* = 8.4 min [7.0, 10.4] | N1 p95 5.6 | pass |
| P3b t2\* > N2 and ratio ≥ 1.25 (400 surrogates, Holm across the 8 regime-III periods) | ratio t2\*/N2 median = 1.33; Holm p = 0.020 | N2 median 6.4; N3 median 4.1 | pass |
| P3c m ∈ {2,3}, crispness ≥ 0.75, t2/t3 ≥ 2 | m = 2, crispness 0.91, t2/t3 = 1.7 | — | fail |
| sets (m = 2 split) | [['browse', 'type'], ['shell', 'chat', 'idle', 'consolidate']] | — | idle alone/with consolidate: no |
| sets (m = 2) | [['browse', 'type'], ['shell', 'chat', 'idle', 'consolidate']] | — | descriptive |
| R1 sticky-only t2 at τ_c | t2\*/t2_R1 = 1.52 | t2_R1 = 5.6 | descriptive |
| P8 MSM beats R1 and M0 on held-out days | ΔLL/pair vs R1 = 0.0538 (5/5 folds); vs M0 = 0.2012 | — | pass |
| order 2 vs 1 (τ = 1) | ΔLL/transition = 0.0547 | — | order 2 better |
| P5 per-agent I² of ln t2 | I² = 0.89 (15 agents; block-bootstrap SEs); own/shrink beats pooled for 0.93 of agents | — | pass |
| P6 committor asymmetry max \|δ\| | 0.014 (CI excl. 0: no); cores ['type', 'idle'] | 0 under detailed balance | fail |
| P7 σ(τ=1) > N2 p95; σ_macro/σ_micro < 0.5 | σ = 0.0092 nats/min; macro share 0.03 | N2 p95 0.0018 | pass |
| mixing time t_mix(¼) | 15 min | — | descriptive |
| R3 half-day t2\* (first / second half) | 8.3 / 8.7 | — | descriptive |
| robustness: 5-min windows (hard / soft counts / shifted = n/a) | 9.6 / 8.7 / – min | — | descriptive |
| robustness: records (≈5-min lag) | t2 ≈ 9.8 min | — | descriptive |
| stuckness covariates | error share 0.141; output 9.63/agent-h; idle share 0.20 | — | for P4b |

**Post hoc (boundary idle):** 15% of idle minutes lie in the leading/trailing idle run of an agent-day; without them t2\* = 8.6 min (N2 median 6.5), m = 2 split [['browse', 'type'], ['shell', 'chat', 'idle', 'consolidate']].
**Per-agent t2 (τ_c):** 21: 2, 10: 2, 26: 3, 22: 4, 24: 5, 23: 6, 14: 6, 20: 6, 17: 6, 18: 6, 16: 7, 25: 7, 13: 8, 12: 8, 6: 10 min (agent codes from `roster.parquet`); lab η² = 0.14 (perm p = 0.79).
**Within-period stuckness (per agent, n = 15):** ρ(t2, error share) = +0.15; ρ(t2, output rate) = +0.32; ρ(t2, idle share) = +0.14.

## Scorecard (period-specific axes)
| Axis | Evidence | Score |
| --- | --- | --- |
| B assumptions | CK max \|Δ\| 0.284 (fail); ITS rise t2(15)/t2(1) = 6.0; plateau: none; order 2 better by 0.055 nats; halves 8/9 min | 0 |
| C adequacy | MSM vs R1 ΔLL/pair +0.0538, vs M0 +0.201 (day-blocked) | 2 |
| D unfitted | t2\*/N2 = 1.33 (sets beyond sticky states: yes); trimmed t2\*/N2 = 1.33 | 1 |
| G ground truth | slow set = [['browse', 'type'], ['shell', 'chat', 'idle', 'consolidate']]; 15% of idle minutes are boundary runs (scaffold/schedule) | 1 |

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods): Jev v3.1 states lumped to 6 macro states (work, inquire, fix, talk, wait = monitor_wait + idle + absent, maint), shifted estimator at τ = 5 min; covariates from real failures instead of `actions.error`. Prediction: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H17-behavior-metastable-sets/r1b/G41.json`.*

| Statistic | Round 1 (action classes) | Round 1b (v3) |
| --- | --- | --- |
| t2\* (min) | 8.4 | raw 122, bias-corrected 87, equal-n 131 |
| in-span windows / agents | – | 3505 / 15 |
| m = 2 slow split | (see Result above) | wait vs work+inquire+fix+talk+maint |
| soft CK max \|Δ\| (no power) | – | 0.010 |
| argmax MSM beats M0 and R1 (P8) | – | False |
| failure share of computer-use turns | stderr 0.141 | real 0.051 |
| mean p_blocked / output per in-span hour | – | 0.233 / 12.12 |

Reading: the v3 slowest mode here is hour-scale (agent-day mixture, R2/R3); see the card for the cross-period tests (P4b-1b, P4c-1b), which failed.
