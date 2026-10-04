# H75 × G39: Build your own interactive world (2026-04-27 → 05-01)

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** regime III · 15 agents · #best / #rest (reshuffled on day 1) · 5 days, 20.2 active h.

## Why this period
- Each agent builds its own world, so the kickoff moves every agent to a new private repo: W_pre should be large (≥ 0.7). Previous week #38 is non-holdout, so W_pre is available.
- Dense agent-work commits (DQ4), regime III, horizon 20 active h after the kickoff (W_pre (primary) and W_∅).

## Prediction
*Written 2026-10-04 ~20:15 UTC, after the synthetic validation (amendment A1), before running on this period.*
- P0: ĀT ≥ W (scheme check).
- P1 (templated from the card): S(T_e) ≥ 3 with agent-bootstrap lower bound ≥ 2 → supported; S ≤ 2 → failed. After A1, "supported" means churn-dominated settling, not an instant freeze (R2); it does not separate field from activity limitation.
- P3: T_e in [2.5, 10] active h. R2 predicts T_e ≤ 1 h.
- P4 (enters the pooled test only): ε per period, read against the synthetic means (F −0.53, A −0.86).

## Result
*Run 2026-10-04 ~20:50 UTC (`analysis/run.py`; data `data/processed/H75-reallocation-speed-limit/G39/results_*.json`; figure `../../figures/summary_obs.pdf`).* N = 14 committing agents; median call rate 133 calls per active hour; D(0) = 1.00, settled floor D_f = 0.01.

| Prediction | Observed (agent-bootstrap 95% CI) | Null / rival | Verdict |
| --- | --- | --- | --- |
| P0 bound ĀT ≥ W | violations: none | counting identity | holds (scheme check) |
| P1 slack S(T_e) ≥ 3, boot lower ≥ 2 | S = 1.00 [1.00, 1.00]; W = 0.79, Ā = 3.14 switches/agent/h | synthetic F/A ≈ 4.5, Z ≈ 1.15 | fails |
| P3 T_e in [2.5, 10] h | T_e = 0.25 h [0.25, 0.50]; T_90 = 2.75 h [0.25, 6.00] | R2 instant freeze: T_e ≤ 1 h | fails |
| tail slack S_90 (descriptive) | 1.15 [1.00, 1.43] | — | — |
| activity ratio R (P2) | R = 0.01; Ā_ss = 0.04/h in the settled window | ≥ 3 | fails |
| Σ_ex,min = 2W atanh(1/S) (nats/agent) | diverges (S = 1: every switch directed) | — | — |
| ε (log t_i on log r_i; P4 input) | -2.21 ± 1.47 (n 14); with commit control -1.82 ± 1.26 | F −0.53, A −0.86 | uninformative (SE > 0.7) |

The from-scratch variant (W_∅) gives S = 1.00 [1.00, 1.00], T_e = 0.25 h.

## Scorecard (period-specific axes)
- C: S separates freeze from churn here; the bootstrap CI is tight.
- D: the field-limited prediction (P1, P3) fails; the instant-freeze rival R2 fits.

## Notes
- Reading: an instant freeze. 79% of the agents are on their settled repo within the first 15 active minutes, each with exactly one switch (S = 1.00): the move saturates the speed limit. W_pre equals W_∅ because no pre-kickoff repo survives into the settled allocation.
