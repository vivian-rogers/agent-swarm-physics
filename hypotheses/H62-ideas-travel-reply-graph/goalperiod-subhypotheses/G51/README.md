# H62 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-20)

**Verdict:** supported
**Role:** native (with the replication estimator)
**Period:** regime III · mode I/K · 21 agents · non-holdout days only (held-out days masked with `holdout_mask`).

## Why this period
Replication layer: the common H62 estimator (channel-resolved, idea-stratified adoption hazard; reply channel vs room-only exposure) on every period H34 analysed. This period also hosts a native test (section below), with its own dated prediction.

## Native test: the largest rooms (dilution)
*Prediction written 2026-10-04 19:33 UTC, before any native statistic.* #51 has the largest rooms of the village (median ≈ 23 agents posting per room-day vs 5–14 elsewhere). Attention dilution (H18: per-pair coupling ∝ N^−0.6; H34: per-pair branching ∝ N^−0.55) should hit room-only exposure hardest, while a reply partner is read whatever the room size.
- **N51-a:** Λ(#51) ≥ 2 with lower 95% CI > 1, and Λ(#51) above the median Λ of the other eligible regime-III periods.
- **N51-b:** T_room(#51) is below every other eligible regime-III period's T_room, while T_rep(#51) lies inside the range of the other regime-III periods.
- Credence 0.5. Verdict: supported = N51-a and N51-b pass; failed = both fail; mixed = otherwise.

*Run 2026-10-04 after the prediction above.* Other eligible regime-III periods: G36, G37, G38, G39, G40, G41, G42, G44.

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N51-a Λ ≥ 2, CI > 1, above the regime-III median | Λ = 9.62 [8.57, 10.91]; other regime-III median 2.17 | pass |
| N51-b T_room lowest of regime III; T_rep inside their range | T_room 0.004 (others' min 0.004); T_rep 0.038 (others 0.016–0.090) | pass |

**Native verdict: supported.**

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
**supported.** 51929 ideas; 2972 adoptions in 2133 idea strata; median agents posting per room-day 23.0; 22917 DQ2 parent edges.

| Prediction | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| P1 Λ > 1 (CI) | Λ = 9.62 [8.57, 10.91] (bootstrap); HR_rep 106.7 (1732 adoptions), HR_room 11.1 (789) | room-contagion synthetic Λ ≈ 0.8 | pass |
| P2 T_rep / T_room > 1 (CI) | 9.96 [9.10, 11.02]; T_rep 0.038 (40188 events), T_room 0.004 (192185) | 1 | pass |
| P3 C_room ≈ 1; C_rep > 1 | C_room 1.85 [0.90, 3.80] (underpowered); C_rep 1.70 [1.15, 2.53] | thread-field synthetic C_rep ≈ 1 | descriptive |
| P4 contagion share ≥ 2× exposure share | reply share of R_c 0.60 vs of exposures 0.17 (ratio 3.49) | 1 | pass |
| P6 guard Λ > 1 (CI) | 9.79 [8.82, 11.31]; guard T ratio 8.23 | 1 | pass |

Branching decomposition: R̂ = 0.228 = reply 0.133 + room-only 0.095 (+ human 0.000). Data: `data/processed/H62-ideas-travel-reply-graph/G51/`; numbers from `analysis/explore.py` → `results/periods.json`.

Replication verdict for this period: **supported**.

## Scorecard (period-specific axes)
H (rival exposure models): Λ 9.62, T ratio 9.96. C (convergence): C_room 1.85, C_rep 1.70. F (guard): Λ_guard 9.79. E, G: not informed by this replication.

## Notes
- Reply channels use only DQ2 edges posted before the use; the adopting message's own parent never enters (circularity guard; RE-V2 known issue).
