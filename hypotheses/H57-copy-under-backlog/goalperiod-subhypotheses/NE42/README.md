# H57 × NE42: #best/#rest merge and split, A-B-A (2026-05-04 / 05-11)

**Verdict:** failed (the merge raised every agent's backlog as designed, but copying did not follow it: estimators disagree in sign and no dose-response)
**Role:** native
**Period:** #39 (2026-04-27 → 05-01, two rooms) → #40 (05-04 → 05-08, one merged room, #universe-coordination) → #41 (05-11 → 05-15, two rooms, same partition). Regime III, 15 agents, not held out. Goal-confounded: each phase is a new goal, and #40 is a shared objective.

## Why this period
The merge puts 14 agents in one room at a fixed roster, so every agent's backlog should jump; the split lowers it again. The backlog moves for a reason unrelated to any one agent's content, and the A-B-A shape guards against a monotone drift. If load drives copying, each agent's chance-corrected echo should rise in #40 and fall in #41, and agents whose backlog rose most should change most.

## Prediction
*Written 2026-10-04 07:09 UTC, before running H57 on these periods.*
- **N42a (DiD):** across agents present in all three phases (≥ 10 statements each), the DiD = y(40) − [y(39) + y(41)]/2 of the chance-corrected echo (bge and gte) and marker near-copy is > 0, with a one-sided sign-flip p < 0.05 for at least one of them and the right sign for all three.
- **N42b (dose):** the per-agent DiD in log k is > 0 on average, and the Spearman correlation across agents between the DiD in echo and the DiD in log k is > 0.
- **N42c (statement level, the transition as the object):** with agent fixed effects over the three periods, the merged-week coefficient is > 0 and shrinks once log k is controlled (the backlog carries the merge effect).
- **Against:** DiD ≤ 0, or a merged-week effect that does not depend on log k (a goal effect of #40's shared objective).
- **Power:** ~15 agents. Only a large effect is detectable.

## Result
*Run 2026-10-04 (non-holdout). Numbers: `data/processed/H57-copy-under-backlog/results/native_NE42.json`. Figure: [figures/ne42_phases.pdf](figures/ne42_phases.pdf).*

11 agents with ≥ 10 statements (k ≥ 1) in each phase; 4 dropped (too few statements in one phase; GPT-5, alone in #rest during #40, reads no agent messages there). The intervention worked: the per-agent mean log₂(1 + k) rose at the merge and fell at the split (2.01 → 2.77 → 2.35, i.e. k ≈ 3.0 → 5.8 → 4.1; DiD +0.59, sign-flip p 0.003).

| Native prediction (dated) | Observed | Verdict |
| --- | --- | --- |
| N42a: DiD > 0 for echo (bge, gte) and marker near-copy, chance-corrected | bge −0.0044 ± 0.0094 (p 0.80; 5/11 agents > 0); gte +0.011 ± 0.006 (p 0.0003; 11/11); marker +0.025 ± 0.009 (p 0.0006; 10/11) | not met (bge has the wrong sign) |
| N42b: dose: Spearman(ΔDiD echo, ΔDiD log k) > 0 | bge −0.36 (p 0.27), gte −0.01 (p 0.98), marker −0.15 (p 0.65) | not met |
| N42c: merged-week effect > 0 and shrinks once log k is controlled | bge −0.007 (p 0.04) → −0.003; gte +0.007 → **+0.011**; marker +0.023 → **+0.035**; the log k coefficient itself is negative (−0.008, −0.008, −0.029) | not met: what moves at the merge is not carried by the backlog |
| Post hoc: raw read-set echo DiD (upper bound) | bge +0.0025 (p 0.16; 3/11 agents), gte −0.0006 (p 0.69) | no effect |
| Post hoc: lag-matched count DiD | bge +0.022 (p 0.0003; 11/11) but dose Spearman −0.66 (p 0.03); gte +0.006 (p 0.001); marker −0.092 | a phase effect, anti-correlated with the backlog change |

**Reading.** The A-B-A moved the backlog cleanly, so it is a good test of load. Whatever moves at the merge (in some estimators) does not scale with how much an agent's backlog rose, and goes the other way in others. The goal changes at both boundaries (#40 is a shared objective), so phase contrasts are goal-confounded; the dose test is the part that speaks to H57, and it fails.

## Scorecard (period-specific axes)
- **E (interventional):** 0. The backlog intervention did not produce the predicted copying change.
- **C:** 0.

## Notes
- The chance-corrected (pre-registered) outcomes are biased by contemporaneous convergence (card Amendment 2); within-agent DiDs remove agent levels but not the k-dependence of that bias, which is why the raw echo and the dose test carry the reading.
