# H17 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-20)

**Verdict:** mixed (CK fails)
**Verdict (1b):** descriptive (Jev v3.1 soft-state replication; by the card's D3 rule soft P3b and the soft CK are not identifiable, so no verdict; the round-1 action-class verdict above stands)
**Role:** replication (exploratory)
**Period:** regime III · mode I/K (individual roles, some competing) · N = 21 at start · 55 active days (non-holdout days 07-06 → 09-04 only; the #51 tail is held out).

## Why this period
The longest stationary-ish window (45 non-holdout days, 8 h/day, 21 → 32 agents): the most power for per-agent MSMs, and the only period where weekly blocks can measure within-period drift of t2* (O10) against the between-period spread (P4a).

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
- **O10/P4a:** the between-week CV of t2\* inside #51 is smaller than the between-period CV of the regime-III periods.
- **NE32 (07-09) and NE33 (09-03/04) inside the window:** not split; weekly blocks (O10) show any drift.

Verdict rule (card): **supported** if CK passes, P3b holds and P8 holds; **mixed** if exactly one of CK or P3b fails; **failed** if both fail.

## Result
*Run 2026-10-03* (`analysis/run_period.py`; numbers in `data/processed/H17-behavior-metastable-sets/G51/result.json`; figure `figures/its_ck.pdf`).

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2 CK passes at τ_c (max \|Δ\| < 0.05, k ≤ 4) | max \|Δ\| = 0.208; bootstrap-significant: yes | — | fail |
| P2 ITS plateau by τ ≤ 15 min | τ\* = – | — | no plateau |
| P3a t2\* > N1 | t2\* = 11.7 min [11.2, 12.4] | N1 p95 5.7 | pass |
| P3b t2\* > N2 and ratio ≥ 1.25 (400 surrogates, Holm across the 8 regime-III periods) | ratio t2\*/N2 median = 1.26; Holm p = 0.020 | N2 median 9.4; N3 median 7.6 | pass |
| P3c m ∈ {2,3}, crispness ≥ 0.75, t2/t3 ≥ 2 | m = 2, crispness 0.81, t2/t3 = 2.0 | — | pass |
| sets (m = 2 split) | [['browse', 'type', 'shell', 'chat', 'consolidate'], ['idle']] | — | idle alone/with consolidate: yes |
| sets (m = 2) | [['browse', 'type', 'shell', 'chat', 'consolidate'], ['idle']] | — | descriptive |
| R1 sticky-only t2 at τ_c | t2\*/t2_R1 = 1.12 | t2_R1 = 10.5 | descriptive |
| P8 MSM beats R1 and M0 on held-out days | ΔLL/pair vs R1 = 0.0333 (5/5 folds); vs M0 = 0.3037 | — | pass |
| order 2 vs 1 (τ = 1) | ΔLL/transition = 0.0472 | — | order 2 better |
| P5 per-agent I² of ln t2 | I² = 0.99 (31 agents; block-bootstrap SEs); own/shrink beats pooled for 0.94 of agents | — | pass |
| P6 committor asymmetry max \|δ\| | 0.010 (CI excl. 0: yes); cores ['browse', 'idle'] | 0 under detailed balance | fail |
| P7 σ(τ=1) > N2 p95; σ_macro/σ_micro < 0.5 | σ = 0.0017 nats/min; macro share 0.07 | N2 p95 0.0001 | pass |
| mixing time t_mix(¼) | 15 min | — | descriptive |
| R3 half-day t2\* (first / second half) | 12.3 / 11.2 | — | descriptive |
| robustness: 5-min windows (hard / soft counts / shifted = n/a) | 15.8 / 12.4 / – min | — | descriptive |
| robustness: records (≈5-min lag) | t2 ≈ 13.6 min | — | descriptive |
| stuckness covariates | error share 0.058; output 4.13/agent-h; idle share 0.40 | — | for P4b |

**Weekly blocks (O10):** 2026-07-06: 16.8 min; 2026-07-13: 11.6 min; 2026-07-20: 11.1 min; 2026-07-27: 12.6 min; 2026-08-03: 10.0 min; 2026-08-10: 10.4 min; 2026-08-17: 11.1 min; 2026-08-24: 12.9 min; 2026-08-31: 10.9 min. Between-week CV 0.17 vs between-period CV (regime III) 0.55.
**Post hoc (boundary idle):** 19% of idle minutes lie in the leading/trailing idle run of an agent-day; without them t2\* = 10.8 min (N2 median 8.5), m = 2 split [['browse', 'type', 'chat', 'consolidate'], ['shell', 'idle']].
**Per-agent t2 (τ_c):** 43: 3, 40: 4, 35: 4, 37: 4, 33: 5, 23: 5, 29: 6, 21: 6, 17: 7, 26: 7, 14: 7, 31: 7, 44: 7, 38: 7, 10: 7, 36: 8, 18: 8, 41: 8, 27: 9, 34: 9, 6: 10, 32: 11, 42: 11, 22: 12, 24: 12, 39: 17, 25: 19, 13: 19, 20: 22, 16: 27, 12: 43 min (agent codes from `roster.parquet`); lab η² = 0.40 (perm p = 0.08).
**Within-period stuckness (per agent, n = 31):** ρ(t2, error share) = -0.35; ρ(t2, output rate) = -0.44; ρ(t2, idle share) = -0.11.

## Scorecard (period-specific axes)
| Axis | Evidence | Score |
| --- | --- | --- |
| B assumptions | CK max \|Δ\| 0.208 (fail); ITS rise t2(15)/t2(1) = 5.1; plateau: none; order 2 better by 0.047 nats; halves 12/11 min | 0 |
| C adequacy | MSM vs R1 ΔLL/pair +0.0333, vs M0 +0.304 (day-blocked) | 2 |
| D unfitted | t2\*/N2 = 1.26 (sets beyond sticky states: yes); trimmed t2\*/N2 = 1.28 | 1 |
| G ground truth | slow set = [['browse', 'type', 'shell', 'chat', 'consolidate'], ['idle']]; 19% of idle minutes are boundary runs (scaffold/schedule) | 1 |

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods): Jev v3.1 states lumped to 6 macro states (work, inquire, fix, talk, wait = monitor_wait + idle + absent, maint), shifted estimator at τ = 5 min; covariates from real failures instead of `actions.error`. Prediction: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H17-behavior-metastable-sets/r1b/G51.json`.*

| Statistic | Round 1 (action classes) | Round 1b (v3) |
| --- | --- | --- |
| t2\* (min) | 11.7 | raw 268, bias-corrected 263, equal-n 160 |
| in-span windows / agents | – | 109165 / 32 |
| m = 2 slow split | (see Result above) | wait vs work+inquire+fix+talk+maint |
| soft CK max \|Δ\| (no power) | – | 0.021 |
| argmax MSM beats M0 and R1 (P8) | – | True |
| failure share of computer-use turns | stderr 0.058 | real 0.027 |
| mean p_blocked / output per in-span hour | – | 0.249 / 5.97 |

Reading: the v3 slowest mode here is hour-scale (agent-day mixture, R2/R3); see the card for the cross-period tests (P4b-1b, P4c-1b), which failed.
