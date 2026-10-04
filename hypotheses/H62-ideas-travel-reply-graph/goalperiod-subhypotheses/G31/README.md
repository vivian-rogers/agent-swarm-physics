# H62 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-23)

**Verdict:** mixed
**Role:** replication
**Period:** regime I · mode F · 12 agents · non-holdout days only (held-out days masked with `holdout_mask`).

## Why this period
Replication layer: the common H62 estimator (channel-resolved, idea-stratified adoption hazard; reply channel vs room-only exposure) on every period H34 analysed.

## Prediction
*Written 2026-10-04 19:45 UTC, before running on this period* (after the card's predictions at 19:25 UTC and the synthetic validation and amendments A1–A2 of the card; no channel-resolved statistic had been computed on real data).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | Sharper locking on the reply graph: Λ = HR_rep / HR_room > 1 with lower 95% CI > 1 (recency window, idea-stratified) | CI includes 1 or Λ < 1 |
| P2 | Per-edge transmissibility T_rep / T_room > 1 (CI > 1) | ratio ≤ 1 |
| P3 | Room-only exposure is mostly a field: C_room (seen vs unread room-only uses at 300 s) CI includes 1 or C_room < 1.5; C_rep > 1 (where Model B has ≥ 10 adoptions per cell) | C_room > 1.5 with CI > 1 |
| P4 | The reply channel's share of the contagion share exceeds its share of exposure events by ≥ 2× | ratio < 1.2 |
| P6 | Under the tie-only guard, Λ lower CI > 1 | guard Λ CI includes 1 |

**Verdict rule (card, with amendment A2, 19:44 UTC):** supported = Λ lower 95% CI > 1, T_rep / T_room lower 95% CI > 1 and C_rep lower 95% CI > 1 (reading matters inside the reply channel; unread-only coding, A1); mixed = a reply premium without C_rep CI > 1, or C_rep underpowered (consistent with a thread field); failed = Λ ≤ 1 and T_rep / T_room ≤ 1; n/a = < 20 adoptions at reply-channel or at room-only recency calls.

## Result
**mixed.** 3722 ideas; 1085 adoptions in 565 idea strata; median agents posting per room-day 12.0; 1009 DQ2 parent edges.

| Prediction | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| P1 Λ > 1 (CI) | Λ = 1.90 [1.65, 2.20] (bootstrap); HR_rep 11.6 (673 adoptions), HR_room 6.1 (277) | room-contagion synthetic Λ ≈ 0.8 | pass |
| P2 T_rep / T_room > 1 (CI) | 2.35 [1.97, 2.85]; T_rep 0.028 (16878 events), T_room 0.012 (21364) | 1 | pass |
| P3 C_room ≈ 1; C_rep > 1 | C_room 0.65 [0.38, 1.13]; C_rep 1.53 [0.83, 2.82] | thread-field synthetic C_rep ≈ 1 | descriptive |
| P4 contagion share ≥ 2× exposure share | reply share of R_c 0.58 vs of exposures 0.44 (ratio 1.32) | 1 | fail |
| P6 guard Λ > 1 (CI) | 1.86 [1.59, 2.14]; guard T ratio 2.16 | 1 | pass |

Branching decomposition: R̂ = 0.297 = reply 0.166 + room-only 0.131 (+ human 0.000). Data: `data/processed/H62-ideas-travel-reply-graph/G31/`; numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
H (rival exposure models): Λ 1.90, T ratio 2.35. C (convergence): C_room 0.65, C_rep 1.53. F (guard): Λ_guard 1.86. E, G: not informed by this replication.

## Notes
- Reply channels use only DQ2 edges posted before the use; the adopting message's own parent never enters (circularity guard; RE-V2 known issue).
