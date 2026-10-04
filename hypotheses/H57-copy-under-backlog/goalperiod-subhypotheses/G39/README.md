# H57 × G39: Build your own interactive world (2026-04-27 → 05-01)

**Verdict:** failed (pre-registered rule; the chance-corrected slopes are biased negative by contemporaneous convergence, card Amendment 2; raw-echo upper bound -0.0001 per doubling)
**Role:** replication
**Period:** 2026-04-27 → 05-01 · unit 39 · N 15 · 5 d, 20.2 act h · regime III · #best (Opus 4.7, GPT-5.5, Gemini 3.1 Pro, Kimi K2.6) / #rest (11). Non-holdout statements with backlog k ≥ 1: 684 by 15 agents.

## Why this period
Layer 1 (replication): the common H57 estimator on every eligible goal period, so the per-period slopes are comparable points on a phase diagram (copying vs backlog against period size, regime and median k). This folder is one such point, not an independent native test.

## Prediction
*Written 2026-10-04 07:09 UTC, before running H57 on this period. Templated replication prediction (layer 1), as the two-layer rule allows.*
- **P1:** the within-agent slope of the chance-corrected read-set echo on log₂(1 + k) is positive in both embedding models (β_echo,bge > 0 and β_echo,gte > 0).
- **P2:** the chance-corrected marker near-copy slope β_mk is positive.
- **P3:** the copy share of the near-coded addressed channel rises from the bottom to the top k tercile (T > 0).
- **Power:** at this size the slope SE is roughly 0.015 per doubling of k (scaled from the synthetic #40 worlds), so only slopes above ~0.041 are reliably detectable here. The synthetic load world plants ≈ 0.03.
- **Verdict rule (card):** supported if β_echo (both models) and β_mk are > 0 with at least one one-sided p < 0.05 and none significantly negative; failed if any of them is significantly negative or all are ≤ 0; mixed otherwise.
- **Against:** slopes ≤ 0, or significantly negative.

## Result
*Run 2026-10-04 (non-holdout). Numbers: `data/processed/H57-copy-under-backlog/results/G39.json`.*

n = 684 statements with k ≥ 1 (15 agents, 5 days, 1 units); median k 3, q90 10. Read-set echo rate 0.0015 (bge), 0.0000 (gte); in-flight chance rate per pair 0.0022 (bge). corr(log k, first day) -0.137.

| Prediction (dated) | Predicted | Observed (95% CI) | Verdict |
| --- | --- | --- | --- |
| P1 β_echo, bge (chance-corrected) | > 0 | -0.0109 ± 0.0018 (p_cal 1.27e-22) | against (sig. < 0) |
| P1 β_echo, gte | > 0 | -0.0109 ± 0.0018 (p_cal 1.74e-23) | against (sig. < 0) |
| P2 β_mk (marker near-copy) | > 0 | -0.0115 ± 0.0019 (p_cal 4.56e-25) | against (sig. < 0) |
| P3 T, near-coded addressed channel, bge (n 71) | > 0 | +0.0000 (s 0.000 → 0.000; perm. p 1.0) | not met |
| P3 T, near-coded addressed channel, gte (n 71) | > 0 | +0.0000 (s 0.000 → 0.000; perm. p 1.0) | not met |

**Post hoc and robustness (not part of the verdict):**

| Statistic | Slope per doubling of k (95% CI) |
| --- | --- |
| raw read-set echo, bge (upper bound; no chance correction) | -0.0001 ± 0.0003 (p 0.667) |
| raw read-set echo, gte | +0.0000 ± 0.0000 |
| lag-matched count excess, bge (Amendment 2) | -0.0105 ± 0.0016 (p 3.24e-20) |
| lag-matched count excess, gte | -0.0105 ± 0.0015 (p 9.79e-21) |
| lag-matched count excess, bge, without templated / kickoff-echo statements | -0.0106 ± 0.0018 (p 3.68e-17) |
| DQ5 cross_echo (crude flag, P7) | -0.0003 ± 0.0007 (p 0.37) |
| rival a: β_echo bge with day FE | -0.0100 ± 0.0022 (p 2.45e-13) |
| rival b: β_echo bge without templated / kickoff-echo statements | -0.0109 ± 0.0020 (p 2.01e-15) |
| context load log₂(1+k_ctx) at fixed k, lag-matched (bge) | -0.0028 ± 0.0035 (p 0.12) |

## Scorecard (period-specific axes)
- **C (adequacy):** 0. The load-dependent copy model does not beat the constant-copy null here: the pre-registered slope is ≤ 0 and the raw upper bound is small (-0.0001 per doubling, bge).
- **D (unfitted predictions):** 0. P1–P3 not met.

## Notes
- Replication folder (layer 1): one phase-diagram point, not an independent test. Per-period p-values are calibrated with κ from the constant-π synthetic worlds (card Amendment 1c).
- The near-coded copy share s is ≈ 0 in both k terciles wherever T = 0: agents almost never near-copy the message they address (the copy information left after the Miller–Madow correction is ≤ 0).
