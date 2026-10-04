# H87 × NE34: the kickoff row (goal changes as scrambles of the standing goal field)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** dense-git non-holdout goal boundaries from #30 on (H70's nights N): new-goal nights vs within-goal nights; the #39 → #40 continuation boundary reported separately.

## Why this period
A goal change replaces the kickoff field for every agent at once. It is the kickoff channel's natural scramble (the HH's "kickoff change").

## Prediction
*Written 2026-10-04 ~20:07 UTC. H70's NE34 numbers (I_A 0.49 within vs 0.12 at new-goal nights) were seen.*
- I_K = I_within(X⁺; A⁻) − I_newgoal(X⁺; A⁻), paired bootstrap over agent-days; ΔV_K = scramble cost of a new-goal night (agent FE).
- **P6:** I_K ≥ 0.2 bits; κ_K's CI includes 0 (R3: the field carries bits, not commits).
- *Counts against:* I_K < 0.1 bits, or κ_K's CI excludes 0.

## Result
*Run 2026-10-04 20:51 UTC (`analysis/run.py`, block `NE34_K`); nights N with an own artifact and ≥ 10 calls of window; 98 new-goal nights vs 1,691 within-goal nights; strata agent; bootstrap B = 300 over 107 PT days.*
- I_within(X⁺; A⁻) = 0.50 bits; I_newgoal = 0.14 bits; **I_K = 0.36 bits [−0.05, +0.79]** (not identified under A1).
- ΔV_K (scramble cost of a new-goal night) = −0.29 commits per 20 calls [−1.46, +0.32]; ΔV_rel −0.33 [−1.72, +0.35] (output tends to be higher on a new goal's first day); V40 −0.39 [−1.67, +0.26].
- κ_K = −0.8 [−16.5, +0.7]; undefined in 7% of draws.
- P6: I_K ≥ 0.2 bits holds at the point estimate (0.36) but its CI includes 0; κ_K's CI includes 0. Partial.

**Reading.** A goal change removes about a third of a bit of allocation information carried by the agent's last repo (the field "keep working on what you were working on"), and does not cost commits; if anything the new goal's first day is busier. The kickoff field steers which repo, not how much work. Consistent with R3 (field dominance: bits, not commits), but day-level resampling leaves the bits unidentified.

## Scorecard (period-specific axes)
- **E:** the goal change is an operator-set scramble of the standing field; 8 boundaries.
- **I:** the #39 → #40 continuation boundary (15 nights) is excluded, not tested.
