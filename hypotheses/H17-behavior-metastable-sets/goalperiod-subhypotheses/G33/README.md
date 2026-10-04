# H17 × G33: Discuss, debate, and act on your views about the recent Pentagon-AI company news (2026-03-02 → 2026-03-05)

**Verdict:** mixed (CK fails)
**Verdict (1b):** descriptive (Jev v3.1 soft-state replication; by the card's D3 rule soft P3b and the soft CK are not identifiable, so no verdict; the round-1 action-class verdict above stands)
**Role:** replication (exploratory)
**Period:** regime II · mode C (shared objective) · N = 12 at start · 3 active days.

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
*Run 2026-10-03* (`analysis/run_period.py`; numbers in `data/processed/H17-behavior-metastable-sets/G33/result.json`; figure `figures/its_ck.pdf`).

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2 CK passes at τ_c (max \|Δ\| < 0.05, k ≤ 4) | max \|Δ\| = 0.168; bootstrap-significant: yes | — | fail |
| P2 ITS plateau by τ ≤ 15 min | τ\* = – | — | no plateau |
| P3a t2\* > N1 | t2\* = 6.2 min [5.3, 7.3] | N1 p95 3.6 | pass |
| P3b t2\* > N2 p95 and ratio ≥ 1.25 | ratio t2\*/N2 median = 1.44 | N2 median 4.3, p95 4.5; N3 median 3.9 | pass |
| P3c m ∈ {2,3}, crispness ≥ 0.75, t2/t3 ≥ 2 | m = 2, crispness 0.91, t2/t3 = 2.1 | — | pass |
| sets (m = 2 split) | [['browse', 'type'], ['shell', 'chat', 'idle', 'consolidate']] | — | descriptive |
| sets (m = 2) | [['browse', 'type'], ['shell', 'chat', 'idle', 'consolidate']] | — | descriptive |
| R1 sticky-only t2 at τ_c | t2\*/t2_R1 = 1.35 | t2_R1 = 4.6 | descriptive |
| P8 MSM beats R1 and M0 on held-out days | ΔLL/pair vs R1 = 0.0357 (3/3 folds); vs M0 = 0.1039 | — | pass |
| order 2 vs 1 (τ = 1) | ΔLL/transition = 0.0385 | — | order 2 better |
| P5 per-agent I² of ln t2 | I² = 0.81 (11 agents; block-bootstrap SEs); own/shrink beats pooled for 0.82 of agents | — | pass |
| P6 committor asymmetry max \|δ\| | 0.020 (CI excl. 0: no); cores ['browse', 'shell'] | 0 under detailed balance | descriptive |
| P7 σ(τ=1) > N2 p95; σ_macro/σ_micro < 0.5 | σ = 0.0711 nats/min; macro share 0.00 | N2 p95 0.0044 | descriptive |
| mixing time t_mix(¼) | 10 min | — | descriptive |
| R3 half-day t2\* (first / second half) | 6.0 / 6.2 | — | descriptive |
| robustness: 5-min windows (hard / soft counts / shifted = n/a) | 8.3 / 6.4 / – min | — | descriptive |
| robustness: records (≈5-min lag) | t2 ≈ 9.9 min | — | descriptive |
| stuckness covariates | error share 0.122; output 6.18/agent-h; idle share 0.30 | — | for P4b |

**Post hoc (boundary idle):** 8% of idle minutes lie in the leading/trailing idle run of an agent-day; without them t2\* = 6.2 min (N2 median 4.2), m = 2 split [['browse', 'type'], ['shell', 'chat', 'idle', 'consolidate']].
**Per-agent t2 (τ_c):** 18: 2, 17: 3, 12: 3, 13: 4, 21: 4, 6: 4, 10: 6, 20: 6, 14: 7, 15: 7, 16: 8 min (agent codes from `roster.parquet`); lab η² = 0.14 (perm p = 0.75).
**Within-period stuckness (per agent, n = 11):** ρ(t2, error share) = +0.19; ρ(t2, output rate) = +0.11; ρ(t2, idle share) = -0.22.

## Scorecard (period-specific axes)
| Axis | Evidence | Score |
| --- | --- | --- |
| B assumptions | CK max \|Δ\| 0.168 (fail); ITS rise t2(15)/t2(1) = 3.7; plateau: none; order 2 better by 0.039 nats; halves 6/6 min | 0 |
| C adequacy | MSM vs R1 ΔLL/pair +0.0357, vs M0 +0.104 (day-blocked) | 2 |
| D unfitted | t2\*/N2 = 1.44 (sets beyond sticky states: yes); trimmed t2\*/N2 = 1.46 | 1 |
| G ground truth | slow set = [['browse', 'type'], ['shell', 'chat', 'idle', 'consolidate']]; 8% of idle minutes are boundary runs (scaffold/schedule) | 1 |

## Notes

## Round 1b (improved data, 2026-10-04)
*Replication layer (templated across periods): Jev v3.1 states lumped to 6 macro states (work, inquire, fix, talk, wait = monitor_wait + idle + absent, maint), shifted estimator at τ = 5 min; covariates from real failures instead of `actions.error`. Prediction: the card's "Round 1b" predictions as they apply here. Numbers: `data/processed/H17-behavior-metastable-sets/r1b/G33.json`.*

| Statistic | Round 1 (action classes) | Round 1b (v3) |
| --- | --- | --- |
| t2\* (min) | 6.2 | raw 32, bias-corrected 23, equal-n 32 |
| in-span windows / agents | – | 1548 / 11 |
| m = 2 slow split | (see Result above) | wait vs work+inquire+fix+talk+maint |
| soft CK max \|Δ\| (no power) | – | 0.013 |
| argmax MSM beats M0 and R1 (P8) | – | False |
| failure share of computer-use turns | stderr 0.122 | real 0.051 |
| mean p_blocked / output per in-span hour | – | 0.257 / 6.13 |

Reading: the v3 slowest mode here is tens of minutes; see the card for the cross-period tests (P4b-1b, P4c-1b), which failed.
