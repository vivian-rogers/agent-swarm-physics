# H76 × G38: Charity fundraiser, year 2 (2026-04-02 → 04-24)

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** regime III · 12 → 14 agents · #best / #rest · 17 days, 4-h days.

## Why this period
- The longest 4-h regime-III period: an intermediate design between G40 and G51.

## Prediction
*Written 2026-10-04 ~20:15 UTC, after the synthetic validation (amendment A1), before running on this period.*
- P1 (kickoff above every day start, share ≥ 0.3): expected to fail; not identifiable at village N under the model (A1).
- P2: pooled edge share of σ_ex (untrimmed, coarse) ≥ 0.6.
- P3: trimming removes ≥ 70% of σ_ex; σ_hk removal ≤ the share of steps removed + 0.1.
- P4: σ_hk/σ ≥ 0.7 on the trimmed grid; fine-state σ_hk per transition within ×[0.3, 10] of H14's pooled v3 EP.
- Verdict rule (card): supported if P2 and P3 hold (P1 undetectable); failed if P2 and P3 both fail; mixed otherwise.

## Result
*Run 2026-10-04 ~21:00 UTC (`analysis/run.py`; data `data/processed/H76-excess-housekeeping-split/G38/`; figure `../../figures/summary_obs.pdf`).* Coarse 5-state soft fluxes, debiased by the block-flip floor, pooled over 16 non-kickoff days (median 12 agents per day); agent bootstrap B = 100 with per-replicate floors (amendment A2).

| Prediction | Observed (95% CI) | Null | Verdict |
| --- | --- | --- | --- |
| P1 kickoff above every day start, share ≥ 0.3 | rank 0.85 (share of day starts below the kickoff); share 0.21 | synthetic: not identifiable | fails (expected) |
| P1b decay τ in [2.5, 10] h | τ = 4.5 h, bootstrap [0.25, 40] (grid limits) | — | not identified |
| P2 edge share ≥ 0.6 (untrimmed, pooled) | 0.94 [0.82, 1.07]; per-day median 0.97; time share of edge steps 0.25 | uniform time: 0.25 | holds |
| start vs end block share of σ_ex | start 0.01, end 0.93 | — | the end carries the excess |
| P3a trimming removes ≥ 70% of σ_ex | 1.00 [0.90, 1.09] | — | holds |
| P3b σ_hk removal ≤ steps removed + 0.1 | σ_hk 0.57 [-2.86, 14.52] vs steps 0.28 | — | fails (CI uninformative) |
| P4 σ_hk/σ ≥ 0.7 (trimmed) | coarse 0.94 [-3.38, 3.81]; fine 0.28 | — | holds (point); CI spans 0 |
| P4 fine σ_hk per step vs H14 pooled v3 EP | 0.0003 vs 0.0069 nats (×0.04) | ×[0.3, 10] | fails |
| excess per agent-step, untrimmed / trimmed | 0.0155 / 0.0001 nats (×12 per agent-hour) | — | — |

**Verdict: mixed.** Excess is the scheduler's day edges, mostly the end of the day, and trimming removes it. The kickoff adds nothing detectable beyond an ordinary day start. Housekeeping is at the noise floor of a 12-agent ensemble with soft labels.

## Scorecard (period-specific axes)
- C: the excess at the edges beats the block-flip floor (CI of the edge share excludes the uniform-time share); housekeeping does not.
- D: P2 and P3a hold as predicted; the end-of-day concentration was not predicted.

## Notes
- Trimming removes 28% of agent-steps. The kickoff is the third highest of 14 two-hour starts (11 of 13 day starts lie below it, two above).
