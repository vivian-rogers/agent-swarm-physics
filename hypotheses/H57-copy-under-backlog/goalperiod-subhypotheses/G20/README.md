# H57 × G20: Substack blogs (2025-11-17 → 11-28)

**Verdict:** failed (pre-registered rule; the chance-corrected slopes are biased negative by contemporaneous convergence, card Amendment 2; raw-echo upper bound +0.0030 per doubling)
**Role:** replication
**Period:** 2025-11-17 → 11-28 · units 20a, 20b (Gemini 3 Pro joins 11-19), 20c (NE06 11-20), 20d (NE06 11-25 + Claude Opus 4.5 joins) · N 8 → 10 · 10 d, 40.0 act h · regime I · #general. Non-holdout statements with backlog k ≥ 1: 4356 by 10 agents.

## Why this period
Layer 1 (replication): the common H57 estimator on every eligible goal period, so the per-period slopes are comparable points on a phase diagram (copying vs backlog against period size, regime and median k). This folder is one such point, not an independent native test.

## Prediction
*Written 2026-10-04 07:09 UTC, before running H57 on this period. Templated replication prediction (layer 1), as the two-layer rule allows.*
- **P1:** the within-agent slope of the chance-corrected read-set echo on log₂(1 + k) is positive in both embedding models (β_echo,bge > 0 and β_echo,gte > 0).
- **P2:** the chance-corrected marker near-copy slope β_mk is positive.
- **P3:** the copy share of the near-coded addressed channel rises from the bottom to the top k tercile (T > 0).
- **Power:** at this size the slope SE is roughly 0.006 per doubling of k (scaled from the synthetic #40 worlds), so only slopes above ~0.016 are reliably detectable here. The synthetic load world plants ≈ 0.03.
- **Verdict rule (card):** supported if β_echo (both models) and β_mk are > 0 with at least one one-sided p < 0.05 and none significantly negative; failed if any of them is significantly negative or all are ≤ 0; mixed otherwise.
- **Against:** slopes ≤ 0, or significantly negative.

## Result
*Run 2026-10-04 (non-holdout). Numbers: `data/processed/H57-copy-under-backlog/results/G20.json`.*

n = 4356 statements with k ≥ 1 (10 agents, 10 days, 4 units); median k 4, q90 19. Read-set echo rate 0.0108 (bge), 0.0080 (gte); in-flight chance rate per pair 0.0057 (bge). corr(log k, first day) -0.025.

| Prediction (dated) | Predicted | Observed (95% CI) | Verdict |
| --- | --- | --- | --- |
| P1 β_echo, bge (chance-corrected) | > 0 | -0.0297 ± 0.0081 (p_cal 2.56e-09) | against (sig. < 0) |
| P1 β_echo, gte | > 0 | -0.0240 ± 0.0048 (p_cal 3.2e-16) | against (sig. < 0) |
| P2 β_mk (marker near-copy) | > 0 | -0.1122 ± 0.0118 (p_cal 3.64e-58) | against (sig. < 0) |
| P3 T, near-coded addressed channel, bge (n 979) | > 0 | -0.0053 (s 0.005 → 0.000; perm. p 0.996) | not met |
| P3 T, near-coded addressed channel, gte (n 979) | > 0 | -0.0023 (s 0.002 → 0.000; perm. p 1.0) | not met |

**Post hoc and robustness (not part of the verdict):**

| Statistic | Slope per doubling of k (95% CI) |
| --- | --- |
| raw read-set echo, bge (upper bound; no chance correction) | +0.0030 ± 0.0031 (p 0.0625) |
| raw read-set echo, gte | +0.0022 ± 0.0022 (p 0.0461) |
| lag-matched count excess, bge (Amendment 2) | -0.0241 ± 0.0037 (p 3.84e-22) |
| lag-matched count excess, gte | -0.0177 ± 0.0029 (p 1.21e-20) |
| lag-matched count excess, bge, without templated / kickoff-echo statements | -0.0266 ± 0.0038 (p 3.71e-24) |
| DQ5 cross_echo (crude flag, P7) | +0.0028 ± 0.0049 (p 0.266) |
| rival a: β_echo bge with day FE | -0.0293 ± 0.0079 (p 1.28e-10) |
| rival b: β_echo bge without templated / kickoff-echo statements | -0.0290 ± 0.0080 (p 2.59e-10) |
| context load log₂(1+k_ctx) at fixed k, lag-matched (bge) | +0.0028 ± 0.0097 (p 0.574) |

## Scorecard (period-specific axes)
- **C (adequacy):** 0. The load-dependent copy model does not beat the constant-copy null here: the pre-registered slope is ≤ 0 and the raw upper bound is small (+0.0030 per doubling, bge).
- **D (unfitted predictions):** 0. P1–P3 not met.

## Notes
- Replication folder (layer 1): one phase-diagram point, not an independent test. Per-period p-values are calibrated with κ from the constant-π synthetic worlds (card Amendment 1c).
- The near-coded copy share s is ≈ 0 in both k terciles wherever T = 0: agents almost never near-copy the message they address (the copy information left after the Miller–Madow correction is ≤ 0).
