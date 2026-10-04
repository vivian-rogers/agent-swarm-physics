# H17 × G16: Choose your own goal! (2025-10-06 → 2025-10-13)

**Verdict:** mixed (CK fails)
**Role:** exploratory
**Period:** regime I · mode F (free / none) · N = 7 at start · 5 active days.

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
*Run 2026-10-03* (`analysis/run_period.py`; numbers in `data/processed/H17-behavior-metastable-sets/G16/result.json`; figure `figures/its_ck.pdf`).

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2 CK passes at τ_c (max \|Δ\| < 0.05, k ≤ 4) | max \|Δ\| = 0.108; bootstrap-significant: yes | — | fail |
| P2 ITS plateau by τ ≤ 15 min | τ\* = 2.00 | — | pass |
| P3a t2\* > N1 | t2\* = 4.1 min [3.4, 4.8] | N1 p95 3.2 | pass |
| P3b t2\* > N2 p95 and ratio ≥ 1.25 | ratio t2\*/N2 median = 1.30 | N2 median 3.1, p95 3.3; N3 median 3.0 | pass |
| P3c m ∈ {2,3}, crispness ≥ 0.75, t2/t3 ≥ 2 | m = 2, crispness 0.87, t2/t3 = 1.4 | — | fail |
| sets (m = 2 split) | [['shell', 'chat', 'idle'], ['browse', 'type', 'consolidate']] | — | descriptive |
| sets (m = 2) | [['shell', 'chat', 'idle'], ['browse', 'type', 'consolidate']] | — | descriptive |
| R1 sticky-only t2 at τ_c | t2\*/t2_R1 = 1.09 | t2_R1 = 3.8 | descriptive |
| P8 MSM beats R1 and M0 on held-out days | ΔLL/pair vs R1 = 0.0094 (5/5 folds); vs M0 = 0.0626 | — | pass |
| order 2 vs 1 (τ = 1) | ΔLL/transition = 0.0316 | — | order 2 better |
| P5 per-agent I² of ln t2 | I² = 0.45 (7 agents; block-bootstrap SEs); own/shrink beats pooled for 0.71 of agents | — | fail |
| P6 committor asymmetry max \|δ\| | 0.062 (CI excl. 0: no); cores ['idle', 'browse'] | 0 under detailed balance | descriptive |
| P7 σ(τ=1) > N2 p95; σ_macro/σ_micro < 0.5 | σ = 0.0108 nats/min; macro share 0.00 | N2 p95 0.0061 | descriptive |
| mixing time t_mix(¼) | 5 min | — | descriptive |
| R3 half-day t2\* (first / second half) | 3.1 / 5.3 | — | descriptive |
| robustness: 5-min windows (hard / soft counts / shifted = n/a) | 6.4 / 4.5 / – min | — | descriptive |
| robustness: records (≈5-min lag) | t2 ≈ 9.1 min | — | descriptive |
| stuckness covariates | error share 0.045; output 0.14/agent-h; idle share 0.26 | — | for P4b |

**Post hoc (boundary idle):** 3% of idle minutes lie in the leading/trailing idle run of an agent-day; without them t2\* = 4.0 min (N2 median 3.1), m = 2 split [['shell', 'chat', 'idle'], ['browse', 'type', 'consolidate']].
**Per-agent t2 (τ_c):** 0: 3, 11: 3, 10: 3, 12: 4, 9: 4, 5: 5, 6: 5 min (agent codes from `roster.parquet`); lab η² = 0.51 (perm p = 0.50).
**Within-period stuckness (per agent, n = 7):** ρ(t2, error share) = -0.11; ρ(t2, output rate) = +0.41; ρ(t2, idle share) = -0.61.

## Scorecard (period-specific axes)
| Axis | Evidence | Score |
| --- | --- | --- |
| B assumptions | CK max \|Δ\| 0.108 (fail); ITS rise t2(15)/t2(1) = 3.7; plateau: 2.0; order 2 better by 0.032 nats; halves 3/5 min | 0 |
| C adequacy | MSM vs R1 ΔLL/pair +0.0094, vs M0 +0.063 (day-blocked) | 2 |
| D unfitted | t2\*/N2 = 1.30 (sets beyond sticky states: yes); trimmed t2\*/N2 = 1.27 | 1 |
| G ground truth | slow set = [['shell', 'chat', 'idle'], ['browse', 'type', 'consolidate']]; 3% of idle minutes are boundary runs (scaffold/schedule) | 1 |

## Notes
