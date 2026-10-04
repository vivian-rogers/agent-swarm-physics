# H02 × G45: Follow your leader (2026-06-01 → 06-05)

**Verdict:** failed
**Role:** confirmatory (locked holdout)
**Period:** regime III · leader week (the operators installed a fine-tuned leader, roster agent 30) · 18 agents in the present population · 5 days · rooms #best/#rest.

## Why this period
The only goal period with a ground-truth leader. If directed couplings inferred from activity reflect influence, the assigned leader should top the net-outgoing-influence ranking.

## Prediction
Pre-registered in the main card ("Prediction", #45) and frozen in `analysis/confirm_45.py` (FROZEN settings), committed in e9bf2f7 before the run: **PASS if the leader ranks #1 by net outgoing influence I_k (KI-1 block estimator) and its z against the N1 surrogate is ≥ 2.** The round-1 credence was ~25% pass.

## Result (run 2026-10-03; `data/processed/H02-couplings-are-real/confirm_45.json`)
| Test | Result | Verdict |
| --- | --- | --- |
| **Primary: KI-1 block, active spin** | leader rank **4/18**, I = 0.19, **z = 0.76** (top: agent 18, z = 1.90) | **FAIL** |
| KI-5 block | rank 16/18, z = −0.91 | — |
| #best room only (N = 6) | rank 1, z = 1.28 | below z = 2 |
| Talk spin (N = 12) | rank 5, z = 0.41 | — |
| Held-out mean-field test | z21 = 1.26 (predicted ≥ 2) | fail |
| Leader–follower MF (MF-P6) | asymmetry ranks 1st but z = 0.27; J_lf ranks 9th | fail |
| Curie–Weiss | βJ₀ = 0.41, z = 6.5 | strong collective co-activation |

## Notes
- Leadership is not visible in 1-minute activity timing. Look for it in message content and replies (H01 D3.2; a Hawkes model on talk events).
