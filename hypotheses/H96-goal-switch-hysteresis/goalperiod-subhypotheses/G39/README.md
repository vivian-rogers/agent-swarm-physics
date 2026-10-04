# H96 × G39: old-state remanence after the #38 → #39 switch (2026-04-27 → 2026-05-01)

**Verdict:** mixed
**Role:** native
**Period:** regime III · transition #38 → #39 · pre day 2026-04-24 · old-state days 2026-04-21, 2026-04-22, 2026-04-23 · post days 2026-04-27, 2026-04-28, 2026-04-29 · 5 placebo old states.

## Why this period
The common estimator (card O1–O3, O5) at the transition #38 → #39: both periods non-holdout and in regime III. The row belongs to the new period. It is one point for the card-level order test (O4): its old-state order q and its inertia time τ_old.

## Prediction
*Written 2026-10-04 21:40 UTC, before running on this period (card predictions applied).*
- The old state is identified: M_pre's agent-bootstrap CI excludes 0.
- Quench (card P1, expected): day-1 remanence is a small fraction of the pre level, below the median persistence ratio of ordinary day boundaries (pseudo-switches) of regime III; τ_old < 8 active h (P3).
- HH123's lag reading for this transition: M_1's CI excludes 0 and R₁ ≥ the pseudo-switch median.
- Verdict rule (card): *supported* (lag) if M_pre > 0, M_1 > 0 and R₁ ≥ the pseudo median; *failed* (quench) if M_pre > 0 and either M_1's CI includes 0 or R₁'s CI lies below the pseudo median; *mixed* otherwise; *descriptive* if M_pre's CI includes 0.

### Native N1 (two old rooms, one new field)
*Written 2026-10-04 21:40 UTC, before running.* #38 had two rooms with different kickoffs (#best: agents 20–23; #rest: 6, 10, 12–14, 16–18; DQ6). #39 applies one new field to both. Domain memory Δ = ⟨s·ê_own⊥ − s·ê_other⊥⟩ over veterans.
- Δ_pre > 0 with the CI excluding 0 [0.85]; Δ_1 > 0 with the CI excluding 0 [0.5]; Δ_1/Δ_pre < 0.5 [0.6].
- HH123: the room with the higher order q_room keeps the larger fraction Δ_1/Δ_pre [0.5].
- *Supported* if Δ_1 > 0 and the more ordered room keeps more; *failed* if Δ_pre > 0 and Δ_1's CI includes 0; *mixed* otherwise. Movers (20, 21, 23 go from #best to #rest) are reported separately because their new room-mates carry the other room's old state (contemporaneous convergence).

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout; bge primary, gte check).* 15 agents, 5 placebo old states, old-state order q = 0.163.

| Quantity | bge | gte | Null / reference |
| --- | --- | --- | --- |
| M_pre (old-state excess, pre day) | 0.269 [0.204, 0.352] | 0.310 [0.242, 0.414] | 0 |
| M_1 (day 1 after the switch) | -0.092 [-0.214, -0.005] | 0.008 [-0.050, 0.064] | 0 |
| R₁ = M_1 / M_pre | -0.34 [-0.86, -0.02] | 0.02 [-0.14, 0.24] | pseudo-switch median 0.89 |
| τ_old (active h) | 0.05 [0.05, 0.14] | 0.17 [0.07, 0.43] | quench ≪ 1 h |
| τ_sw switching time, A1 (active h; 500 = no decline) | – [1.7, 3.4] | – [0.3, 17.2] | – |
| old kickoff R₁ (O6) | 0.21 [-0.42, 0.83] | – | |
| new-kickoff depth A_K, day 1 | 0.223 [0.177, 0.269] | 0.278 [0.222, 0.335] | 0 |

**Verdict (card rule):** bge failed; gte failed. M_exc by bin (active h 0.2, 0.8, 1.5, 3.0, 6.1, 10.1): -0.004, -0.130, -0.080, -0.053, -0.162, -0.120.

### Native N1 result
| Group | bge | gte |
| --- | --- | --- |
| all veterans | Δ_pre 0.610 [0.480, 0.729], Δ_1 0.091 [0.019, 0.172], ratio 0.15 (n 12) | Δ_pre 0.584 [0.397, 0.730], Δ_1 0.151 [0.072, 0.225], ratio 0.26 (n 12) |
| from #best | Δ_pre 0.656 [0.476, 0.844], Δ_1 -0.023 [-0.089, 0.047], ratio -0.04 (n 4) | Δ_pre 0.637 [0.485, 0.749], Δ_1 0.039 [-0.054, 0.189], ratio 0.06 (n 4) |
| from #rest | Δ_pre 0.584 [0.418, 0.724], Δ_1 0.156 [0.076, 0.247], ratio 0.27 (n 8) | Δ_pre 0.553 [0.275, 0.767], Δ_1 0.215 [0.162, 0.263], ratio 0.39 (n 8) |
| movers (20, 21, 23) | Δ_pre 0.698 [0.419, 0.985], Δ_1 -0.057 [-0.113, -0.017], ratio -0.08 (n 3) | Δ_pre 0.619 [0.416, 0.805], Δ_1 -0.033 [-0.070, -0.005], ratio -0.05 (n 3) |
| stayers | Δ_pre 0.578 [0.444, 0.697], Δ_1 0.146 [0.074, 0.229], ratio 0.25 (n 9) | Δ_pre 0.570 [0.339, 0.754], Δ_1 0.220 [0.171, 0.264], ratio 0.39 (n 9) |

Room order q_room (bge): #best 0.547, #rest 0.375; higher-q room keeps more: False. **Native verdict:** bge mixed, gte mixed. The folder verdict is the native verdict; the replication verdict for this transition is failed (bge).

## Scorecard (period-specific axes)
- **C:** placebo old states and pseudo-switches as nulls; **D:** R₁ and τ_old are unfitted relative to the pre level; **F:** synthetic recovery at this transition's counts (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H96-goal-switch-hysteresis/results/transitions_{bge_small,gte_modernbert}_style_resid32.json` (key P = 39).
