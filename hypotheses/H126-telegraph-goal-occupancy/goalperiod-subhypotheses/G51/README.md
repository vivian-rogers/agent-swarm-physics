# H126 × G51: goal #51, private goals (2026-07-06 → 2026-09-06, head units 51a–51l)

**Verdict:** supported
**Role:** exploratory (native)
**Period:** regime III · mode I/K · 21 agents · private goals and roles · units 51a–51l (the #51 tail is held out).

## Why this period
Each agent has its own private goal (`agent_goal`), so each agent has its own field. #51 has the most statements per agent of any period and the longest run of stationary assignments: the best-powered test of the dwell shape, and the only period where per-agent rates can be compared across units (an agent-level property, exception (b)).

## Prediction
*Written 2026-10-04 ~22:25 UTC, before running on this period.*
**Native N2:** along each agent's own goal direction (own decoy threshold), P1's exponential rule holds in ≥ 2/3 of the 12 units, and per-agent ln k_on is stable across consecutive units (median Spearman across agents ≥ 0.3). Credence 0.35. Counts against: heavy-tailed in > ½ of units, or median Spearman ≤ 0.
P2 (occupancy within 20%) is also computed per unit.

## Result
*Run 2026-10-04 (UTC), after Amendment A1 (the shape test has no power, so N2's first clause is descriptive).*

| Unit | agents | statements | P1 dLL vs N0 q95; CV max | P2 ρ_p | p_win | τ_on / τ_off (calls) | q₀ / q₁ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | 20 | 5529 | +0.0057 vs 0.0006; 3.41 (heavy) | +0.01 | 0.40 | 143.2 / 94.2 | 0.056 / 0.66 |
| 51c | 24 | 6793 | +0.0105 vs 0.0000; 2.44 (heavy) | -0.01 | 0.27 | 23.6 / 317.3 | 0.044 / 0.66 |
| 51d | 23 | 7676 | +0.0037 vs 0.0004; 2.13 (heavy) | +0.17 | 0.27 | 32.3 / 437.8 | 0.058 / 0.61 |
| 51e | 24 | 4057 | +0.0052 vs 0.0002; 1.98 (exponential) | -0.03 | 0.23 | 10.9 / 50.8 | 0.037 / 0.56 |
| 51f | 24 | 6637 | +0.0018 vs 0.0003; 2.33 (heavy) | -0.09 | 0.25 | 18.4 / 432.8 | 0.054 / 0.70 |
| 51g | 27 | 17845 | +0.0066 vs 0.0000; 3.77 (heavy) | -0.03 | 0.27 | 48.0 / 407.1 | 0.043 / 0.70 |
| 51h | 21 | 4704 | +0.0020 vs 0.0004; 1.82 (exponential) | -0.07 | 0.25 | 8.3 / 41.8 | 0.008 / 0.72 |
| 51i | 17 | 2140 | +0.0034 vs 0.0015; 3.09 (heavy) | -0.03 | 0.24 | 2.4 / 12.9 | 0.029 / 0.85 |
| 51j | 19 | 2242 | -0.0009 vs 0.0015; 1.86 (exponential) | -0.03 | 0.34 | 5.2 / 14.7 | 0.022 / 0.83 |

Exponential by the P1 rule in 3/9 units (uninformative after A1). Per-agent ln k_on stability across consecutive units: median Spearman 0.61 over 8 unit pairs (ln k_off: 0.58).

## Scorecard (period-specific axes)
B: stationarity of per-agent rates across units (agent-level property, exception (b)); F: shape not identifiable (A1).
