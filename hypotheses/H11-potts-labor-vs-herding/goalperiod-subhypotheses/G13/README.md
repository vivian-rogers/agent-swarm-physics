# H11 × G13: Design, run and write up a human subjects experiment (2025-09-08 → 2025-09-22)

**Verdict:** n/a (insufficient labels)
**Verdict (1b):** n/a (insufficient labels; unchanged)
**Role:** exploratory (candidate)
**Period:** regime I · mode C · N = 6 at start · one room (#general) · 10 active days. Class for H11: **AF**.

## Why this period
HH24's case: a shared objective with separable subtasks (design, recruit, run, analyze, write). The cleanest a-priori antiferromagnetic week. Labels here are mostly Google Docs, Forms and Sheets, and only ~28% of agent-windows carry a strict mention, so power is low.

## Prediction
*Written 2026-10-03, before running on this period.*
- **Class prediction:** antiferromagnetic (division of labor): βJ_CW < 0 (P1) and βJ_PL ≤ 0 vs the circular-shift null N2 (P2). Per-period verdict on P1: **supported** if the sign is right and |t| > t_(D−1, 0.975) (leave-one-day-out jackknife); **weak** if the sign is right but not significant; **failed** if the sign is wrong.
- **P4 (control):** the action-class βJ_CW is positive or ≈ 0 whatever the class.
- **P7 (prior):** |βJ_CW| < 2, below βJ_s(q), so no spontaneous first-order transition.
- **Minimum data:** ≥ 15 room blocks with N_b ≥ 3 at W = 30; otherwise n/a.
- **What would count against it:** the opposite sign of βJ_CW (P1), or, for an FM class, a positive βJ_CW that disappears under the within-agent permutation null N1 (spread carried entirely by agent fields, R1).

## Result
Not tested: 14 room blocks with ≥ 3 labeled agents (minimum 15), from 106 labeled agent-windows.

*Descriptive only (below the minimum-data rule):* βJ_CW = +4.68 (jackknife SE 0.71); βJ_PL = +6.22, z vs N2 = +1.75. The sign is opposite to the AF prediction, but this does not count as a test.

## Scorecard (period-specific axes)
No period-specific axes scored (insufficient labels).

## Notes
- 2026-10-03 (round 1): only 28% of agent-windows carry a strict artifact mention (mostly Google Docs/Forms/Sheets), so the HH24 test of this period needs a different state variable (e.g. chat-declared task assignments).

## Round 1b (improved data, 2026-10-04)
*Replication on the shared deterministic `project_states` labels (`scheme/build_r1b.py`, `analysis/round1b.py`).* Still below the minimum-data rule: 14 room blocks with ≥ 3 labelled agents (minimum 15). Nothing to re-test.
