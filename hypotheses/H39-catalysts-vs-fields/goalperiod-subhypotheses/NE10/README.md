# H39 × NE10: Auto-nudger switched on (first nudges 2026-02-13, #30)

**Verdict:** failed
**Verdict (1b):** mixed (V4 neither, Δπ_wait wrong sign)
**Role:** native (round 1b: the step on the Jev v3.1 state space; round-1 role: exploratory spanning test)
**Period:** see Prediction for the windows; non-holdout days only.

## Why this test
A dated scaffold change inside a goal period: a quasi-intervention on every agent.

## Prediction
*Written 2026-10-04 (UTC), before running this test.* P7 (card): within #30, 02-11 and 02-12 (no nudges) vs 02-13 (first nudges): Δπ_idle < 0 and idle escape up (the P1 direction), **not** significant at step level (one post day; placebo shape 2 + 1). HH52's check (idle escape rate vs stationary idle fraction) is answered mainly by the nudge point-lever units (P1); NE23 (off/on) is held out for confirmation.

## Result
**Step NE10** (auto-nudger switched on (first nudges 02-13); pre 2026-02-11, 2026-02-12 → post 2026-02-13; 11 agents in the balanced panel; placebo pool: era I-4h, n = 58).

| State family | class | φ (percentile in placebo) | K (percentile) | Δπ |
| --- | --- | --- | --- | --- |
| behavior B4 | **neither** | 0.094 (21) | -0.067 (5) | work -0.009, chat -0.022, idle +0.035, consolidate -0.004 |
| content C6 | **neither** | 1.514 (85) | +0.222 (35) | (clusters) |

Prediction (P7): neither → observed neither. Direction: Δπ_idle +0.035 (predicted < 0: ✗). ✗

## Round 1b native test: the switch-on on the second state space (prediction)
*Written 2026-10-04 07:31 UTC, before any V4 statistic was computed for #30. Seen: the round-1 B4 result above (neither; idle +0.035).*

The same step (02-11, 02-12 → 02-13) on the Jev v3.1 states lumped to V4 (work, coord, wait, maint; soft 5-min transitions; card Round 1b), against the same-era day-boundary placebos computed on V4.
- **N1:** V4 class neither (one post day, 12 nudges spread over 11 agents).
- **N2:** direction: Δπ_wait < 0 (the P1 direction), not significant.
- **Verdict rule (native):** supported if N1 holds; mixed if N1 holds but N2's sign is wrong; failed if V4 shows a field or catalyst beyond the placebo band. Low information by design: the point is whether the round-1 B4 verdict survives a different state space.

## Notes
- Run 2026-10-04; placebos are within-goal day boundaries of the same era (regime × hours) and window shape, excluding ±1 day around the tested scaffold steps.

### Round 1b native result
*Run 2026-10-04 ~08:40 UTC (`analysis/r1b_native.py`; 73 same-era placebos).* B4: neither · K -0.067 (pct 7) · φ pct 16 · Δπ idle/wait +0.035 (pct 68) · escape idle/wait -0.213 (pct 11). V4: neither · K +0.026 (pct 41) · φ pct 3 · Δπ idle/wait +0.023 (pct 52) · escape idle/wait -0.080 (pct 49). N1 ✓ (neither), N2 ✗ (Δπ_wait +0.023): **mixed**.
