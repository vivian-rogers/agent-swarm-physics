# H75 × G44: #best fine-tunes a leader; #rest picks its own goals (2026-05-26 → 05-29)

**Verdict:** supported
**Role:** native (exploratory)
**Period:** regime III · 18 agents (4 in #best, 12 in #rest; DQ6 room_assignment) · 4 days, 16.2 active h · the previous week #43 is held out, so W_∅ only; horizon = the whole period (16 h, settled window = last 4 h).

## Why this period
- Two fields on the same days and scaffold: #best has one named, shared target; #rest has none (each agent chooses). If settling is field-limited, the room with the named target settles at least as fast whatever its switch rate; if activity-limited, the T ratio follows the inverse Ā ratio.

## Prediction
*Written 2026-10-04 ~20:15 UTC, after the synthetic validation (amendment A1), before running on this period.*
- N1: T_e(#best) ≤ T_e(#rest), and the activity-limited ratio T_rest/T_best = Ā_best/Ā_rest misses by ≥ ×2 or has the wrong sign → supported. T_e(#best) > T_e(#rest) → failed. Weak: 4 agents in #best. Credence 0.45.

## Result
*Run 2026-10-04 ~20:50 UTC (`analysis/run.py: native_g44`; `data/processed/H75-reallocation-speed-limit/G44/results_native.json`).* Horizon 16 active h, W_∅.

| Room | N committing | T_e (h) | Ā (switches/agent/h) | S (95% CI) | T_90 (h) | S_90 |
| --- | --- | --- | --- | --- | --- | --- |
| #best (named shared target) | 4 | 0.75 | 3.33 | 2.50 [1.00, 33.50] | 9.50 | 17.25 |
| #rest (free choice) | 10 | 4.25 | 3.41 | 14.50 [4.26, 27.86] | 12.50 | 26.90 |
| both rooms | 15 | 6.50 | 2.19 | 15.29 [5.57, 25.30] | 10.50 | 20.73 |

- T_rest / T_best = 5.67; the activity-limited rival predicts Ā_best / Ā_rest = 0.98. It misses by ×5.8.
- **Verdict: supported.** At equal switch rates (3.3 vs 3.4 per agent-hour), the room with a named, shared target settles 5.7× faster and close to the bound (S 2.5); the free-choice room spends 14.5 switches per net move. The field, not the switch rate, sets the settling time.
- Weak: 4 committing agents in #best; the bootstrap CI of S in #best spans 1.0–33.5.

## Scorecard (period-specific axes)
- E (quasi-intervention): two fields on the same days and scaffold; consistent with field-limited settling.
- G: room membership from DQ6 ground truth.
