# H17 × G37: Pick your own goal! (2026-03-30 → 2026-04-02)

**Verdict:** failed (CK fails; t2* not beyond the sojourn null; MSM does not beat R1/M0)
**Role:** exploratory
**Period:** regime III · mode F (free / none) · N = 13 at start · 3 active days.

## Why this period
First regime-III period and a free-choice period: the undriven reference for P4d.

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
- **P4d:** this free-choice period is not the fastest (smallest t2\*) of its regime. Descriptive.

Verdict rule (card): **supported** if CK passes, P3b holds and P8 holds; **mixed** if exactly one of CK or P3b fails; **failed** if both fail.

## Result
*Run 2026-10-03* (`analysis/run_period.py`; numbers in `data/processed/H17-behavior-metastable-sets/G37/result.json`; figure `figures/its_ck.pdf`).

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P2 CK passes at τ_c (max \|Δ\| < 0.05, k ≤ 4) | max \|Δ\| = 0.182; bootstrap-significant: yes | — | fail |
| P2 ITS plateau by τ ≤ 15 min | τ\* = – | — | no plateau |
| P3a t2\* > N1 | t2\* = 23.5 min [17.2, 30.0] | N1 p95 5.5 | pass |
| P3b t2\* > N2 and ratio ≥ 1.25 (400 surrogates, Holm across the 8 regime-III periods) | ratio t2\*/N2 median = 1.19; Holm p = 0.020 | N2 median 19.7; N3 median 15.7 | fail |
| P3c m ∈ {2,3}, crispness ≥ 0.75, t2/t3 ≥ 2 | m = 2, crispness 0.94, t2/t3 = 5.1 | — | pass |
| sets (m = 2 split) | [['browse', 'type', 'shell', 'chat', 'consolidate'], ['idle']] | — | idle alone/with consolidate: yes |
| sets (m = 2) | [['browse', 'type', 'shell', 'chat', 'consolidate'], ['idle']] | — | descriptive |
| R1 sticky-only t2 at τ_c | t2\*/t2_R1 = 1.11 | t2_R1 = 21.2 | descriptive |
| P8 MSM beats R1 and M0 on held-out days | ΔLL/pair vs R1 = 0.0123 (2/3 folds); vs M0 = 0.6647 | — | fail |
| order 2 vs 1 (τ = 1) | ΔLL/transition = 0.0274 | — | order 2 better |
| P5 per-agent I² of ln t2 | I² = 0.87 (12 agents; block-bootstrap SEs); own/shrink beats pooled for 0.33 of agents | — | pass |
| P6 committor asymmetry max \|δ\| | 0.004 (CI excl. 0: no); cores ['type', 'idle'] | 0 under detailed balance | fail |
| P7 σ(τ=1) > N2 p95; σ_macro/σ_micro < 0.5 | σ = 0.0020 nats/min; macro share 0.34 | N2 p95 0.0022 | fail |
| mixing time t_mix(¼) | 25 min | — | descriptive |
| R3 half-day t2\* (first / second half) | 38.3 / 14.9 | — | descriptive |
| robustness: 5-min windows (hard / soft counts / shifted = n/a) | 27.2 / 24.5 / – min | — | descriptive |
| robustness: records (≈5-min lag) | t2 ≈ 11.3 min | — | descriptive |
| stuckness covariates | error share 0.063; output 0.94/agent-h; idle share 0.55 | — | for P4b |

**Post hoc (boundary idle):** 80% of idle minutes lie in the leading/trailing idle run of an agent-day; without them t2\* = 8.5 min (N2 median 6.9), m = 2 split [['idle'], ['browse', 'type', 'shell', 'chat', 'consolidate']].
**Per-agent t2 (τ_c):** 18: 5, 23: 12, 14: 13, 16: 13, 17: 16, 12: 22, 13: 29, 6: 29, 22: 34, 20: 50, 21: 114, 10: 131 min (agent codes from `roster.parquet`); lab η² = 0.13 (perm p = 0.74).
**Within-period stuckness (per agent, n = 12):** ρ(t2, error share) = -0.62; ρ(t2, output rate) = -0.14; ρ(t2, idle share) = -0.91.

## Scorecard (period-specific axes)
| Axis | Evidence | Score |
| --- | --- | --- |
| B assumptions | CK max \|Δ\| 0.182 (fail); ITS rise t2(15)/t2(1) = 4.8; plateau: none; order 2 better by 0.027 nats; halves 38/15 min | 0 |
| C adequacy | MSM vs R1 ΔLL/pair +0.0123, vs M0 +0.665 (day-blocked) | 1 |
| D unfitted | t2\*/N2 = 1.19 (sets beyond sticky states: no); trimmed t2\*/N2 = 1.22 | 0 |
| G ground truth | slow set = [['browse', 'type', 'shell', 'chat', 'consolidate'], ['idle']]; 80% of idle minutes are boundary runs (scaffold/schedule) | 1 |

## Notes
