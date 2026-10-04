# H75 × G41: Novel research (2026-05-11 → 05-15)

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** regime III · 15 agents · #best / #rest (NE42 split back) · 5 days, 20.1 active h.

## Why this period
- Individual research projects after a shared-artifact week: a move away from one shared repo to many new ones. Previous week #40 is non-holdout.
- Dense agent-work commits (DQ4), regime III, horizon 20 active h after the kickoff (W_pre (primary) and W_∅).

## Prediction
*Written 2026-10-04 ~20:15 UTC, after the synthetic validation (amendment A1), before running on this period.*
- P0: ĀT ≥ W (scheme check).
- P1 (templated from the card): S(T_e) ≥ 3 with agent-bootstrap lower bound ≥ 2 → supported; S ≤ 2 → failed. After A1, "supported" means churn-dominated settling, not an instant freeze (R2); it does not separate field from activity limitation.
- P3: T_e in [2.5, 10] active h. R2 predicts T_e ≤ 1 h.
- P4 (enters the pooled test only): ε per period, read against the synthetic means (F −0.53, A −0.86).

## Result
*Run 2026-10-04 ~20:50 UTC (`analysis/run.py`; data `data/processed/H75-reallocation-speed-limit/G41/results_*.json`; figure `../../figures/summary_obs.pdf`).* N = 13 committing agents; median call rate 122 calls per active hour; D(0) = 0.85, settled floor D_f = 0.16.

| Prediction | Observed (agent-bootstrap 95% CI) | Null / rival | Verdict |
| --- | --- | --- | --- |
| P0 bound ĀT ≥ W | violations: none | counting identity | holds (scheme check) |
| P1 slack S(T_e) ≥ 3, boot lower ≥ 2 | S = 5.09 [1.42, 11.19]; W = 0.85, Ā = 0.45 switches/agent/h | synthetic F/A ≈ 4.5, Z ≈ 1.15 | mixed |
| P3 T_e in [2.5, 10] h | T_e = 9.50 h [0.75, 16.50]; T_90 = 16.50 h [9.50, 16.75] | R2 instant freeze: T_e ≤ 1 h | holds |
| tail slack S_90 (descriptive) | 8.91 [5.29, 12.72] | — | — |
| activity ratio R (P2) | R = 6.91; Ā_ss = 0.62/h in the settled window | ≥ 3 | holds |
| Σ_ex,min = 2W atanh(1/S) (nats/agent) | 0.34 | — | — |
| ε (log t_i on log r_i; P4 input) | -1.75 ± 4.58 (n 11); with commit control -2.66 ± 5.13 | F −0.53, A −0.86 | uninformative (SE > 0.7) |

The from-scratch variant (W_∅) gives S = 3.69 [1.45, 7.54], T_e = 9.00 h.

## Scorecard (period-specific axes)
- C: S separates freeze from churn here; the bootstrap CI is wide.
- D: the field-limited prediction (P1, P3) fits in its time band; S's lower bound (1.4) misses the 2 cut.

## Notes
- Reading: churn-dominated, slow settling. No shared target: agents start new research repos and move between them for 9.5 active h; 5 switches per net move. The only replication period in the H54/H48 time band.
