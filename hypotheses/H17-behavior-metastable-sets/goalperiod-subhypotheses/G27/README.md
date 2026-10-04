# H17 × G27: Hack the OWASP Juice Shop hacking playground. Compete to see which agent can complete the most challenges (2026-01-12 → 2026-01-26)

**Verdict:** mixed (CK fails)
**Role:** exploratory
**Period:** regime I · mode K (competition) · N = 10 at start · 10 active days.

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
*Run 2026-10-03* (`analysis/run_period.py`; numbers in `data/processed/H17-behavior-metastable-sets/G27/result.json`; figure `figures/its_ck.pdf`).

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2 CK passes at τ_c (max \|Δ\| < 0.05, k ≤ 4) | max \|Δ\| = 0.192; bootstrap-significant: yes | — | fail |
| P2 ITS plateau by τ ≤ 15 min | τ\* = – | — | no plateau |
| P3a t2\* > N1 | t2\* = 6.2 min [5.5, 6.9] | N1 p95 4.5 | pass |
| P3b t2\* > N2 p95 and ratio ≥ 1.25 | ratio t2\*/N2 median = 1.26 | N2 median 4.9, p95 5.0; N3 median 3.6 | pass |
| P3c m ∈ {2,3}, crispness ≥ 0.75, t2/t3 ≥ 2 | m = 2, crispness 0.88, t2/t3 = 1.9 | — | fail |
| sets (m = 2 split) | [['browse', 'type'], ['shell', 'chat', 'idle', 'consolidate']] | — | descriptive |
| sets (m = 2) | [['browse', 'type'], ['shell', 'chat', 'idle', 'consolidate']] | — | descriptive |
| R1 sticky-only t2 at τ_c | t2\*/t2_R1 = 1.48 | t2_R1 = 4.2 | descriptive |
| P8 MSM beats R1 and M0 on held-out days | ΔLL/pair vs R1 = 0.0485 (5/5 folds); vs M0 = 0.1212 | — | pass |
| order 2 vs 1 (τ = 1) | ΔLL/transition = 0.0434 | — | order 2 better |
| P5 per-agent I² of ln t2 | I² = 0.92 (10 agents; block-bootstrap SEs); own/shrink beats pooled for 1.00 of agents | — | pass |
| P6 committor asymmetry max \|δ\| | 0.016 (CI excl. 0: yes); cores ['type', 'shell'] | 0 under detailed balance | descriptive |
| P7 σ(τ=1) > N2 p95; σ_macro/σ_micro < 0.5 | σ = 0.0867 nats/min; macro share 0.02 | N2 p95 0.0014 | descriptive |
| mixing time t_mix(¼) | 10 min | — | descriptive |
| R3 half-day t2\* (first / second half) | 6.1 / 6.3 | — | descriptive |
| robustness: 5-min windows (hard / soft counts / shifted = n/a) | 8.8 / 6.6 / – min | — | descriptive |
| robustness: records (≈5-min lag) | t2 ≈ 9.5 min | — | descriptive |
| stuckness covariates | error share 0.071; output 0.23/agent-h; idle share 0.30 | — | for P4b |

**Post hoc (boundary idle):** 3% of idle minutes lie in the leading/trailing idle run of an agent-day; without them t2\* = 6.2 min (N2 median 5.0), m = 2 split [['browse', 'type'], ['shell', 'chat', 'idle', 'consolidate']].
**Per-agent t2 (τ_c):** 17: 3, 12: 3, 13: 3, 10: 4, 16: 4, 15: 5, 0: 6, 18: 6, 6: 7, 14: 8 min (agent codes from `roster.parquet`); lab η² = 0.57 (perm p = 0.13).
**Within-period stuckness (per agent, n = 10):** ρ(t2, error share) = +0.41; ρ(t2, output rate) = +0.53; ρ(t2, idle share) = +0.16.

## Scorecard (period-specific axes)
| Axis | Evidence | Score |
| --- | --- | --- |
| B assumptions | CK max \|Δ\| 0.192 (fail); ITS rise t2(15)/t2(1) = 4.8; plateau: none; order 2 better by 0.043 nats; halves 6/6 min | 0 |
| C adequacy | MSM vs R1 ΔLL/pair +0.0485, vs M0 +0.121 (day-blocked) | 2 |
| D unfitted | t2\*/N2 = 1.26 (sets beyond sticky states: yes); trimmed t2\*/N2 = 1.25 | 1 |
| G ground truth | slow set = [['browse', 'type'], ['shell', 'chat', 'idle', 'consolidate']]; 3% of idle minutes are boundary runs (scaffold/schedule) | 1 |

## Notes
