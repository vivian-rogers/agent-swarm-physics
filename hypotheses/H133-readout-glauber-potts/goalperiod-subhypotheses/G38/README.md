# H133 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-24)

**Verdict:** pending
**Role:** exploratory (replication, native N1)
**Period:** regime III · mode C · 12 agents · 17 non-reserved active days. Units: 38a, 38b, 38c, 38d, 38e (`period_units`).

## Why this period
Units meeting the structural precondition (>= 30 project hops (call) and >= 20 named reads about a project other than the reader's current one; counted 2026-10-07 before any outcome): 38a (1744 hops, 178 named reads about another project).
Units below the precondition (not tested): 38b, 38c, 38d, 38e.
Role: native N1 (within-project-hour contrast; G38 is split into units 38a-38e, of which only 38a meets the precondition).

## Prediction
*Written 2026-10-07, before running H133 on this period.*
- Regime III. Card P1: gamma_nam > 0 with bootstrap CI > 0 and N1 p < 0.05. P2: gamma_un CI includes 0 and Delta-gamma = gamma_nam - gamma_un has CI > 0. P3: gamma_nam - gamma_if > 0. P4: eta_sw CI includes 0 and excludes 1.
- Native N1 (credence 0.4): P1-P3 hold in the within-project-hour contrast; counts against: gamma_nam CI includes 0 at power >= 0.8.
- Verdict rule for this folder: supported if the period's predictions hold; failed if a kill-rule quantity fires here; descriptive if a test is unpowered by the synthetic check (power < 0.8) or a term is not estimable (< 5 chosen rows with a read).

## Result
Not run yet.

## Scorecard (period-specific axes)
Filled after the run.

## Notes
- 2026-10-07: folder and prediction written before any H133 outcome statistic on this period (only the structural counts above were computed).
