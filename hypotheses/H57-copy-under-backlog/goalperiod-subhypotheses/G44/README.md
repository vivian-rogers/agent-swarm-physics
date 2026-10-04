# H57 × G44: #best fine-tunes a leader; #rest picks its own goals (2026-05-26 → 05-29)

**Verdict:** failed (pre-registered rule; the chance-corrected slopes are biased negative by contemporaneous convergence, card Amendment 2; raw-echo upper bound -0.0003 per doubling)
**Role:** replication
**Period:** 2026-05-26 → 05-29 · units 44a, 44b (Claude Opus 4.8 and the temporary leader join the roster 05-28) · N 17 → 18 · 4 d, 16.2 act h · regime III · #best (Opus 4.7, GPT-5.5, Gemini 3.5 Flash, Kimi K2.6) / #rest (12). Non-holdout statements with backlog k ≥ 1: 1328 by 17 agents.

## Why this period
Layer 1 (replication): the common H57 estimator on every eligible goal period, so the per-period slopes are comparable points on a phase diagram (copying vs backlog against period size, regime and median k). This folder is one such point, not an independent native test.

## Prediction
*Written 2026-10-04 07:09 UTC, before running H57 on this period. Templated replication prediction (layer 1), as the two-layer rule allows.*
- **P1:** the within-agent slope of the chance-corrected read-set echo on log₂(1 + k) is positive in both embedding models (β_echo,bge > 0 and β_echo,gte > 0).
- **P2:** the chance-corrected marker near-copy slope β_mk is positive.
- **P3:** the copy share of the near-coded addressed channel rises from the bottom to the top k tercile (T > 0).
- **Power:** at this size the slope SE is roughly 0.011 per doubling of k (scaled from the synthetic #40 worlds), so only slopes above ~0.030 are reliably detectable here. The synthetic load world plants ≈ 0.03.
- **Verdict rule (card):** supported if β_echo (both models) and β_mk are > 0 with at least one one-sided p < 0.05 and none significantly negative; failed if any of them is significantly negative or all are ≤ 0; mixed otherwise.
- **Against:** slopes ≤ 0, or significantly negative.

## Result
*Run 2026-10-04 (non-holdout). Numbers: `data/processed/H57-copy-under-backlog/results/G44.json`.*

n = 1328 statements with k ≥ 1 (17 agents, 4 days, 2 units); median k 3, q90 12. Read-set echo rate 0.0008 (bge), 0.0030 (gte); in-flight chance rate per pair 0.0003 (bge). corr(log k, first day) 0.036.

| Prediction (dated) | Predicted | Observed (95% CI) | Verdict |
| --- | --- | --- | --- |
| P1 β_echo, bge (chance-corrected) | > 0 | -0.0023 ± 0.0008 (p_cal 8.9e-07) | against (sig. < 0) |
| P1 β_echo, gte | > 0 | -0.0012 ± 0.0041 (p_cal 0.638) | not met |
| P2 β_mk (marker near-copy) | > 0 | -0.0190 ± 0.0189 (p_cal 0.0887) | not met |
| P3 T, near-coded addressed channel, bge (n 409) | > 0 | +0.0000 (s 0.000 → 0.000; perm. p 1.0) | not met |
| P3 T, near-coded addressed channel, gte (n 409) | > 0 | -0.0035 (s 0.003 → 0.000; perm. p 0.782) | not met |

**Post hoc and robustness (not part of the verdict):**

| Statistic | Slope per doubling of k (95% CI) |
| --- | --- |
| raw read-set echo, bge (upper bound; no chance correction) | -0.0003 ± 0.0007 (p 0.487) |
| raw read-set echo, gte | +0.0009 ± 0.0040 (p 0.658) |
| lag-matched count excess, bge (Amendment 2) | -0.0011 ± 0.0007 (p 0.00312) |
| lag-matched count excess, gte | +0.0001 ± 0.0040 (p 0.977) |
| lag-matched count excess, bge, without templated / kickoff-echo statements | -0.0009 ± 0.0001 (p 2.4e-21) |
| DQ5 cross_echo (crude flag, P7) | -0.0003 ± 0.0007 (p 0.487) |
| rival a: β_echo bge with day FE | -0.0023 ± 0.0007 (p 9.8e-08) |
| rival b: β_echo bge without templated / kickoff-echo statements | -0.0021 ± 0.0004 (p 4.75e-13) |
| context load log₂(1+k_ctx) at fixed k, lag-matched (bge) | +0.0001 ± 0.0003 (p 0.507) |

## Scorecard (period-specific axes)
- **C (adequacy):** 0. The load-dependent copy model does not beat the constant-copy null here: the pre-registered slope is ≤ 0 and the raw upper bound is small (-0.0003 per doubling, bge).
- **D (unfitted predictions):** 0. P1–P3 not met.

## Notes
- Replication folder (layer 1): one phase-diagram point, not an independent test. Per-period p-values are calibrated with κ from the constant-π synthetic worlds (card Amendment 1c).
- The near-coded copy share s is ≈ 0 in both k terciles wherever T = 0: agents almost never near-copy the message they address (the copy information left after the Miller–Madow correction is ≤ 0).
