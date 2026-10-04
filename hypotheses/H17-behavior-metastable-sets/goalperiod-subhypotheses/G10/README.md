# H17 × G10: Complete as many games as you can in a week! (2025-08-18 → 2025-08-25)

**Verdict:** failed (CK fails; t2* not beyond the sojourn null)
**Role:** exploratory
**Period:** regime I · mode I (each agent its own objective) · N = 7 at start · 5 active days.

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

Verdict rule (card): **supported** if CK passes, P3b holds and P8 holds; **mixed** if exactly one of CK or P3b fails; **failed** if both fail.

## Result
*Run 2026-10-03* (`analysis/run_period.py`; numbers in `data/processed/H17-behavior-metastable-sets/G10/result.json`; figure `figures/its_ck.pdf`).

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2 CK passes at τ_c (max \|Δ\| < 0.05, k ≤ 4) | max \|Δ\| = 0.205; bootstrap-significant: yes | — | fail |
| P2 ITS plateau by τ ≤ 15 min | τ\* = – | — | no plateau |
| P3a t2\* > N1 | t2\* = 5.3 min [4.5, 6.5] | N1 p95 3.9 | pass |
| P3b t2\* > N2 p95 and ratio ≥ 1.25 | ratio t2\*/N2 median = 1.23 | N2 median 4.3, p95 4.5; N3 median 3.9 | fail |
| P3c m ∈ {2,3}, crispness ≥ 0.75, t2/t3 ≥ 2 | m = 3, crispness 0.91, t2/t3 = 1.1 | — | fail |
| sets (m = 2 split) | [['idle'], ['browse', 'type', 'chat', 'consolidate']] | — | descriptive |
| sets (m = 3) | [['type'], ['idle'], ['browse', 'chat', 'consolidate']] | — | descriptive |
| R1 sticky-only t2 at τ_c | t2\*/t2_R1 = 0.96 | t2_R1 = 5.6 | descriptive |
| P8 MSM beats R1 and M0 on held-out days | ΔLL/pair vs R1 = 0.0067 (4/5 folds); vs M0 = 0.1206 | — | pass |
| order 2 vs 1 (τ = 1) | ΔLL/transition = 0.0539 | — | order 2 better |
| P5 per-agent I² of ln t2 | I² = 0.69 (7 agents; block-bootstrap SEs); own/shrink beats pooled for 0.86 of agents | — | pass |
| P6 committor asymmetry max \|δ\| | 0.022 (CI excl. 0: no); cores ['idle', 'browse'] | 0 under detailed balance | descriptive |
| P7 σ(τ=1) > N2 p95; σ_macro/σ_micro < 0.5 | σ = 0.0105 nats/min; macro share 0.04 | N2 p95 0.0042 | descriptive |
| mixing time t_mix(¼) | 10 min | — | descriptive |
| R3 half-day t2\* (first / second half) | 5.1 / 6.2 | — | descriptive |
| robustness: 5-min windows (hard / soft counts / shifted = n/a) | 9.2 / 5.5 / – min | — | descriptive |
| robustness: records (≈5-min lag) | t2 ≈ 7.4 min | — | descriptive |
| stuckness covariates | error share 0.050; output 0.00/agent-h; idle share 0.24 | — | for P4b |

**Post hoc (boundary idle):** 13% of idle minutes lie in the leading/trailing idle run of an agent-day; without them t2\* = 5.0 min (N2 median 4.0), m = 2 split [['type', 'idle'], ['browse', 'chat', 'consolidate']].
**Per-agent t2 (τ_c):** 10: 3, 9: 4, 8: 5, 11: 5, 5: 7, 0: 7, 6: 10 min (agent codes from `roster.parquet`); lab η² = 0.51 (perm p = 0.52).
**Within-period stuckness (per agent, n = 7):** ρ(t2, error share) = +0.54; ρ(t2, output rate) = n/a; ρ(t2, idle share) = -0.29.

## Scorecard (period-specific axes)
| Axis | Evidence | Score |
| --- | --- | --- |
| B assumptions | CK max \|Δ\| 0.205 (fail); ITS rise t2(15)/t2(1) = 5.9; plateau: none; order 2 better by 0.054 nats; halves 5/6 min | 0 |
| C adequacy | MSM vs R1 ΔLL/pair +0.0067, vs M0 +0.121 (day-blocked) | 1 |
| D unfitted | t2\*/N2 = 1.23 (sets beyond sticky states: no); trimmed t2\*/N2 = 1.23 | 0 |
| G ground truth | slow set = [['idle'], ['browse', 'type', 'chat', 'consolidate']]; 13% of idle minutes are boundary runs (scaffold/schedule) | 1 |

## Notes
