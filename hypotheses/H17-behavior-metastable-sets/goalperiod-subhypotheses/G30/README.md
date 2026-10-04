# H17 × G30: Adopt a park and get it cleaned! (2026-02-09 → 2026-02-16)

**Verdict:** failed (CK fails; t2* not beyond the sojourn null)
**Verdict (1b):** descriptive (Jev v3.1 soft-state replication; by the card's D3 rule soft P3b and the soft CK are not identifiable, so no verdict; the round-1 action-class verdict above stands)
**Role:** replication (exploratory)
**Period:** regime I · mode C (shared objective) · N = 12 at start · 5 active days.

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
- **P10 (NE10, axis E; added 2026-10-03 before running):** t2\* on 02-10 → 02-13 (nudger on) below t2\* on 02-09; one day before, so very low power. Credence 0.35.

Verdict rule (card): **supported** if CK passes, P3b holds and P8 holds; **mixed** if exactly one of CK or P3b fails; **failed** if both fail.

## Result
*Run 2026-10-03* (`analysis/run_period.py`; numbers in `data/processed/H17-behavior-metastable-sets/G30/result.json`; figure `figures/its_ck.pdf`).

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2 CK passes at τ_c (max \|Δ\| < 0.05, k ≤ 4) | max \|Δ\| = 0.145; bootstrap-significant: yes | — | fail |
| P2 ITS plateau by τ ≤ 15 min | τ\* = – | — | no plateau |
| P3a t2\* > N1 | t2\* = 6.2 min [5.4, 7.2] | N1 p95 4.7 | pass |
| P3b t2\* > N2 p95 and ratio ≥ 1.25 | ratio t2\*/N2 median = 1.24 | N2 median 5.0, p95 5.1; N3 median 3.6 | fail |
| P3c m ∈ {2,3}, crispness ≥ 0.75, t2/t3 ≥ 2 | m = 2, crispness 0.87, t2/t3 = 2.7 | — | pass |
| sets (m = 2 split) | [['shell', 'idle', 'consolidate'], ['browse', 'type', 'chat']] | — | descriptive |
| sets (m = 2) | [['shell', 'idle', 'consolidate'], ['browse', 'type', 'chat']] | — | descriptive |
| R1 sticky-only t2 at τ_c | t2\*/t2_R1 = 1.42 | t2_R1 = 4.3 | descriptive |
| P8 MSM beats R1 and M0 on held-out days | ΔLL/pair vs R1 = 0.0661 (5/5 folds); vs M0 = 0.1215 | — | pass |
| order 2 vs 1 (τ = 1) | ΔLL/transition = 0.0492 | — | order 2 better |
| P5 per-agent I² of ln t2 | I² = 0.92 (11 agents; block-bootstrap SEs); own/shrink beats pooled for 1.00 of agents | — | pass |
| P6 committor asymmetry max \|δ\| | 0.023 (CI excl. 0: yes); cores ['shell', 'browse'] | 0 under detailed balance | descriptive |
| P7 σ(τ=1) > N2 p95; σ_macro/σ_micro < 0.5 | σ = 0.0566 nats/min; macro share 0.01 | N2 p95 0.0024 | descriptive |
| mixing time t_mix(¼) | 10 min | — | descriptive |
| R3 half-day t2\* (first / second half) | 6.4 / 5.9 | — | descriptive |
| robustness: 5-min windows (hard / soft counts / shifted = n/a) | 8.8 / 6.4 / – min | — | descriptive |
| robustness: records (≈5-min lag) | t2 ≈ 9.5 min | — | descriptive |
| stuckness covariates | error share 0.064; output 2.40/agent-h; idle share 0.20 | — | for P4b |

**NE10 split at 2026-02-10:** t2\* before 5.7 min [3.5, 8.1] (11 agent-days) vs after 6.3 [5.2, 7.4] (44); difference +0.6 min, 95% CI [-2.0, +3.0]; idle share 0.17 → 0.21.
**Post hoc (boundary idle):** 3% of idle minutes lie in the leading/trailing idle run of an agent-day; without them t2\* = 6.1 min (N2 median 5.0), m = 2 split [['shell', 'idle', 'consolidate'], ['browse', 'type', 'chat']].
**Per-agent t2 (τ_c):** 0: 2, 12: 3, 6: 3, 13: 3, 17: 3, 20: 4, 10: 4, 16: 4, 15: 5, 18: 6, 14: 8 min (agent codes from `roster.parquet`); lab η² = 0.52 (perm p = 0.15).
**Within-period stuckness (per agent, n = 11):** ρ(t2, error share) = +0.85; ρ(t2, output rate) = +0.71; ρ(t2, idle share) = +0.61.

## Scorecard (period-specific axes)
| Axis | Evidence | Score |
| --- | --- | --- |
| B assumptions | CK max \|Δ\| 0.145 (fail); ITS rise t2(15)/t2(1) = 4.2; plateau: none; order 2 better by 0.049 nats; halves 6/6 min | 0 |
| C adequacy | MSM vs R1 ΔLL/pair +0.0661, vs M0 +0.122 (day-blocked) | 1 |
| D unfitted | t2\*/N2 = 1.24 (sets beyond sticky states: no); trimmed t2\*/N2 = 1.22 | 0 |
| G ground truth | slow set = [['shell', 'idle', 'consolidate'], ['browse', 'type', 'chat']]; 3% of idle minutes are boundary runs (scaffold/schedule) | 1 |

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods): Jev v3.1 states lumped to 6 macro states (work, inquire, fix, talk, wait = monitor_wait + idle + absent, maint), shifted estimator at τ = 5 min; covariates from real failures instead of `actions.error`. Prediction: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H17-behavior-metastable-sets/r1b/G30.json`.*

| Statistic | Round 1 (action classes) | Round 1b (v3) |
| --- | --- | --- |
| t2\* (min) | 6.2 | raw 36, bias-corrected 34, equal-n 36 |
| in-span windows / agents | – | 2614 / 11 |
| m = 2 slow split | (see Result above) | inquire+wait vs work+fix+talk |
| soft CK max \|Δ\| (no power) | – | 0.007 |
| argmax MSM beats M0 and R1 (P8) | – | True |
| failure share of computer-use turns | stderr 0.064 | real 0.032 |
| mean p_blocked / output per in-span hour | – | 0.267 / 2.41 |

Reading: the v3 slowest mode here is tens of minutes; see the card for the cross-period tests (P4b-1b, P4c-1b), which failed.
