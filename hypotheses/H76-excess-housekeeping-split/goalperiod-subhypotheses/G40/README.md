# H76 × G40: Connect your worlds into a 3D universe (2026-05-04 → 05-08)

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** regime III · 15 agents · one merged room · 5 days, 4-h days.

## Why this period
- The G40-sized design of the synthetic (N 15 × 5 days): expected to be unresolved for P2/P3 (amendment A1); kept as the small-period point.

## Prediction
*Written 2026-10-04 ~20:15 UTC, after the synthetic validation (amendment A1), before running on this period.*
- P1 (kickoff above every day start, share ≥ 0.3): expected to fail; not identifiable at village N under the model (A1).
- P2: pooled edge share of σ_ex (untrimmed, coarse) ≥ 0.6.
- P3: trimming removes ≥ 70% of σ_ex; σ_hk removal ≤ the share of steps removed + 0.1.
- P4: σ_hk/σ ≥ 0.7 on the trimmed grid; fine-state σ_hk per transition within ×[0.3, 10] of H14's pooled v3 EP.
- Verdict rule (card): supported if P2 and P3 hold (P1 undetectable); failed if P2 and P3 both fail; mixed otherwise.

## Result
*Run 2026-10-04 ~21:00 UTC (`analysis/run.py`; data `data/processed/H76-excess-housekeeping-split/G40/`; figure `../../figures/summary_obs.pdf`).* Coarse 5-state soft fluxes, debiased by the block-flip floor, pooled over 4 non-kickoff days (median 15 agents per day); agent bootstrap B = 100 with per-replicate floors (amendment A2).

| Prediction | Observed (95% CI) | Null | Verdict |
| --- | --- | --- | --- |
| P1 kickoff above every day start, share ≥ 0.3 | rank 0.33 (share of day starts below the kickoff); share n/a | synthetic: not identifiable | fails (expected) |
| P1b decay τ in [2.5, 10] h | τ = 2.2 h, bootstrap [0.25, 40] (grid limits) | — | not identified |
| P2 edge share ≥ 0.6 (untrimmed, pooled) | 1.00 [0.97, 1.06]; per-day median 1.01; time share of edge steps 0.25 | uniform time: 0.25 | holds |
| start vs end block share of σ_ex | start -0.00, end 1.00 | — | the end carries the excess |
| P3a trimming removes ≥ 70% of σ_ex | 1.00 [0.93, 1.06] | — | holds |
| P3b σ_hk removal ≤ steps removed + 0.1 | σ_hk 0.64 [-1.17, 3.45] vs steps 0.28 | — | fails (CI uninformative) |
| P4 σ_hk/σ ≥ 0.7 (trimmed) | coarse 1.07 [-1.23, 9.47]; fine -0.47 | — | holds (point); CI spans 0 |
| P4 fine σ_hk per step vs H14 pooled v3 EP | -0.0007 vs 0.0026 nats (×-0.29) | ×[0.3, 10] | fails |
| excess per agent-step, untrimmed / trimmed | 0.0283 / -0.0001 nats (×12 per agent-hour) | — | — |

**Verdict: mixed.** Excess is the scheduler's day edges, mostly the end of the day, and trimming removes it. The kickoff adds nothing detectable beyond an ordinary day start. Housekeeping is at the noise floor of a 15-agent ensemble with soft labels.

## Scorecard (period-specific axes)
- C: the excess at the edges beats the block-flip floor (CI of the edge share excludes the uniform-time share); housekeeping does not.
- D: P2 and P3a hold as predicted; the end-of-day concentration was not predicted.

## Notes
- Only 4 non-kickoff days, but the edge share's CI is narrow (0.97–1.06), so the G40-sized design resolves P2 here, unlike in the synthetic (the real edge excess is 5–10× the synthetic's).
