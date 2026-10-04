# H57 × G18: Reduce global poverty (2025-10-20 → 10-31)

**Verdict:** failed (pre-registered rule; the chance-corrected slopes are biased negative by contemporaneous convergence, card Amendment 2; raw-echo upper bound +0.0283 per doubling)
**Role:** replication
**Period:** 2025-10-20 → 10-31 · units 18a, 18b (Claude Haiku 4.5 joins 10-22), 18c (Grok 4 leaves 10-29) · N 7 → 8 → 7 · 10 d, 35.0 act h · regime I · #general. Non-holdout statements with backlog k ≥ 1: 6681 by 8 agents.

## Why this period
Layer 1 (replication): the common H57 estimator on every eligible goal period, so the per-period slopes are comparable points on a phase diagram (copying vs backlog against period size, regime and median k). This folder is one such point, not an independent native test.

## Prediction
*Written 2026-10-04 07:09 UTC, before running H57 on this period. Templated replication prediction (layer 1), as the two-layer rule allows.*
- **P1:** the within-agent slope of the chance-corrected read-set echo on log₂(1 + k) is positive in both embedding models (β_echo,bge > 0 and β_echo,gte > 0).
- **P2:** the chance-corrected marker near-copy slope β_mk is positive.
- **P3:** the copy share of the near-coded addressed channel rises from the bottom to the top k tercile (T > 0).
- **Power:** at this size the slope SE is roughly 0.005 per doubling of k (scaled from the synthetic #40 worlds), so only slopes above ~0.013 are reliably detectable here. The synthetic load world plants ≈ 0.03.
- **Verdict rule (card):** supported if β_echo (both models) and β_mk are > 0 with at least one one-sided p < 0.05 and none significantly negative; failed if any of them is significantly negative or all are ≤ 0; mixed otherwise.
- **Against:** slopes ≤ 0, or significantly negative.

## Result
*Run 2026-10-04 (non-holdout). Numbers: `data/processed/H57-copy-under-backlog/results/G18.json`.*

n = 6681 statements with k ≥ 1 (8 agents, 10 days, 3 units); median k 3, q90 14. Read-set echo rate 0.0581 (bge), 0.0594 (gte); in-flight chance rate per pair 0.0276 (bge). corr(log k, first day) 0.015.

| Prediction (dated) | Predicted | Observed (95% CI) | Verdict |
| --- | --- | --- | --- |
| P1 β_echo, bge (chance-corrected) | > 0 | -0.0873 ± 0.0118 (p_cal 1.8e-33) | against (sig. < 0) |
| P1 β_echo, gte | > 0 | -0.0905 ± 0.0135 (p_cal 1.63e-27) | against (sig. < 0) |
| P2 β_mk (marker near-copy) | > 0 | -0.1717 ± 0.0157 (p_cal 6.44e-77) | against (sig. < 0) |
| P3 T, near-coded addressed channel, bge (n 1391) | > 0 | +0.0000 (s 0.000 → 0.000; perm. p 1.0) | not met |
| P3 T, near-coded addressed channel, gte (n 1391) | > 0 | -0.0000 (s 0.000 → 0.000; perm. p 0.731) | not met |

**Post hoc and robustness (not part of the verdict):**

| Statistic | Slope per doubling of k (95% CI) |
| --- | --- |
| raw read-set echo, bge (upper bound; no chance correction) | +0.0283 ± 0.0099 (p 3.55e-07) |
| raw read-set echo, gte | +0.0276 ± 0.0120 (p 2.41e-05) |
| lag-matched count excess, bge (Amendment 2) | +0.0607 ± 0.0440 (p 0.00852) |
| lag-matched count excess, gte | +0.0610 ± 0.0459 (p 0.0111) |
| lag-matched count excess, bge, without templated / kickoff-echo statements | -0.0202 ± 0.0101 (p 0.000186) |
| DQ5 cross_echo (crude flag, P7) | +0.0170 ± 0.0093 (p 0.000597) |
| rival a: β_echo bge with day FE | -0.0893 ± 0.0120 (p 1.64e-23) |
| rival b: β_echo bge without templated / kickoff-echo statements | -0.1018 ± 0.0157 (p 2.43e-20) |
| context load log₂(1+k_ctx) at fixed k, lag-matched (bge) | -0.0163 ± 0.0136 (p 0.0217) |

## Scorecard (period-specific axes)
- **C (adequacy):** 0. The load-dependent copy model does not beat the constant-copy null on the pre-registered estimator. The raw echo slope is sizeable here (bge +0.0283); the lag-matched slope is +0.0607 but turns -0.0202 without templated / kickoff-echo statements (rival b: shared sources).
- **D (unfitted predictions):** 0. P1–P3 not met.

## Notes
- Replication folder (layer 1): one phase-diagram point, not an independent test. Per-period p-values are calibrated with κ from the constant-π synthetic worlds (card Amendment 1c).
- The near-coded copy share s is ≈ 0 in both k terciles wherever T = 0: agents almost never near-copy the message they address (the copy information left after the Miller–Madow correction is ≤ 0).
