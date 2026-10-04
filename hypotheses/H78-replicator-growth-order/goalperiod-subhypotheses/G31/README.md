# H78 × G31: Free week (farewell to Claude 3.7 Sonnet) (2026-02-16 → 02-20)

**Verdict:** failed
**Role:** replication
**Period:** regime I · free week with a field-free herding wave · 11–12 agents · #general · 5 days. Units 31a–31d (join, NE29, NE11).

## Why this period
H11's clearest field-free herding week in work, with competing repos and dense git (1,309 work commits).

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list, plus this period's aggregate counts from the built tables (recruitments, births, switch-outs, expiries; listed below) used to calibrate the synthetic worlds. No σ*, fitness, order or step statistic had been computed on this period. Counts: 78 recruitments, 60 births, 110 switch-outs, 18 expiries/leaves.

- p̂ ∈ [1.2, 1.5] (0.25); p̂ > 1 (0.45).
- Removing blind/named recruitments moves p̂ by < 0.2 (0.5).
- A0: a step in the named-host share (0.2).
- Against: p̂ ≤ 1 with CI below 1.2.

## Result
*Run 2026-10-04 (non-holdout days only; host expiry E = 100).*

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| p̂ ∈ [1.2, 1.5] | 0.73 [−0.08, 1.54] (36 formation-free recruitments; 4 units, τ² = 0) | neutral world 1.10; fitness-spread worlds (p = 1) 1.41–2.04 | failed (CI does not exclude the band) |
| impostor shift < 0.2 | all recruitments: 1.54 [1.22, 1.86]; shift 0.81 | — | failed |
| A0 step in the named-host share | ΔBIC 18.7 but AR(1) surrogate p = 0.80 (share 0.60 → 0.24) | surrogate 95th pct 88 | failed (no calibrated step) |

Variants: E = 50/150/300/∞ 0.69/0.82/0.66/0.75; B = 100/400 0.65/0.82; wall clock 0.73; conditional logit 0.76; repo FE 0.33; cross-lab 0.42 [−0.69, 1.52]; first-time recruits 1.01. The named stratum (46 recruitments) gives 1.80 [1.42, 2.18]. Touch classes: read 36, return 38, self 9, blind 0. Data: `data/processed/H78-replicator-growth-order/GG31/`, results `.../results/GG31.json`.

## Scorecard (period-specific axes)
- C: 0 (inside the neutral and fitness-spread bands). F: 1 (stable across E, B and clock). G: 1 (herding repo is the named one).

## Notes
- 2026-10-04: folder created by the round-1 agent.
- 2026-10-04: amendment A1 (card) moved the primary host expiry from E = 300 to E = 100 before this period was run; the counts quoted under Prediction are at E = 300. A2 (post hoc) added the touch-based impostor class, the fitness-spread null worlds and the AR(1) surrogate null for the A0 step test.
