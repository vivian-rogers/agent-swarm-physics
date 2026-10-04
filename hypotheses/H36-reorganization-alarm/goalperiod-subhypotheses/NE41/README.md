# H36 × NE41: forced context erasure at the 41-turn cap (regime III), as a nuisance

**Verdict:** n/a
**Verdict (1b):** n/a
**Role:** exploratory (round 1, non-holdout)
**Period:** regime III, #37–#51 (non-holdout days)

## Why this test
NE41 is per-agent and asynchronous (turn-level), so it is not a swarm transition at day resolution. It is a candidate nuisance: days with more consolidations might look more 'reorganized'.

## Prediction
*Written 2026-10-04 01:51 UTC, before computing any statistic on real data.* Consolidations per present agent per day do not predict Z_phys on regime-III placebo days (|Spearman ρ| < 0.2) [0.7].

**Verdict rule:** Nuisance check: verdict 'n/a' (descriptive); pass if |ρ| < 0.2 or p > 0.05.

## Result
<!-- RESULT -->
Regime-III placebo days (n = 15): Spearman ρ(consolidations per present agent, Z_phys) = -0.31 (p 0.260); with Z_act: -0.34. Nuisance check passes (rule: |ρ| < 0.2 or p > 0.05).

**Prediction check:** held by the pre-registered rule (p > 0.05), but ρ = −0.31 with n = 15 is underpowered; consolidations, if anything, go with *lower* scores.
<!-- /RESULT -->

## Round 1b (improved data, 2026-10-04)
<!-- R1B -->
Round 1b tables (bge-small, restatements removed, fixed activity table):

Regime-III placebo days (n = 10): Spearman ρ(consolidations per present agent, Z_phys) = 0.55 (p 0.098); with Z_act: 0.30. Nuisance check passes (rule: |ρ| < 0.2 or p > 0.05).

gte-modernbert:

Regime-III placebo days (n = 10): Spearman ρ(consolidations per present agent, Z_phys) = 0.36 (p 0.310); with Z_act: 0.30. Nuisance check passes (rule: |ρ| < 0.2 or p > 0.05).
<!-- /R1B -->
