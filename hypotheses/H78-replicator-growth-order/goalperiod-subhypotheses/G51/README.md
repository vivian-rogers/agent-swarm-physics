# H78 × G51: Maximize your private assigned role (2026-07-06 → 09-04 (non-holdout))

**Verdict:** failed
**Role:** replication
**Period:** regime III · private roles, own artifacts · 21–32 agents · #general (+ #focus in 51g) · 45 non-holdout days. Units 51a–51l (51m is holdout).

## Why this period
Private roles: own repos, 12 non-holdout units, the largest count of recruitments (258).

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list, plus this period's aggregate counts from the built tables (recruitments, births, switch-outs, expiries; listed below) used to calibrate the synthetic worlds. No σ*, fitness, order or step statistic had been computed on this period. Counts: 258 recruitments, 828 births, 801 switch-outs, 263 expiries/leaves.

- Pooled p̂ ≤ 0.7 (0.35).
- Against: pooled p̂ > 0.7 with CI above 0.7.

## Result
*Run 2026-10-04 (non-holdout days only; host expiry E = 100).*

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| pooled p̂ ≤ 0.7 | 1.94 [1.22, 2.67] (271; 8 units, τ² = 0.69); whole-period fit 2.38 | neutral 1.07; fitness-spread worlds (p = 1): σ_A = 0.5 → 1.54, σ_A = 1.0 → 2.73 | failed (CI above 0.7) |
| A0 step | calibrated: share 0.10 → 0.06 at 38 active h (surrogate p = 0.005); new-repo rate 3.9× the mean | — | (the named share is small in #51) |

Robust across variants: E 2.07/1.98/2.10/1.98; B 1.88/1.99; wall 2.13; conditional logit 2.10 [1.72, 2.49]; cross-lab 2.43 [2.09, 2.77]; first-time recruits 2.44 [1.30, 3.58]. Repo FE 0.18 [−0.17, 0.52] (FE is biased −0.9 under p = 1 in the synthetic). Reading: superlinear *between* repos, consistent with first-order copying plus repo fitness spread (σ_A between 0.5 and 1.0), not with conformism. Touch classes: return 214, read 72, self 13, blind 0. Data: `data/processed/H78-replicator-growth-order/GG51/`, results `.../results/GG51.json`.

## Scorecard (period-specific axes)
- C: 0 (bracketed by the fitness-spread null). F: 1 (stable across variants). H: 0 (cannot beat the fitness rival).

## Notes
- 2026-10-04: folder created by the round-1 agent.
- 2026-10-04: amendment A1 (card) moved the primary host expiry from E = 300 to E = 100 before this period was run; the counts quoted under Prediction are at E = 300. A2 (post hoc) added the touch-based impostor class, the fitness-spread null worlds and the AR(1) surrogate null for the A0 step test.
