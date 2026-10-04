# H17 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 2026-05-11)

**Verdict:** failed (CK fails; t2* not beyond the sojourn null)
**Verdict (1b):** descriptive (Jev v3.1 soft-state replication; by the card's D3 rule soft P3b and the soft CK are not identifiable, so no verdict; the round-1 action-class verdict above stands)
**Role:** exploratory
**Period:** regime III · mode C (shared objective) · N = 15 at start · 5 active days.

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
*Run 2026-10-03* (`analysis/run_period.py`; numbers in `data/processed/H17-behavior-metastable-sets/G40/result.json`; figure `figures/its_ck.pdf`).

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2 CK passes at τ_c (max \|Δ\| < 0.05, k ≤ 4) | max \|Δ\| = 0.319; bootstrap-significant: yes | — | fail |
| P2 ITS plateau by τ ≤ 15 min | τ\* = – | — | no plateau |
| P3a t2\* > N1 | t2\* = 9.2 min [7.8, 10.6] | N1 p95 7.5 | pass |
| P3b t2\* > N2 and ratio ≥ 1.25 (400 surrogates, Holm across the 8 regime-III periods) | ratio t2\*/N2 median = 1.16; Holm p = 0.020 | N2 median 7.9; N3 median 4.2 | fail |
| P3c m ∈ {2,3}, crispness ≥ 0.75, t2/t3 ≥ 2 | m = 3, crispness 0.92, t2/t3 = 1.7 | — | fail |
| sets (m = 2 split) | [['browse', 'type'], ['shell', 'chat', 'idle', 'consolidate']] | — | idle alone/with consolidate: no |
| sets (m = 3) | [['idle'], ['browse', 'type'], ['shell', 'chat', 'consolidate']] | — | descriptive |
| R1 sticky-only t2 at τ_c | t2\*/t2_R1 = 1.59 | t2_R1 = 5.8 | descriptive |
| P8 MSM beats R1 and M0 on held-out days | ΔLL/pair vs R1 = 0.0860 (5/5 folds); vs M0 = 0.2467 | — | pass |
| order 2 vs 1 (τ = 1) | ΔLL/transition = 0.0557 | — | order 2 better |
| P5 per-agent I² of ln t2 | I² = 0.90 (15 agents; block-bootstrap SEs); own/shrink beats pooled for 0.93 of agents | — | pass |
| P6 committor asymmetry max \|δ\| | 0.023 (CI excl. 0: yes); cores ['browse', 'idle'] | 0 under detailed balance | fail |
| P7 σ(τ=1) > N2 p95; σ_macro/σ_micro < 0.5 | σ = 0.0096 nats/min; macro share 0.07 | N2 p95 0.0020 | pass |
| mixing time t_mix(¼) | 15 min | — | descriptive |
| R3 half-day t2\* (first / second half) | 8.9 / 9.5 | — | descriptive |
| robustness: 5-min windows (hard / soft counts / shifted = n/a) | 9.7 / 9.8 / – min | — | descriptive |
| robustness: records (≈5-min lag) | t2 ≈ 11.4 min | — | descriptive |
| stuckness covariates | error share 0.174; output 11.69/agent-h; idle share 0.15 | — | for P4b |

**Post hoc (boundary idle):** 22% of idle minutes lie in the leading/trailing idle run of an agent-day; without them t2\* = 9.4 min (N2 median 8.1), m = 2 split [['browse', 'type'], ['shell', 'chat', 'idle', 'consolidate']].
**Per-agent t2 (τ_c):** 21: 2, 10: 3, 16: 3, 17: 3, 24: 4, 14: 4, 20: 5, 23: 6, 26: 6, 22: 6, 18: 6, 12: 8, 25: 9, 13: 11, 6: 14 min (agent codes from `roster.parquet`); lab η² = 0.31 (perm p = 0.42).
**Within-period stuckness (per agent, n = 15):** ρ(t2, error share) = +0.16; ρ(t2, output rate) = +0.20; ρ(t2, idle share) = +0.05.

## Scorecard (period-specific axes)
| Axis | Evidence | Score |
| --- | --- | --- |
| B assumptions | CK max \|Δ\| 0.319 (fail); ITS rise t2(15)/t2(1) = 6.7; plateau: none; order 2 better by 0.056 nats; halves 9/9 min | 0 |
| C adequacy | MSM vs R1 ΔLL/pair +0.0860, vs M0 +0.247 (day-blocked) | 1 |
| D unfitted | t2\*/N2 = 1.16 (sets beyond sticky states: no); trimmed t2\*/N2 = 1.15 | 0 |
| G ground truth | slow set = [['browse', 'type'], ['shell', 'chat', 'idle', 'consolidate']]; 22% of idle minutes are boundary runs (scaffold/schedule) | 1 |

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods): Jev v3.1 states lumped to 6 macro states (work, inquire, fix, talk, wait = monitor_wait + idle + absent, maint), shifted estimator at τ = 5 min; covariates from real failures instead of `actions.error`. Prediction: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H17-behavior-metastable-sets/r1b/G40.json`.*

| Statistic | Round 1 (action classes) | Round 1b (v3) |
| --- | --- | --- |
| t2\* (min) | 9.2 | raw λ₂ ≈ 1 (unidentified), bias-corrected λ₂ ≈ 1 (unidentified), equal-n λ₂ ≈ 1 (unidentified) |
| in-span windows / agents | – | 3541 / 15 |
| m = 2 slow split | (see Result above) | inquire+fix+talk+wait+maint vs work |
| soft CK max \|Δ\| (no power) | – | 0.007 |
| argmax MSM beats M0 and R1 (P8) | – | False |
| failure share of computer-use turns | stderr 0.174 | real 0.026 |
| mean p_blocked / output per in-span hour | – | 0.224 / 15.63 |

Reading: the v3 slowest mode here is not identified (λ₂ ≈ 1 at this sample size); see the card for the cross-period tests (P4b-1b, P4c-1b), which failed.
