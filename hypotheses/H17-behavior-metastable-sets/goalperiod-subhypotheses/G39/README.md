# H17 × G39: Build your own interactive world! (2026-04-27 → 2026-05-04)

**Verdict:** failed (CK fails; t2* not beyond the sojourn null)
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
*Run 2026-10-03* (`analysis/run_period.py`; numbers in `data/processed/H17-behavior-metastable-sets/G39/result.json`; figure `figures/its_ck.pdf`).

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2 CK passes at τ_c (max \|Δ\| < 0.05, k ≤ 4) | max \|Δ\| = 0.161; bootstrap-significant: yes | — | fail |
| P2 ITS plateau by τ ≤ 15 min | τ\* = – | — | no plateau |
| P3a t2\* > N1 | t2\* = 6.6 min [5.6, 7.8] | N1 p95 4.6 | pass |
| P3b t2\* > N2 and ratio ≥ 1.25 (400 surrogates, Holm across the 8 regime-III periods) | ratio t2\*/N2 median = 1.25; Holm p = 0.020 | N2 median 5.3; N3 median 4.0 | fail |
| P3c m ∈ {2,3}, crispness ≥ 0.75, t2/t3 ≥ 2 | m = 2, crispness 0.79, t2/t3 = 1.7 | — | fail |
| sets (m = 2 split) | [['shell', 'chat', 'idle'], ['browse', 'type', 'consolidate']] | — | idle alone/with consolidate: no |
| sets (m = 2) | [['shell', 'chat', 'idle'], ['browse', 'type', 'consolidate']] | — | descriptive |
| R1 sticky-only t2 at τ_c | t2\*/t2_R1 = 1.25 | t2_R1 = 5.3 | descriptive |
| P8 MSM beats R1 and M0 on held-out days | ΔLL/pair vs R1 = 0.0376 (5/5 folds); vs M0 = 0.1548 | — | pass |
| order 2 vs 1 (τ = 1) | ΔLL/transition = 0.0437 | — | order 2 better |
| P5 per-agent I² of ln t2 | I² = 0.90 (15 agents; block-bootstrap SEs); own/shrink beats pooled for 0.80 of agents | — | pass |
| P6 committor asymmetry max \|δ\| | 0.024 (CI excl. 0: no); cores ['idle', 'browse'] | 0 under detailed balance | fail |
| P7 σ(τ=1) > N2 p95; σ_macro/σ_micro < 0.5 | σ = 0.0232 nats/min; macro share 0.03 | N2 p95 0.0020 | pass |
| mixing time t_mix(¼) | 10 min | — | descriptive |
| R3 half-day t2\* (first / second half) | 6.0 / 7.3 | — | descriptive |
| robustness: 5-min windows (hard / soft counts / shifted = n/a) | 7.9 / 7.1 / – min | — | descriptive |
| robustness: records (≈5-min lag) | t2 ≈ 6.0 min | — | descriptive |
| stuckness covariates | error share 0.085; output 9.02/agent-h; idle share 0.21 | — | for P4b |

**Post hoc (boundary idle):** 27% of idle minutes lie in the leading/trailing idle run of an agent-day; without them t2\* = 6.0 min (N2 median 4.7), m = 2 split [['browse', 'type', 'consolidate'], ['shell', 'chat', 'idle']].
**Per-agent t2 (τ_c):** 21: 2, 20: 3, 24: 3, 23: 3, 10: 4, 17: 4, 25: 4, 14: 4, 26: 4, 12: 6, 13: 7, 18: 8, 16: 13, 6: 14, 22: 29 min (agent codes from `roster.parquet`); lab η² = 0.55 (perm p = 0.10).
**Within-period stuckness (per agent, n = 15):** ρ(t2, error share) = +0.07; ρ(t2, output rate) = +0.19; ρ(t2, idle share) = +0.16.

## Scorecard (period-specific axes)
| Axis | Evidence | Score |
| --- | --- | --- |
| B assumptions | CK max \|Δ\| 0.161 (fail); ITS rise t2(15)/t2(1) = 5.5; plateau: none; order 2 better by 0.044 nats; halves 6/7 min | 0 |
| C adequacy | MSM vs R1 ΔLL/pair +0.0376, vs M0 +0.155 (day-blocked) | 1 |
| D unfitted | t2\*/N2 = 1.25 (sets beyond sticky states: no); trimmed t2\*/N2 = 1.26 | 0 |
| G ground truth | slow set = [['shell', 'chat', 'idle'], ['browse', 'type', 'consolidate']]; 27% of idle minutes are boundary runs (scaffold/schedule) | 1 |

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods): Jev v3.1 states lumped to 6 macro states (work, inquire, fix, talk, wait = monitor_wait + idle + absent, maint), shifted estimator at τ = 5 min; covariates from real failures instead of `actions.error`. Prediction: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H17-behavior-metastable-sets/r1b/G39.json`.*

| Statistic | Round 1 (action classes) | Round 1b (v3) |
| --- | --- | --- |
| t2\* (min) | 6.6 | raw 598, bias-corrected λ₂ ≈ 1 (unidentified), equal-n 258 |
| in-span windows / agents | – | 3403 / 15 |
| m = 2 slow split | (see Result above) | inquire+fix+maint vs work+wait |
| soft CK max \|Δ\| (no power) | – | 0.056 |
| argmax MSM beats M0 and R1 (P8) | – | True |
| failure share of computer-use turns | stderr 0.085 | real 0.024 |
| mean p_blocked / output per in-span hour | – | 0.202 / 13.71 |

Reading: the v3 slowest mode here is hour-scale (agent-day mixture, R2/R3); see the card for the cross-period tests (P4b-1b, P4c-1b), which failed.
