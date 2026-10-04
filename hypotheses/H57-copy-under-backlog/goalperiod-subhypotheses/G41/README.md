# H57 × G41: Novel research (NE42 split back) (2026-05-11 → 05-15)

**Verdict:** failed (pre-registered rule; the chance-corrected slopes are biased negative by contemporaneous convergence, card Amendment 2; raw-echo upper bound +0.0023 per doubling)
**Role:** replication
**Period:** 2026-05-11 → 05-15 · unit 41 · N 15 · 5 d, 20.1 act h · regime III · #best / #rest. Non-holdout statements with backlog k ≥ 1: 1800 by 15 agents.

## Why this period
Layer 1 (replication): the common H57 estimator on every eligible goal period, so the per-period slopes are comparable points on a phase diagram (copying vs backlog against period size, regime and median k). This folder is one such point, not an independent native test.

## Prediction
*Written 2026-10-04 07:09 UTC, before running H57 on this period. Templated replication prediction (layer 1), as the two-layer rule allows.*
- **P1:** the within-agent slope of the chance-corrected read-set echo on log₂(1 + k) is positive in both embedding models (β_echo,bge > 0 and β_echo,gte > 0).
- **P2:** the chance-corrected marker near-copy slope β_mk is positive.
- **P3:** the copy share of the near-coded addressed channel rises from the bottom to the top k tercile (T > 0).
- **Power:** at this size the slope SE is roughly 0.009 per doubling of k (scaled from the synthetic #40 worlds), so only slopes above ~0.026 are reliably detectable here. The synthetic load world plants ≈ 0.03.
- **Verdict rule (card):** supported if β_echo (both models) and β_mk are > 0 with at least one one-sided p < 0.05 and none significantly negative; failed if any of them is significantly negative or all are ≤ 0; mixed otherwise.
- **Against:** slopes ≤ 0, or significantly negative.

## Result
*Run 2026-10-04 (non-holdout). Numbers: `data/processed/H57-copy-under-backlog/results/G41.json`.*

n = 1800 statements with k ≥ 1 (15 agents, 5 days, 1 units); median k 4, q90 13. Read-set echo rate 0.0100 (bge), 0.0078 (gte); in-flight chance rate per pair 0.0020 (bge). corr(log k, first day) 0.081.

| Prediction (dated) | Predicted | Observed (95% CI) | Verdict |
| --- | --- | --- | --- |
| P1 β_echo, bge (chance-corrected) | > 0 | -0.0103 ± 0.0067 (p_cal 0.0131) | against (sig. < 0) |
| P1 β_echo, gte | > 0 | -0.0146 ± 0.0053 (p_cal 7.12e-06) | against (sig. < 0) |
| P2 β_mk (marker near-copy) | > 0 | -0.0564 ± 0.0133 (p_cal 6.77e-13) | against (sig. < 0) |
| P3 T, near-coded addressed channel, bge (n 348) | > 0 | -0.0102 (s 0.010 → 0.000; perm. p 0.998) | not met |
| P3 T, near-coded addressed channel, gte (n 348) | > 0 | -0.0026 (s 0.003 → 0.000; perm. p 0.986) | not met |

**Post hoc and robustness (not part of the verdict):**

| Statistic | Slope per doubling of k (95% CI) |
| --- | --- |
| raw read-set echo, bge (upper bound; no chance correction) | +0.0023 ± 0.0053 (p 0.386) |
| raw read-set echo, gte | +0.0022 ± 0.0029 (p 0.142) |
| lag-matched count excess, bge (Amendment 2) | -0.0483 ± 0.0083 (p 1.12e-17) |
| lag-matched count excess, gte | -0.0046 ± 0.0037 (p 0.0165) |
| lag-matched count excess, bge, without templated / kickoff-echo statements | -0.0490 ± 0.0096 (p 3.65e-15) |
| DQ5 cross_echo (crude flag, P7) | +0.0069 ± 0.0082 (p 0.102) |
| rival a: β_echo bge with day FE | -0.0104 ± 0.0069 (p 0.00435) |
| rival b: β_echo bge without templated / kickoff-echo statements | -0.0106 ± 0.0076 (p 0.0083) |
| context load log₂(1+k_ctx) at fixed k, lag-matched (bge) | +0.0043 ± 0.0088 (p 0.339) |

## Scorecard (period-specific axes)
- **C (adequacy):** 0. The load-dependent copy model does not beat the constant-copy null here: the pre-registered slope is ≤ 0 and the raw upper bound is small (+0.0023 per doubling, bge).
- **D (unfitted predictions):** 0. P1–P3 not met.

## Notes
- Replication folder (layer 1): one phase-diagram point, not an independent test. Per-period p-values are calibrated with κ from the constant-π synthetic worlds (card Amendment 1c).
- The near-coded copy share s is ≈ 0 in both k terciles wherever T = 0: agents almost never near-copy the message they address (the copy information left after the Miller–Madow correction is ≤ 0).
