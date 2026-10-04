# H02 × NE14: regime II → III (2026-03-24), collective coupling βJ₀ with and without the day-edge adjustment

**Verdict:** failed
**Role:** native
**Period:** last regime-II days (#35, #36 on 03-23) vs first regime-III days (#36 from 03-24, #37), N = 12 per side. Transition exception (c). H02's own chunks contain no regime-II week (card), so this boundary test uses H19's NE14 computation of the same Curie–Weiss estimator (βJ₀ = g / q, 30-min blocks, H02 population rule).

## Prediction
*Not blind (disclosed): computed 2026-10-04 06:37 UTC in round 1b; the prediction is H38's published round-1 result:* the regime II → III rise in collective co-activation is significant on the whole-day grid and vanishes under the DQ8 trim and H38's agent-state conditioning. Verdict rule for H02-MF's round-1 reading ("collective coupling concentrates in regime III"): **supported** if the adjusted rise excludes 0; **failed** otherwise.

## Result
Source: `data/processed/H19-loop-gain-collapse/r1b/NE14/result.json` (`hypotheses/H19-loop-gain-collapse/analysis/r1b_ne14.py`).

| Activity spins | Old tables: ΔE (g units) | Δβ J₀ | Fixed tables: ΔE | Δβ J₀ |
| --- | --- | --- | --- | --- |
| whole grid (round-1 definition) | +0.145 ± 0.083 | +0.27 | +0.112 ± 0.177 | +0.16 |
| DQ8 trim + stall mask | −0.024 ± 0.117 | −0.05 | −0.080 ± 0.214 | −0.23 |
| H38 agent-state conditioning | −0.062 ± 0.132 | −0.13 | −0.140 ± 0.280 | −0.21 |

- **Verdict: failed.** The regime-III collective coupling of round 1 is the operator's day edges; across the switch itself the adjusted βJ₀ does not rise. This matches the replication layer: under the corrected null, regime-III βJ₀ is significant in 2/8 chunks (#38c1, #44) against 7/13 in regime I.
