# H77 × G31: Free week (farewell to Claude 3.7 Sonnet) (2026-02-16 → 02-20)

**Verdict:** failed
**Role:** replication
**Period:** regime I · free week with a field-free herding wave · 11–12 agents · #general · 5 days. Units 31a–31d (join, NE29, NE11).

## Why this period
H11's clearest shared-artifact herding week in work (z_N2 +7.2; 9 agents on one repo in one window), with 37 repos competing: many rivals to test the resolution bound.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list, plus this period's aggregate counts from the built tables (recruitments, births, switch-outs, expiries; listed below) used to calibrate the synthetic worlds. No σ*, fitness, order or step statistic had been computed on this period. Counts: 78 recruitments, 60 births, 110 switch-outs, 18 expiries/leaves.

- σ* of the top repo ≥ 1 nat (credence 0.45).
- Resolution: ≥ 90% of testable extinct rivals have ŝ ≥ e^{−σ*}, above the permutation null (0.30).
- A0: nucleus ≠ winner (0.50); ≥ 1 frustrated herd (0.50).
- Uncopying order |q − 1| < 0.3 (0.45).
- Against: σ* < 1, or a resolution fraction at the permutation null.

## Result
*Run 2026-10-04 (non-holdout days only; host expiry E = 100).*

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| σ* ≥ 1 nat | 0.89 [−0.36, 2.13] (J⁺ 8, J⁻ 3, dilution 11; top repo n_max 10) | neutral world 95th pct 1.10 | failed |
| resolution fraction ≥ 0.9 | untestable: the top repo gets no formation-free recruitment (f_T = 0); the top repo is kickoff-named | — | n/a |
| nucleus ≠ winner | true (mechanical: the top repo is named, the nucleus is formation-free) | — | supported (uninformative) |
| ≥ 1 frustrated herd | 3 repos reached ≥ 3 hosts and died | — | supported |
| \|q − 1\| < 0.3 | q = 0.59 [0.24, 0.95] (70 switch-outs) | neutral-world q̂ 0.78 | failed |

σ* depends on the loss convention: 1.73 (E = 50), 0.89 (E = 100), 0.00 (E = 150), −0.55 (E = 300). Data: `data/processed/H77-repos-as-replicators/GG31/`, results `.../results/GG31.json`.

## Scorecard (period-specific axes)
- C: 0 (σ* inside the neutral band). F: 0 here (sign changes with E). G: 1 (top repo is the kickoff-named one).

## Notes
- 2026-10-04: folder created by the round-1 agent.
- 2026-10-04: amendment A1 (card) moved the primary host expiry from E = 300 to E = 100 before this period was run; the counts quoted under Prediction are at E = 300. A2 (post hoc) added the touch-based impostor class, the fitness-spread null worlds and the AR(1) surrogate null for the A0 step test.
