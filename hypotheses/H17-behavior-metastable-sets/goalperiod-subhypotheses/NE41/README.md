# H17 × NE41: Forced erasures as quasi-random kicks (G51 primary, G38 secondary)

**Verdict:** failed
**Role:** native
**Period:** regime III · G51 non-holdout days 07-06 → 09-04 (14,544 forced erasures; 109k in-span windows) and G38 (2,311 forced erasures). Natural experiment NE41: the scaffold erases the context at the 41-turn cap, so the timing of an erasure is set by the scaffold, not the agent.

## Why this period
An MSM's slowest implied timescale should be the relaxation time after any perturbation. NE41 supplies thousands of perturbations at scaffold-set (quasi-random) times, so the MSM can be tested on a statistic it was not fitted to (axis D) and against an intervention (axis E). Only regime III has forced erasures; G51 has the most.

## Prediction
*Written 2026-10-04, before running (card, "Round 1b", N1).* After a forced erasure (the first call flagged `reset_forced` in `context_ledger_turns`), the mean v3 macro-state vector (deviation from the agent's own mean) in windows k = 1…4 relaxes; the TV distance d(k) decays with τ_relax = −5 min / slope(ln d(k) on k) within [0.5, 2] × t2\*_bc of the same period. Control anchors: mid-segment calls (`ctx_pos` ≥ 15, no reset). Events censored at the next consolidation or segment end. Credence 0.7 for a measurable transient (d(1) above control, agent-day bootstrap CI), 0.35 for the factor-2 agreement.

## Result
*Run 2026-10-04 (`analysis/native_r1b.py`; `data/processed/H17-behavior-metastable-sets/r1b/native_r1b.json`; figure `../../figures/r1b_summary.pdf`, panel b).*

| | G51 | G38 |
| --- | --- | --- |
| d(k), k = 0…4 after forced erasure | 0.14, 0.16, 0.10, 0.02, 0.11 | 0.09, 0.11, 0.05, 0.08, 0.15 |
| d(k) after control anchors | 0.16, 0.03, 0.13, 0.22, 0.25 | 0.09, 0.03, 0.16, 0.25, 0.28 |
| d(1) forced − control (95% CI) | [0.10, 0.14] | [0.05, 0.10] |
| slope of ln d, k = 1…4 (95% CI) | −0.23 [−0.33, −0.09] → τ_relax ≈ 21 min | +0.15 [−0.04, 0.34] (no decay) |
| MSM t2\*_bc | 263 min | 230 min |
| τ_relax / t2\*_bc | 0.08 | n/a |
| Verdict | transient yes; factor 2 **failed** | transient yes; **failed** |

The erasure signature is a re-orientation: self_maintenance is up in the erasure window (+0.07 in G51) and work is up one window later (+0.11). It is gone within about 20 min, an order of magnitude faster than the MSM's slowest mode, so t2\* is not the system's relaxation time after the scaffold's kicks; it is the slow agent/day mixture.

## Scorecard (period-specific axes)
D 0 (the unfitted relaxation misses by ×12). E 0 (the intervention response is not what the model predicts). G 1 (erasures do perturb the behavior state, as H15/H39/H46 found).

## Notes
- The control anchors are mid-segment calls, which are active windows by construction (less `wait` than the agent mean), and censoring at the next consolidation leaves mostly long idle stretches by k = 3–4, so the control curve rises. Both curves carry this selection after k ≈ 2; the k = 1 contrast is the cleanest number.
