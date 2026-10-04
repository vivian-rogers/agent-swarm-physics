# H76 × G51: Maximize your private assigned role (2026-07-06 → 09-04, non-holdout head)

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** regime III · 21 → 32 agents · one room (+ #focus from 08-05) · 45 non-holdout days, 8-h days.

## Why this period
- The largest ensemble and the most days: the only period where the synthetic says edges and trimming are resolvable with SD ≲ 0.25.

## Prediction
*Written 2026-10-04 ~20:15 UTC, after the synthetic validation (amendment A1), before running on this period.*
- P1 (kickoff above every day start, share ≥ 0.3): expected to fail; not identifiable at village N under the model (A1).
- P2: pooled edge share of σ_ex (untrimmed, coarse) ≥ 0.6.
- P3: trimming removes ≥ 70% of σ_ex; σ_hk removal ≤ the share of steps removed + 0.1.
- P4: σ_hk/σ ≥ 0.7 on the trimmed grid; fine-state σ_hk per transition within ×[0.3, 10] of H14's pooled v3 EP.
- Verdict rule (card): supported if P2 and P3 hold (P1 undetectable); failed if P2 and P3 both fail; mixed otherwise.

## Result
*Run 2026-10-04 ~21:00 UTC (`analysis/run.py`; data `data/processed/H76-excess-housekeeping-split/G51/`; figure `../../figures/summary_obs.pdf`).* Coarse 5-state soft fluxes, debiased by the block-flip floor, pooled over 44 non-kickoff days (median 27 agents per day); agent bootstrap B = 100 with per-replicate floors (amendment A2).

| Prediction | Observed (95% CI) | Null | Verdict |
| --- | --- | --- | --- |
| P1 kickoff above every day start, share ≥ 0.3 | rank 0.06 (share of day starts below the kickoff); share n/a | synthetic: not identifiable | fails (expected) |
| P1b decay τ in [2.5, 10] h | τ = 4.7 h, bootstrap [0.25, 40] (grid limits) | — | not identified |
| P2 edge share ≥ 0.6 (untrimmed, pooled) | 0.80 [0.73, 0.90]; per-day median 0.95; time share of edge steps 0.12 | uniform time: 0.12 | holds |
| start vs end block share of σ_ex | start 0.08, end 0.72 | — | the end carries the excess |
| P3a trimming removes ≥ 70% of σ_ex | 0.81 [0.69, 0.90] | — | holds |
| P3b σ_hk removal ≤ steps removed + 0.1 | σ_hk 0.60 [-1.43, 1.99] vs steps 0.30 | — | fails (CI uninformative) |
| P4 σ_hk/σ ≥ 0.7 (trimmed) | coarse 0.33 [-0.93, 0.61]; fine 0.62 | — | fails; CI spans 0 |
| P4 fine σ_hk per step vs H14 pooled v3 EP | 0.0028 vs 0.0118 nats (×0.24) | ×[0.3, 10] | fails |
| excess per agent-step, untrimmed / trimmed | 0.0060 / 0.0017 nats (×12 per agent-hour) | — | — |

**Verdict: mixed.** Excess is the scheduler's day edges, mostly the end of the day, and trimming removes it. The kickoff adds nothing detectable beyond an ordinary day start. Housekeeping is at the noise floor of a 27-agent ensemble with soft labels.

## Scorecard (period-specific axes)
- C: the excess at the edges beats the block-flip floor (CI of the edge share excludes the uniform-time share); housekeeping does not.
- D: P2 and P3a hold as predicted; the end-of-day concentration was not predicted.

## Notes
- The trimmed (all-present) window is empty on 11 of 44 non-kickoff days (one agent with a short span empties it); trim statistics use the 33 days that have one. Trimming removes 30% of agent-steps.
- Housekeeping does not separate from the block-flip floor (bootstrap CIs of σ_hk statistics span 0). The coarse share 0.33 and the fine 0.62 are therefore not interpretable.
