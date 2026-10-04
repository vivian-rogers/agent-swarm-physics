# H57 × G35: Test your game (forked per room) (2026-03-16 → 03-20)

**Verdict:** failed (pre-registered rule; the chance-corrected slopes are biased negative by contemporaneous convergence, card Amendment 2; raw-echo upper bound +0.0029 per doubling)
**Role:** replication
**Period:** 2026-03-16 → 03-20 · unit 35 · N 12 · 5 d, 19.9 act h · regime II · **#best / #rest**. Non-holdout statements with backlog k ≥ 1: 1768 by 12 agents.

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
*Run 2026-10-04 (non-holdout). Numbers: `data/processed/H57-copy-under-backlog/results/G35.json`.*

n = 1768 statements with k ≥ 1 (12 agents, 5 days, 1 units); median k 4, q90 13. Read-set echo rate 0.0096 (bge), 0.0034 (gte); in-flight chance rate per pair 0.0032 (bge). corr(log k, first day) 0.015.

| Prediction (dated) | Predicted | Observed (95% CI) | Verdict |
| --- | --- | --- | --- |
| P1 β_echo, bge (chance-corrected) | > 0 | -0.0136 ± 0.0055 (p_cal 5.16e-05) | against (sig. < 0) |
| P1 β_echo, gte | > 0 | -0.0005 ± 0.0020 (p_cal 0.695) | not met |
| P2 β_mk (marker near-copy) | > 0 | -0.0245 ± 0.0181 (p_cal 0.022) | against (sig. < 0) |
| P3 T, near-coded addressed channel, bge (n 338) | > 0 | +0.0058 (s 0.000 → 0.006; perm. p 0.216) | not met |
| P3 T, near-coded addressed channel, gte (n 338) | > 0 | +0.0000 (s 0.000 → 0.000; perm. p 1.0) | not met |

**Post hoc and robustness (not part of the verdict):**

| Statistic | Slope per doubling of k (95% CI) |
| --- | --- |
| raw read-set echo, bge (upper bound; no chance correction) | +0.0029 ± 0.0037 (p 0.132) |
| raw read-set echo, gte | +0.0017 ± 0.0019 (p 0.0783) |
| lag-matched count excess, bge (Amendment 2) | -0.0135 ± 0.0046 (p 4.25e-07) |
| lag-matched count excess, gte | -0.0015 ± 0.0020 (p 0.141) |
| lag-matched count excess, bge, without templated / kickoff-echo statements | -0.0111 ± 0.0048 (p 3.14e-05) |
| DQ5 cross_echo (crude flag, P7) | +0.0011 ± 0.0033 (p 0.526) |
| rival a: β_echo bge with day FE | -0.0136 ± 0.0055 (p 9.15e-06) |
| rival b: β_echo bge without templated / kickoff-echo statements | -0.0124 ± 0.0064 (p 0.000341) |
| context load log₂(1+k_ctx) at fixed k, lag-matched (bge) | -0.0063 ± 0.0063 (p 0.0554) |

## Scorecard (period-specific axes)
- **C (adequacy):** 0. The load-dependent copy model does not beat the constant-copy null here: the pre-registered slope is ≤ 0 and the raw upper bound is small (+0.0029 per doubling, bge).
- **D (unfitted predictions):** 0. P1–P3 not met.

## Notes
- Replication folder (layer 1): one phase-diagram point, not an independent test. Per-period p-values are calibrated with κ from the constant-π synthetic worlds (card Amendment 1c).
- The near-coded copy share s is ≈ 0 in both k terciles wherever T = 0: agents almost never near-copy the message they address (the copy information left after the Miller–Madow correction is ≤ 0).
