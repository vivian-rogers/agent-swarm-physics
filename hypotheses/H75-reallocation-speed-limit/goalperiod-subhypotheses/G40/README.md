# H75 × G40: Connect your worlds into a 3D universe (2026-05-04 → 05-08)

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** regime III · 15 agents · one merged room (NE42) · 5 days, 20.3 active h.

## Why this period
- One shared artifact: the kickoff points every agent at the same target, while each agent keeps its own world repo. The previous week #39 is non-holdout.
- Dense agent-work commits (DQ4), regime III, horizon 20 active h after the kickoff (W_pre (primary) and W_∅).

## Prediction
*Written 2026-10-04 ~20:15 UTC, after the synthetic validation (amendment A1), before running on this period.*
- P0: ĀT ≥ W (scheme check).
- P1 (templated from the card): S(T_e) ≥ 3 with agent-bootstrap lower bound ≥ 2 → supported; S ≤ 2 → failed. After A1, "supported" means churn-dominated settling, not an instant freeze (R2); it does not separate field from activity limitation.
- P3: T_e in [2.5, 10] active h. R2 predicts T_e ≤ 1 h.
- P4 (enters the pooled test only): ε per period, read against the synthetic means (F −0.53, A −0.86).

## Result
*Run 2026-10-04 ~20:50 UTC (`analysis/run.py`; data `data/processed/H75-reallocation-speed-limit/G40/results_*.json`; figure `../../figures/summary_obs.pdf`).* N = 13 committing agents; median call rate 132 calls per active hour; D(0) = 0.77, settled floor D_f = 0.00.

| Prediction | Observed (agent-bootstrap 95% CI) | Null / rival | Verdict |
| --- | --- | --- | --- |
| P0 bound ĀT ≥ W | violations: none | counting identity | holds (scheme check) |
| P1 slack S(T_e) ≥ 3, boot lower ≥ 2 | S = 1.25 [1.00, 12.70]; W = 0.62, Ā = 1.54 switches/agent/h | synthetic F/A ≈ 4.5, Z ≈ 1.15 | fails |
| P3 T_e in [2.5, 10] h | T_e = 0.50 h [0.25, 4.50]; T_90 = 4.50 h [0.50, 13.00] | R2 instant freeze: T_e ≤ 1 h | fails |
| tail slack S_90 (descriptive) | 5.89 [1.00, 26.51] | — | — |
| activity ratio R (P2) | R = 0.00; Ā_ss = 0.00/h in the settled window | ≥ 3 | fails |
| Σ_ex,min = 2W atanh(1/S) (nats/agent) | 1.35 | — | — |
| ε (log t_i on log r_i; P4 input) | -0.70 ± 2.26 (n 10); with commit control 1.82 ± 2.08 | F −0.53, A −0.86 | uninformative (SE > 0.7) |

The from-scratch variant (W_∅) gives S = 1.64 [1.30, 4.60], T_e = 0.50 h.

## Scorecard (period-specific axes)
- C: S separates freeze from churn here; the bootstrap CI is wide.
- D: the field-limited prediction (P1, P3) fails; the instant-freeze rival R2 fits.

## Notes
- Reading: a near-freeze (S 1.25 at T_e = 0.5 h), then a churn tail (S_90 5.9 over 4.5 h) as agents move between their own worlds and the shared universe repo. Stationary switching in the last 4 h is zero (R = 0).
