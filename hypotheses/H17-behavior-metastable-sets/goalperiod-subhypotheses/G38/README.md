# H17 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-27)

**Verdict:** failed (CK fails; t2* not beyond the sojourn null)
**Verdict (1b):** descriptive (Jev v3.1 soft-state replication; by the card's D3 rule soft P3b and the soft CK are not identifiable, so no verdict; the round-1 action-class verdict above stands)
**Role:** replication (exploratory)
**Period:** regime III · mode C (shared objective) · N = 12 at start · 17 active days.

## Why this period
Longest 4-h regime-III period (17 days): the most power of the 4-h periods. Outreach approval (G) arrives on 04-14 inside the period (descriptive only, no prediction).

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
- **NE17 split (04-14):** descriptive, no prediction.

Verdict rule (card): **supported** if CK passes, P3b holds and P8 holds; **mixed** if exactly one of CK or P3b fails; **failed** if both fail.

## Result
*Run 2026-10-03* (`analysis/run_period.py`; numbers in `data/processed/H17-behavior-metastable-sets/G38/result.json`; figure `figures/its_ck.pdf`).

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2 CK passes at τ_c (max \|Δ\| < 0.05, k ≤ 4) | max \|Δ\| = 0.174; bootstrap-significant: yes | — | fail |
| P2 ITS plateau by τ ≤ 15 min | τ\* = – | — | no plateau |
| P3a t2\* > N1 | t2\* = 10.1 min [9.0, 11.2] | N1 p95 6.8 | pass |
| P3b t2\* > N2 and ratio ≥ 1.25 (400 surrogates, Holm across the 8 regime-III periods) | ratio t2\*/N2 median = 1.16; Holm p = 0.020 | N2 median 8.7; N3 median 5.7 | fail |
| P3c m ∈ {2,3}, crispness ≥ 0.75, t2/t3 ≥ 2 | m = 2, crispness 0.80, t2/t3 = 2.0 | — | pass |
| sets (m = 2 split) | [['browse', 'type', 'consolidate'], ['shell', 'chat', 'idle']] | — | idle alone/with consolidate: no |
| sets (m = 2) | [['browse', 'type', 'consolidate'], ['shell', 'chat', 'idle']] | — | descriptive |
| R1 sticky-only t2 at τ_c | t2\*/t2_R1 = 1.33 | t2_R1 = 7.6 | descriptive |
| P8 MSM beats R1 and M0 on held-out days | ΔLL/pair vs R1 = 0.0655 (5/5 folds); vs M0 = 0.2759 | — | pass |
| order 2 vs 1 (τ = 1) | ΔLL/transition = 0.0706 | — | order 2 better |
| P5 per-agent I² of ln t2 | I² = 0.78 (14 agents; block-bootstrap SEs); own/shrink beats pooled for 1.00 of agents | — | pass |
| P6 committor asymmetry max \|δ\| | 0.037 (CI excl. 0: yes); cores ['type', 'idle'] | 0 under detailed balance | fail |
| P7 σ(τ=1) > N2 p95; σ_macro/σ_micro < 0.5 | σ = 0.0087 nats/min; macro share 0.03 | N2 p95 0.0009 | pass |
| mixing time t_mix(¼) | 10 min | — | descriptive |
| R3 half-day t2\* (first / second half) | 11.0 / 9.5 | — | descriptive |
| robustness: 5-min windows (hard / soft counts / shifted = n/a) | 12.7 / 10.5 / – min | — | descriptive |
| robustness: records (≈5-min lag) | t2 ≈ 14.5 min | — | descriptive |
| stuckness covariates | error share 0.058; output 2.07/agent-h; idle share 0.22 | — | for P4b |

**NE17 split at 2026-04-14:** t2\* before 9.0 min [8.0, 10.1] (96 agent-days) vs after 10.5 [9.3, 12.2] (115); difference +1.5 min, 95% CI [-0.1, +3.6]; idle share 0.15 → 0.28.
**Post hoc (boundary idle):** 35% of idle minutes lie in the leading/trailing idle run of an agent-day; without them t2\* = 8.7 min (N2 median 7.6), m = 2 split [['browse', 'type'], ['shell', 'chat', 'idle', 'consolidate']].
**Per-agent t2 (τ_c):** 21: 5, 20: 6, 13: 6, 18: 7, 24: 7, 23: 7, 17: 8, 10: 8, 25: 10, 14: 10, 22: 10, 6: 21, 12: 34, 16: 53 min (agent codes from `roster.parquet`); lab η² = 0.10 (perm p = 0.90).
**Within-period stuckness (per agent, n = 14):** ρ(t2, error share) = -0.44; ρ(t2, output rate) = -0.24; ρ(t2, idle share) = -0.42.

## Scorecard (period-specific axes)
| Axis | Evidence | Score |
| --- | --- | --- |
| B assumptions | CK max \|Δ\| 0.174 (fail); ITS rise t2(15)/t2(1) = 6.8; plateau: none; order 2 better by 0.071 nats; halves 11/9 min | 0 |
| C adequacy | MSM vs R1 ΔLL/pair +0.0655, vs M0 +0.276 (day-blocked) | 1 |
| D unfitted | t2\*/N2 = 1.16 (sets beyond sticky states: no); trimmed t2\*/N2 = 1.16 | 0 |
| G ground truth | slow set = [['browse', 'type', 'consolidate'], ['shell', 'chat', 'idle']]; 35% of idle minutes are boundary runs (scaffold/schedule) | 1 |

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods): Jev v3.1 states lumped to 6 macro states (work, inquire, fix, talk, wait = monitor_wait + idle + absent, maint), shifted estimator at τ = 5 min; covariates from real failures instead of `actions.error`. Prediction: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H17-behavior-metastable-sets/r1b/G38.json`.*

| Statistic | Round 1 (action classes) | Round 1b (v3) |
| --- | --- | --- |
| t2\* (min) | 10.1 | raw 230, bias-corrected 230, equal-n 231 |
| in-span windows / agents | – | 9960 / 14 |
| m = 2 slow split | (see Result above) | wait vs work+inquire+fix+talk+maint |
| soft CK max \|Δ\| (no power) | – | 0.017 |
| argmax MSM beats M0 and R1 (P8) | – | True |
| failure share of computer-use turns | stderr 0.058 | real 0.030 |
| mean p_blocked / output per in-span hour | – | 0.247 / 2.85 |

Reading: the v3 slowest mode here is hour-scale (agent-day mixture, R2/R3); see the card for the cross-period tests (P4b-1b, P4c-1b), which failed.
