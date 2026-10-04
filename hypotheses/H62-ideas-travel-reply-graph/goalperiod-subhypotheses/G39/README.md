# H62 × G39: Build your own interactive world! (2026-04-27 → 2026-05-04)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · mode I · 15 agents · non-holdout days only (held-out days masked with `holdout_mask`).

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
**mixed.** 3172 ideas; 245 adoptions in 183 idea strata; median agents posting per room-day 7.0; 164 DQ2 parent edges.

| Prediction | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| P1 Λ > 1 (CI) | Λ = 1.66 [1.13, 2.47] (bootstrap); HR_rep 11.2 (71 adoptions), HR_room 6.8 (129) | room-contagion synthetic Λ ≈ 0.8 | pass |
| P2 T_rep / T_room > 1 (CI) | 4.08 [2.87, 5.98]; T_rep 0.016 (3158 events), T_room 0.004 (26286) | 1 | pass |
| P3 C_room ≈ 1; C_rep > 1 | C_room 2.17 [0.52, 8.97] (underpowered); C_rep 1.07 [0.11, 10.75] (underpowered) | thread-field synthetic C_rep ≈ 1 | descriptive |
| P4 contagion share ≥ 2× exposure share | reply share of R_c 0.30 vs of exposures 0.11 (ratio 2.84) | 1 | pass |
| P6 guard Λ > 1 (CI) | 1.77 [1.16, 2.87]; guard T ratio 3.77 | 1 | pass |

Branching decomposition: R̂ = 0.088 = reply 0.026 + room-only 0.062 (+ human 0.001). Data: `data/processed/H62-ideas-travel-reply-graph/G39/`; numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
H (rival exposure models): Λ 1.66, T ratio 4.08. C (convergence): C_room 2.17, C_rep 1.07. F (guard): Λ_guard 1.77. E, G: not informed by this replication.

## Notes
- Reply channels use only DQ2 edges posted before the use; the adopting message's own parent never enters (circularity guard; RE-V2 known issue).
