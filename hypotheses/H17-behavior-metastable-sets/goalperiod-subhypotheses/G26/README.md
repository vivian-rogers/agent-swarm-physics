# H17 × G26: Elect a village leader. They choose this week’s goal! (2026-01-05 → 2026-01-12)

**Verdict:** failed (CK fails; t2* not beyond the sojourn null)
**Role:** exploratory
**Period:** regime I · mode C (shared objective) · N = 10 at start · 5 active days.

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
*Run 2026-10-03* (`analysis/run_period.py`; numbers in `data/processed/H17-behavior-metastable-sets/G26/result.json`; figure `figures/its_ck.pdf`).

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2 CK passes at τ_c (max \|Δ\| < 0.05, k ≤ 4) | max \|Δ\| = 0.116; bootstrap-significant: yes | — | fail |
| P2 ITS plateau by τ ≤ 15 min | τ\* = 2.00 | — | pass |
| P3a t2\* > N1 | t2\* = 5.1 min [4.3, 5.9] | N1 p95 3.5 | pass |
| P3b t2\* > N2 p95 and ratio ≥ 1.25 | ratio t2\*/N2 median = 1.23 | N2 median 4.2, p95 4.3; N3 median 3.8 | fail |
| P3c m ∈ {2,3}, crispness ≥ 0.75, t2/t3 ≥ 2 | m = 2, crispness 0.84, t2/t3 = 2.0 | — | fail |
| sets (m = 2 split) | [['browse', 'type', 'consolidate'], ['shell', 'chat', 'idle']] | — | descriptive |
| sets (m = 2) | [['browse', 'type', 'consolidate'], ['shell', 'chat', 'idle']] | — | descriptive |
| R1 sticky-only t2 at τ_c | t2\*/t2_R1 = 1.22 | t2_R1 = 4.2 | descriptive |
| P8 MSM beats R1 and M0 on held-out days | ΔLL/pair vs R1 = 0.0232 (5/5 folds); vs M0 = 0.1025 | — | pass |
| order 2 vs 1 (τ = 1) | ΔLL/transition = 0.0518 | — | order 2 better |
| P5 per-agent I² of ln t2 | I² = 0.89 (10 agents; block-bootstrap SEs); own/shrink beats pooled for 0.90 of agents | — | pass |
| P6 committor asymmetry max \|δ\| | 0.026 (CI excl. 0: no); cores ['type', 'shell'] | 0 under detailed balance | descriptive |
| P7 σ(τ=1) > N2 p95; σ_macro/σ_micro < 0.5 | σ = 0.0255 nats/min; macro share 0.30 | N2 p95 0.0037 | descriptive |
| mixing time t_mix(¼) | 5 min | — | descriptive |
| R3 half-day t2\* (first / second half) | 5.3 / 5.1 | — | descriptive |
| robustness: 5-min windows (hard / soft counts / shifted = n/a) | 6.5 / 5.4 / – min | — | descriptive |
| robustness: records (≈5-min lag) | t2 ≈ 8.4 min | — | descriptive |
| stuckness covariates | error share 0.040; output 0.00/agent-h; idle share 0.34 | — | for P4b |

**Post hoc (boundary idle):** 8% of idle minutes lie in the leading/trailing idle run of an agent-day; without them t2\* = 5.0 min (N2 median 4.0), m = 2 split [['shell', 'chat', 'idle'], ['browse', 'type', 'consolidate']].
**Per-agent t2 (τ_c):** 14: 2, 17: 2, 12: 3, 16: 4, 15: 4, 10: 4, 13: 5, 18: 6, 6: 6, 0: 8 min (agent codes from `roster.parquet`); lab η² = 0.39 (perm p = 0.38).
**Within-period stuckness (per agent, n = 10):** ρ(t2, error share) = +0.36; ρ(t2, output rate) = n/a; ρ(t2, idle share) = -0.05.

## Scorecard (period-specific axes)
| Axis | Evidence | Score |
| --- | --- | --- |
| B assumptions | CK max \|Δ\| 0.116 (fail); ITS rise t2(15)/t2(1) = 3.4; plateau: 2.0; order 2 better by 0.052 nats; halves 5/5 min | 0 |
| C adequacy | MSM vs R1 ΔLL/pair +0.0232, vs M0 +0.103 (day-blocked) | 1 |
| D unfitted | t2\*/N2 = 1.23 (sets beyond sticky states: no); trimmed t2\*/N2 = 1.25 | 0 |
| G ground truth | slow set = [['browse', 'type', 'consolidate'], ['shell', 'chat', 'idle']]; 8% of idle minutes are boundary runs (scaffold/schedule) | 1 |

## Notes
