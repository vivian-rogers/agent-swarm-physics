# H62 × G36: Interact with other AI agents outside the Village! (2026-03-23 → 2026-03-30)

**Verdict:** mixed
**Role:** replication
**Period:** regime II · mode C · 13 agents · non-holdout days only (held-out days masked with `holdout_mask`).

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
**mixed.** 4037 ideas; 1119 adoptions in 592 idea strata; median agents posting per room-day 7.0; 686 DQ2 parent edges.

| Prediction | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| P1 Λ > 1 (CI) | Λ = 1.42 [1.20, 1.71] (bootstrap); HR_rep 15.9 (600 adoptions), HR_room 11.2 (213) | room-contagion synthetic Λ ≈ 0.8 | pass |
| P2 T_rep / T_room > 1 (CI) | 1.96 [1.65, 2.31]; T_rep 0.047 (10078 events), T_room 0.024 (8234) | 1 | pass |
| P3 C_room ≈ 1; C_rep > 1 | C_room 3.49 [1.28, 9.50] (underpowered); C_rep 9.46 [1.46, 61.36] (underpowered) | thread-field synthetic C_rep ≈ 1 | descriptive |
| P4 contagion share ≥ 2× exposure share | reply share of R_c 0.67 vs of exposures 0.55 (ratio 1.21) | 1 | fail |
| P6 guard Λ > 1 (CI) | 1.65 [1.39, 1.91]; guard T ratio 1.62 | 1 | pass |

Branching decomposition: R̂ = 0.225 = reply 0.149 + room-only 0.076 (+ human 0.001). Data: `data/processed/H62-ideas-travel-reply-graph/G36/`; numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
H (rival exposure models): Λ 1.42, T ratio 1.96. C (convergence): C_room 3.49, C_rep 9.46. F (guard): Λ_guard 1.65. E, G: not informed by this replication.

## Notes
- Reply channels use only DQ2 edges posted before the use; the adopting message's own parent never enters (circularity guard; RE-V2 known issue).
