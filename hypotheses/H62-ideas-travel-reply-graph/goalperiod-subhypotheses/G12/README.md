# H62 × G12: Form two teams and debate each other, while one agent judges. Choose your teammates wisely! (2025-09-01 → 2025-09-08)

**Verdict:** descriptive
**Role:** native (with the replication estimator)
**Period:** regime I · mode M · 7 agents · non-holdout days only (held-out days masked with `holdout_mask`).

## Why this period
Replication layer: the common H62 estimator (channel-resolved, idea-stratified adoption hazard; reply channel vs room-only exposure) on every period H34 analysed. This period also hosts a native test (section below), with its own dated prediction.

## Native test: debate teams (DQ6)
*Prediction written 2026-10-04 19:33 UTC, before any native statistic.* #12 is a judged debate with DQ6 team labels in one room. A team is a shared stance field. Every channel indicator is split by whether the source agent is on the recipient's team (same) or not (cross).
- **N12-a:** HR for reply-channel exposure from the other team ≥ HR for room-only exposure from team-mates (ideas cross a team boundary along reply edges at least as well as they move through the shared team field).
- **N12-b:** T_rep,cross > T_room,cross (point estimates; CIs reported).
- Credence 0.4 (936 ideas; power is low). Verdict: supported = both pass; failed = both fail; mixed = otherwise; descriptive if a cell has < 10 adoptions.

*Run 2026-10-04 after the prediction above.* Teams from DQ6 (`team`, gov / opp; bench and out-of-debate times form group 0).

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N12-a HR(reply, cross-team) ≥ HR(room-only, same team) | HR reply cross 0.72 (46 adoptions); HR room-only same 5.43 (6); ratio 0.13 [0.04, 0.58] | fail |
| N12-b T_rep,cross > T_room,cross | 0.029 (842 events) vs 0.009 (341); ratio 3.24 [1.41, 11.85] | pass |

Other cells: HR reply same-team 2.56 (59), room-only cross-team 1.03 (6), outside debates reply 3.25 (155) / room-only 1.09 (15). **Native verdict: descriptive.**

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

## Result (replication estimator)
**mixed.** 936 ideas; 312 adoptions in 179 idea strata; median agents posting per room-day 7.0; 1248 DQ2 parent edges.

| Prediction | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| P1 Λ > 1 (CI) | Λ = 2.40 [1.60, 3.92] (bootstrap); HR_rep 5.9 (223 adoptions), HR_room 2.5 (26) | room-contagion synthetic Λ ≈ 0.8 | pass |
| P2 T_rep / T_room > 1 (CI) | 4.06 [2.62, 7.02]; T_rep 0.045 (3933 events), T_room 0.011 (1635) | 1 | pass |
| P3 C_room ≈ 1; C_rep > 1 | C_room 0.50 [0.23, 1.05] (underpowered); C_rep 0.76 [0.45, 1.28] | thread-field synthetic C_rep ≈ 1 | descriptive |
| P4 contagion share ≥ 2× exposure share | reply share of R_c 0.88 vs of exposures 0.71 (ratio 1.24) | 1 | fail |
| P6 guard Λ > 1 (CI) | 2.75 [1.79, 4.72]; guard T ratio 3.95 | 1 | pass |

Branching decomposition: R̂ = 0.284 = reply 0.237 + room-only 0.047 (+ human 0.006). Data: `data/processed/H62-ideas-travel-reply-graph/G12/`; numbers from `analysis/explore.py` → `results/periods.json`.

Replication verdict for this period: **mixed**.

## Scorecard (period-specific axes)
H (rival exposure models): Λ 2.40, T ratio 4.06. C (convergence): C_room 0.50, C_rep 0.76. F (guard): Λ_guard 2.75. E, G: not informed by this replication.

## Notes
- Reply channels use only DQ2 edges posted before the use; the adopting message's own parent never enters (circularity guard; RE-V2 known issue).
