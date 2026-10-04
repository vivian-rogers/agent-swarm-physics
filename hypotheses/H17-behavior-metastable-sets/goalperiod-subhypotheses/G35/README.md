# H17 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 2026-03-23)

**Verdict:** failed (CK fails; t2* not beyond the sojourn null)
**Verdict (1b):** descriptive (Jev v3.1 soft-state replication; by the card's D3 rule soft P3b and the soft CK are not identifiable, so no verdict; the round-1 action-class verdict above stands)
**Role:** exploratory
**Period:** regime II · mode C (shared objective) · N = 13 at start · 5 active days.

## Why this period
Regime II (rooms + discrete sessions): comparison period between regimes I and III (descriptive for P4c).

## Prediction
*Written 2026-10-03, before running on this period.* The card's predictions (`../../README.md`, "Prediction") as they apply here; states = H14 coarse 6-state minute grid, pooled MSM over present agent-days, τ_c = 5 min:
- **CK (P2):** the crisp-set CK test passes at τ_c = 5 min (max |Δ| < 0.05 for k ≤ 4).
- **P3b (sets beyond sticky states):** t2\* above the N2 sojourn-null 95th percentile and t2\*/median(N2) ≥ 1.25.
- **P8:** the MSM beats R1 (sticky-only) and M0 on held-out days at τ_c.
- **P3a:** t2\* above the N1 shuffled floor.
- **P5:** per-agent I² of ln t2 ≥ 0.5 (if ≥ 3 agents qualify).
- **P4c (regime part):** t2\* above the median of the regime-III periods (session on/off makes a slow two-set process).
- **Regime-I set identity (credence 0.6):** the m = 2 split separates in-session computer work (browse/type/shell) from out-of-session states (chat/idle/session events).

Verdict rule (card): **supported** if CK passes, P3b holds and P8 holds; **mixed** if exactly one of CK or P3b fails; **failed** if both fail.

## Result
*Run 2026-10-03* (`analysis/run_period.py`; numbers in `data/processed/H17-behavior-metastable-sets/G35/result.json`; figure `figures/its_ck.pdf`).

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2 CK passes at τ_c (max \|Δ\| < 0.05, k ≤ 4) | max \|Δ\| = 0.103; bootstrap-significant: yes | — | fail |
| P2 ITS plateau by τ ≤ 15 min | τ\* = – | — | no plateau |
| P3a t2\* > N1 | t2\* = 4.2 min [3.5, 4.9] | N1 p95 3.2 | pass |
| P3b t2\* > N2 p95 and ratio ≥ 1.25 | ratio t2\*/N2 median = 1.23 | N2 median 3.4, p95 3.5; N3 median 2.6 | fail |
| P3c m ∈ {2,3}, crispness ≥ 0.75, t2/t3 ≥ 2 | m = 2, crispness 0.87, t2/t3 = 1.9 | — | fail |
| sets (m = 2 split) | [['shell', 'idle', 'consolidate'], ['browse', 'type', 'chat']] | — | descriptive |
| sets (m = 2) | [['shell', 'idle', 'consolidate'], ['browse', 'type', 'chat']] | — | descriptive |
| R1 sticky-only t2 at τ_c | t2\*/t2_R1 = 1.15 | t2_R1 = 3.6 | descriptive |
| P8 MSM beats R1 and M0 on held-out days | ΔLL/pair vs R1 = 0.0266 (5/5 folds); vs M0 = 0.0578 | — | pass |
| order 2 vs 1 (τ = 1) | ΔLL/transition = 0.0266 | — | order 2 better |
| P5 per-agent I² of ln t2 | I² = 0.72 (12 agents; block-bootstrap SEs); own/shrink beats pooled for 1.00 of agents | — | pass |
| P6 committor asymmetry max \|δ\| | 0.029 (CI excl. 0: no); cores ['shell', 'browse'] | 0 under detailed balance | descriptive |
| P7 σ(τ=1) > N2 p95; σ_macro/σ_micro < 0.5 | σ = 0.1096 nats/min; macro share 0.02 | N2 p95 0.0025 | descriptive |
| mixing time t_mix(¼) | 5 min | — | descriptive |
| R3 half-day t2\* (first / second half) | 4.3 / 4.0 | — | descriptive |
| robustness: 5-min windows (hard / soft counts / shifted = n/a) | 5.7 / 4.6 / – min | — | descriptive |
| robustness: records (≈5-min lag) | t2 ≈ 6.1 min | — | descriptive |
| stuckness covariates | error share 0.064; output 2.87/agent-h; idle share 0.17 | — | for P4b |

**Post hoc (boundary idle):** 4% of idle minutes lie in the leading/trailing idle run of an agent-day; without them t2\* = 4.2 min (N2 median 3.4), m = 2 split [['shell', 'idle', 'consolidate'], ['browse', 'type', 'chat']].
**Per-agent t2 (τ_c):** 23: 2, 12: 2, 13: 3, 14: 3, 16: 3, 20: 3, 21: 4, 22: 4, 17: 4, 18: 4, 6: 4, 10: 5 min (agent codes from `roster.parquet`); lab η² = 0.33 (perm p = 0.34).
**Within-period stuckness (per agent, n = 12):** ρ(t2, error share) = +0.45; ρ(t2, output rate) = -0.02; ρ(t2, idle share) = +0.08.

## Scorecard (period-specific axes)
| Axis | Evidence | Score |
| --- | --- | --- |
| B assumptions | CK max \|Δ\| 0.103 (fail); ITS rise t2(15)/t2(1) = 4.3; plateau: none; order 2 better by 0.027 nats; halves 4/4 min | 0 |
| C adequacy | MSM vs R1 ΔLL/pair +0.0266, vs M0 +0.058 (day-blocked) | 1 |
| D unfitted | t2\*/N2 = 1.23 (sets beyond sticky states: no); trimmed t2\*/N2 = 1.23 | 0 |
| G ground truth | slow set = [['shell', 'idle', 'consolidate'], ['browse', 'type', 'chat']]; 4% of idle minutes are boundary runs (scaffold/schedule) | 1 |

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods): Jev v3.1 states lumped to 6 macro states (work, inquire, fix, talk, wait = monitor_wait + idle + absent, maint), shifted estimator at τ = 5 min; covariates from real failures instead of `actions.error`. Prediction: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H17-behavior-metastable-sets/r1b/G35.json`.*

| Statistic | Round 1 (action classes) | Round 1b (v3) |
| --- | --- | --- |
| t2\* (min) | 4.2 | raw 43, bias-corrected 41, equal-n 43 |
| in-span windows / agents | – | 2856 / 12 |
| m = 2 slow split | (see Result above) | wait vs work+inquire+fix+talk |
| soft CK max \|Δ\| (no power) | – | 0.028 |
| argmax MSM beats M0 and R1 (P8) | – | True |
| failure share of computer-use turns | stderr 0.064 | real 0.025 |
| mean p_blocked / output per in-span hour | – | 0.220 / 2.86 |

Reading: the v3 slowest mode here is tens of minutes; see the card for the cross-period tests (P4b-1b, P4c-1b), which failed.
