# H134 × NE41: forced consolidation at the 41-call cap, as a reset inside a project visit (G51 primary, G38 second)

**Verdict:** failed
**Role:** exploratory (native N1)
**Period:** regime III. G51 units 51a–51l (non-reserved; 7,777 forced resets inside visits with d ≥ 10) and G38 units 38a, 38b, 38e (1,179). The cap times the reset, not the agent (NE41).

## Why this period
A forced reset sets the project self-share f_proj to 0 at fixed dwell. The urn predicts a leave step of −β_F ln(1 − f_pre). R-store (H70, H44) predicts no step.

## Prediction
*Written 2026-10-07, before running H134 on these periods.*
- N1: in G51, the observed Δ_reset (MH log odds ratio of leaving at the first call after a forced reset vs matched non-reset calls; strata agent × dwell decile × f_pre decile) is > 0 with CI > 0, and observed/predicted lies in [0.5, 2]. The pseudo-reset placebo (20 own calls earlier) has a CI that contains 0.
- Kill C: Δ_reset's CI includes 0 at synthetic power ≥ 0.8 for the urn's predicted step.
- G38: the same contrast, reported as the second period.

## Result
Run 2026-10-07 (`analysis/run.py`, `analysis/summarize.py`; post hoc `analysis/posthoc.py`). A forced reset raises leaving, but about 24 times more than the urn predicts.

| Quantity | G51 (12 units) | G38 (38a, 38b, 38e) |
| --- | --- | --- |
| forced resets inside visits, d ≥ 10 | 7,762 | 1,173 |
| Δ_reset (pooled MH log OR) | +0.40 [+0.25, +0.54] | +0.38 [-0.11, +0.87] |
| urn prediction −β_F ln(1 − f_pre) | +0.016 | -0.010 |
| observed / predicted | 24 | n/a (prediction ≤ 0) |
| pseudo-reset placebo (20 calls earlier) | -0.02 [-0.19, +0.14] | -0.14 [-0.69, +0.40] |
| post hoc: sustained leaves only (flickers A → B → A within 5 calls removed) | +0.46 [+0.30, +0.62] | +0.59 [+0.07, +1.11] |
| synthetic power at the urn's step (β_F = 1) | 0.52 | 0.23 |

- **N1 fails:** Δ_reset > 0 with CI > 0 and the placebo CI contains 0, but observed/predicted is 24, outside [0.5, 2]. Even with β_F = 1 the urn's step is about +0.10 (synthetic W1), so the observed step is about 4× that.
- **Kill C does not fire:** the step is positive. (A7 declared Kill C unpowered for a null result.)
- **R-store's "no step" is rejected** in G51 (synthetic size of the step in W4: 0.04).
- Reading: a forced erasure releases an agent from its project as a step, not as the urn's dose. This matches H69 (loops end as a step) and H16 (escape step 4.6× the urn).
