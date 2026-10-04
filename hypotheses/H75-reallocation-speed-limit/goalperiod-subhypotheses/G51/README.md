# H75 × G51: Maximize your private assigned role (2026-07-06 → 09-04, non-holdout head)

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** regime III · 21 agents at the kickoff · one room · first 20 active h = 07-06 → 07-08 (8-h days).

## Why this period
- Private roles: each agent gets its own target. The previous week #50 is held out, so only W_∅ (re-allocation from scratch) is available.
- Dense agent-work commits (DQ4), regime III, horizon 20 active h after the kickoff (W_∅ only).

## Prediction
*Written 2026-10-04 ~20:15 UTC, after the synthetic validation (amendment A1), before running on this period.*
- P0: ĀT ≥ W (scheme check).
- P1 (templated from the card): S(T_e) ≥ 3 with agent-bootstrap lower bound ≥ 2 → supported; S ≤ 2 → failed. After A1, "supported" means churn-dominated settling, not an instant freeze (R2); it does not separate field from activity limitation.
- P3: T_e in [2.5, 10] active h. R2 predicts T_e ≤ 1 h.
- P4 (enters the pooled test only): ε per period, read against the synthetic means (F −0.53, A −0.86).

## Result
*Run 2026-10-04 ~20:50 UTC (`analysis/run.py`; data `data/processed/H75-reallocation-speed-limit/G51/results_*.json`; figure `../../figures/summary_obs.pdf`).* N = 16 committing agents; median call rate 89 calls per active hour; D(0) = 0.97, settled floor D_f = 0.18.

| Prediction | Observed (agent-bootstrap 95% CI) | Null / rival | Verdict |
| --- | --- | --- | --- |
| P0 bound ĀT ≥ W | violations: none | counting identity | holds (scheme check) |
| P1 slack S(T_e) ≥ 3, boot lower ≥ 2 | S = 1.40 [1.00, 3.94]; W = 0.62, Ā = 1.75 switches/agent/h | synthetic F/A ≈ 4.5, Z ≈ 1.15 | fails |
| P3 T_e in [2.5, 10] h | T_e = 0.50 h [0.49, 6.00]; T_90 = 6.25 h [0.50, 7.75] | R2 instant freeze: T_e ≤ 1 h | fails |
| tail slack S_90 (descriptive) | 4.00 [1.26, 7.33] | — | — |
| activity ratio R (P2) | R = 0.31; Ā_ss = 0.39/h in the settled window | ≥ 3 | fails |
| Σ_ex,min = 2W atanh(1/S) (nats/agent) | 1.12 | — | — |
| ε (log t_i on log r_i; P4 input) | 2.02 ± 0.74 (n 15); with commit control 1.21 ± 0.41 | F −0.53, A −0.86 | uninformative (SE > 0.7) |

## Scorecard (period-specific axes)
- C: S separates freeze from churn here; the bootstrap CI is wide.
- D: the field-limited prediction (P1, P3) fails; the instant-freeze rival R2 fits.

## Notes
- Reading: a near-freeze from scratch (S 1.40 at T_e = 0.5 h; 16 committing agents of 21), followed by a churn tail (S_90 4.0, T_90 6.3 h). W_∅ counts every first commit as a move, so W is an upper bound on the true re-allocation.
