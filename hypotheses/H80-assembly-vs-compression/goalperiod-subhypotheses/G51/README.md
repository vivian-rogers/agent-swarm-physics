# H80 × G51: Maximize your private assigned role (2026-07-06 → 2026-09-04 non-holdout; post-period automata 09-21 → 10-03)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · mode K (private roles) · N 21 → 32 · one room (+ #focus) · 45 non-holdout days. Units: in-period G51 (one automated stream, the GPT-5 cron stream) and G51+post (adds 28 automated streams that commit after the village's last day, 09-21 → 10-03; amendment A1).

## Why this period
The densest git period (54k agent work commits, 87k automated). It is the only period with many automated streams, and the only one where 11–13 agents have a true first day (joiners, NE32, NE33), which the shared-prior test needs.

## Prediction
*Written 2026-10-04, before running on this period.*
- P1: compression family C reaches AUC ≥ 0.90 (G51+post repo-blocked; G51 in-period day-blocked).
- P2: ΔAUC_A = AUC(C + A) − AUC(C) < 0.02. Kill: ≥ 0.05.
- P3: Spearman ρ(a_RP, LZ78) ≥ 0.9 over windows.
- P4: timing T alone ≥ 0.85; T + C adds ≥ 0.02 over T.
- P5: ≥ 70% of high-index (a ≥ 6), high-copy (≥ 20 sessions) command motifs are present on a joiner's first day and used by ≥ 2 labs; median first-day / later-day presence ratio ≥ 0.8.
- P6: joiners' NCD to the other joiners' first-day reference does not fall by ≥ 0.05 from days 1–2 to days ≥ 5.

## Result
Data: `data/processed/H80-assembly-vs-compression/results/{classifier,motifs,ncd}.json`; `analysis/run.py`.

| Prediction | Observed (95% cluster-bootstrap CI) | Verdict |
| --- | --- | --- |
| P1 C ≥ 0.90 | in-period (1 stream, day-blocked): 0.965 [0.947, 0.980]; **G51+post (28 streams, repo-blocked): 0.254 [0.150, 0.464]** | failed (holds only for one cron stream) |
| P2 ΔAUC_A < 0.02 | in-period +0.0009 [−0.0003, 0.0019]; G51+post −0.0074 [−0.018, −0.001] | supported (kill not near) |
| P3 ρ(a_RP, LZ78) ≥ 0.9 | 0.82 (LZ76 0.83) over 3,609 windows | failed |
| P4 T ≥ 0.85; T + C adds ≥ 0.02 | T 0.999 in-period, 0.915 G51+post; T + C adds +0.001 [0.000, 0.002] and −0.003 | first part supported; second failed |
| P5 prior share ≥ 70% | 7.8% of 562 high-index, high-copy motifs on a joiner's first day and in ≥ 2 labs (copy-matched low-index motifs: 14.8% on a first day) | failed |
| P6 no NCD fall | late − early NCD +0.005 (7 joiners, all > 0); incumbents' slope −5×10⁻⁶ per day | supported |

**Readings.**
- The in-period automated windows are one cron stream that writes identical commits (1.25 distinct tokens per 16 commits). The 28 post-period streams write commits as varied as agent work (12.5 vs 12.5 distinct tokens). Compression detects replay, not automation.
- Repo-blocked C below 0.5 means the classifier learns "low complexity = script" from the cron stream and the rule inverts on other scripts.
- High-index motifs are not shared: the median number of agents per motif falls from 7 at a = 2 to 1 at a = 7. The top agent holds 70% of a high-index motif's agent-days. High a × high copy here is one agent's habit repeated, not cross-agent selection and not a cross-family prior.

## Scorecard (period-specific axes)
- C: 1. Every family beats label permutation in-period (p < 0.005), but C fails transfer across streams (0.25).
- D: 1. P2 and P6 hold; P1, P3, P5 fail.
- H: 2 against AT (assembly adds ≤ 0.001 AUC); 0 for compression against the scheduler.

## Notes
- 2026-10-04: round 1 run.
