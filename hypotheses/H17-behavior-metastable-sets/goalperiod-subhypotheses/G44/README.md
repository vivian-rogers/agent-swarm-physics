# H17 × G44: Finetune your leader! (2026-05-26 → 2026-06-01)

**Verdict:** failed (CK fails; t2* not beyond the sojourn null)
**Verdict (1b):** descriptive (Jev v3.1 soft-state replication; by the card's D3 rule soft P3b and the soft CK are not identifiable, so no verdict; the round-1 action-class verdict above stands)
**Role:** replication (exploratory)
**Period:** regime III · mode C (shared objective) · N = 16 at start · 4 active days.

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
*Run 2026-10-03* (`analysis/run_period.py`; numbers in `data/processed/H17-behavior-metastable-sets/G44/result.json`; figure `figures/its_ck.pdf`).

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2 CK passes at τ_c (max \|Δ\| < 0.05, k ≤ 4) | max \|Δ\| = 0.256; bootstrap-significant: yes | — | fail |
| P2 ITS plateau by τ ≤ 15 min | τ\* = – | — | no plateau |
| P3a t2\* > N1 | t2\* = 7.5 min [6.1, 8.7] | N1 p95 5.2 | pass |
| P3b t2\* > N2 and ratio ≥ 1.25 (400 surrogates, Holm across the 8 regime-III periods) | ratio t2\*/N2 median = 1.22; Holm p = 0.020 | N2 median 6.1; N3 median 4.3 | fail |
| P3c m ∈ {2,3}, crispness ≥ 0.75, t2/t3 ≥ 2 | m = 3, crispness 0.90, t2/t3 = 1.7 | — | fail |
| sets (m = 2 split) | [['browse', 'type'], ['shell', 'chat', 'idle', 'consolidate']] | — | idle alone/with consolidate: no |
| sets (m = 3) | [['browse', 'type'], ['idle'], ['shell', 'chat', 'consolidate']] | — | descriptive |
| R1 sticky-only t2 at τ_c | t2\*/t2_R1 = 1.25 | t2_R1 = 6.0 | descriptive |
| P8 MSM beats R1 and M0 on held-out days | ΔLL/pair vs R1 = 0.0397 (4/4 folds); vs M0 = 0.1703 | — | pass |
| order 2 vs 1 (τ = 1) | ΔLL/transition = 0.0315 | — | order 2 better |
| P5 per-agent I² of ln t2 | I² = 0.84 (17 agents; block-bootstrap SEs); own/shrink beats pooled for 0.89 of agents | — | pass |
| P6 committor asymmetry max \|δ\| | 0.006 (CI excl. 0: no); cores ['type', 'idle'] | 0 under detailed balance | fail |
| P7 σ(τ=1) > N2 p95; σ_macro/σ_micro < 0.5 | σ = 0.0039 nats/min; macro share 0.05 | N2 p95 0.0021 | pass |
| mixing time t_mix(¼) | 10 min | — | descriptive |
| R3 half-day t2\* (first / second half) | 6.8 / 8.4 | — | descriptive |
| robustness: 5-min windows (hard / soft counts / shifted = n/a) | 10.0 / 8.1 / – min | — | descriptive |
| robustness: records (≈5-min lag) | t2 ≈ 7.9 min | — | descriptive |
| stuckness covariates | error share 0.105; output 6.77/agent-h; idle share 0.25 | — | for P4b |

**Post hoc (boundary idle):** 24% of idle minutes lie in the leading/trailing idle run of an agent-day; without them t2\* = 6.9 min (N2 median 5.6), m = 2 split [['browse', 'type'], ['shell', 'chat', 'idle', 'consolidate']].
**Per-agent t2 (τ_c):** 18: 2, 21: 2, 10: 2, 26: 3, 16: 3, 27: 3, 22: 4, 24: 4, 14: 4, 13: 5, 29: 6, 6: 6, 28: 6, 25: 7, 17: 7, 20: 8, 12: 29 min (agent codes from `roster.parquet`); lab η² = 0.26 (perm p = 0.45).
**Within-period stuckness (per agent, n = 17):** ρ(t2, error share) = -0.04; ρ(t2, output rate) = -0.10; ρ(t2, idle share) = +0.33.

## Scorecard (period-specific axes)
| Axis | Evidence | Score |
| --- | --- | --- |
| B assumptions | CK max \|Δ\| 0.256 (fail); ITS rise t2(15)/t2(1) = 5.2; plateau: none; order 2 better by 0.031 nats; halves 7/8 min | 0 |
| C adequacy | MSM vs R1 ΔLL/pair +0.0397, vs M0 +0.170 (day-blocked) | 1 |
| D unfitted | t2\*/N2 = 1.22 (sets beyond sticky states: no); trimmed t2\*/N2 = 1.23 | 0 |
| G ground truth | slow set = [['browse', 'type'], ['shell', 'chat', 'idle', 'consolidate']]; 24% of idle minutes are boundary runs (scaffold/schedule) | 1 |

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods): Jev v3.1 states lumped to 6 macro states (work, inquire, fix, talk, wait = monitor_wait + idle + absent, maint), shifted estimator at τ = 5 min; covariates from real failures instead of `actions.error`. Prediction: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H17-behavior-metastable-sets/r1b/G44.json`.*

| Statistic | Round 1 (action classes) | Round 1b (v3) |
| --- | --- | --- |
| t2\* (min) | 7.5 | raw 38, bias-corrected 35, equal-n 38 |
| in-span windows / agents | – | 3024 / 18 |
| m = 2 slow split | (see Result above) | wait vs work+inquire+fix+talk+maint |
| soft CK max \|Δ\| (no power) | – | 0.020 |
| argmax MSM beats M0 and R1 (P8) | – | False |
| failure share of computer-use turns | stderr 0.105 | real 0.047 |
| mean p_blocked / output per in-span hour | – | 0.265 / 10.63 |

Reading: the v3 slowest mode here is tens of minutes; see the card for the cross-period tests (P4b-1b, P4c-1b), which failed.
