# H57 × G38: Charity fundraiser, year 2 (2026-04-02 → 04-24)

**Verdict:** failed (pre-registered rule; the chance-corrected slopes are biased negative by contemporaneous convergence, card Amendment 2; raw-echo upper bound +0.0052 per doubling)
**Role:** replication
**Period:** 2026-04-02 → 04-24 · units 38a (NE36), 38b (NE17), 38c (Opus 4.7 joins), 38d (NE18), 38e (Kimi K2.6 joins) · N 12 → 14 · 17 d, 68.6 act h · regime III · #best (Opus 4.6, Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro) / #rest. Non-holdout statements with backlog k ≥ 1: 3146 by 14 agents.

## Why this period
Layer 1 (replication): the common H57 estimator on every eligible goal period, so the per-period slopes are comparable points on a phase diagram (copying vs backlog against period size, regime and median k). This folder is one such point, not an independent native test.

## Prediction
*Written 2026-10-04 07:09 UTC, before running H57 on this period. Templated replication prediction (layer 1), as the two-layer rule allows.*
- **P1:** the within-agent slope of the chance-corrected read-set echo on log₂(1 + k) is positive in both embedding models (β_echo,bge > 0 and β_echo,gte > 0).
- **P2:** the chance-corrected marker near-copy slope β_mk is positive.
- **P3:** the copy share of the near-coded addressed channel rises from the bottom to the top k tercile (T > 0).
- **Power:** at this size the slope SE is roughly 0.007 per doubling of k (scaled from the synthetic #40 worlds), so only slopes above ~0.019 are reliably detectable here. The synthetic load world plants ≈ 0.03.
- **Verdict rule (card):** supported if β_echo (both models) and β_mk are > 0 with at least one one-sided p < 0.05 and none significantly negative; failed if any of them is significantly negative or all are ≤ 0; mixed otherwise.
- **Against:** slopes ≤ 0, or significantly negative.

## Result
*Run 2026-10-04 (non-holdout). Numbers: `data/processed/H57-copy-under-backlog/results/G38.json`.*

n = 3146 statements with k ≥ 1 (14 agents, 17 days, 5 units); median k 2, q90 7. Read-set echo rate 0.0184 (bge), 0.0095 (gte); in-flight chance rate per pair 0.0162 (bge). corr(log k, first day) 0.031.

| Prediction (dated) | Predicted | Observed (95% CI) | Verdict |
| --- | --- | --- | --- |
| P1 β_echo, bge (chance-corrected) | > 0 | -0.0510 ± 0.0078 (p_cal 2.97e-26) | against (sig. < 0) |
| P1 β_echo, gte | > 0 | -0.0267 ± 0.0060 (p_cal 3.67e-13) | against (sig. < 0) |
| P2 β_mk (marker near-copy) | > 0 | -0.0278 ± 0.0118 (p_cal 6.03e-05) | against (sig. < 0) |
| P3 T, near-coded addressed channel, bge (n 553) | > 0 | +0.0000 (s 0.000 → 0.000; perm. p 0.972) | not met |
| P3 T, near-coded addressed channel, gte (n 553) | > 0 | +0.0000 (s 0.000 → 0.000; perm. p 1.0) | not met |

**Post hoc and robustness (not part of the verdict):**

| Statistic | Slope per doubling of k (95% CI) |
| --- | --- |
| raw read-set echo, bge (upper bound; no chance correction) | +0.0052 ± 0.0058 (p 0.0796) |
| raw read-set echo, gte | +0.0022 ± 0.0052 (p 0.405) |
| lag-matched count excess, bge (Amendment 2) | -0.0276 ± 0.0141 (p 0.000163) |
| lag-matched count excess, gte | -0.0180 ± 0.0052 (p 2.08e-10) |
| lag-matched count excess, bge, without templated / kickoff-echo statements | -0.0280 ± 0.0155 (p 0.000502) |
| DQ5 cross_echo (crude flag, P7) | +0.0019 ± 0.0079 (p 0.636) |
| rival a: β_echo bge with day FE | -0.0490 ± 0.0079 (p 1.04e-25) |
| rival b: β_echo bge without templated / kickoff-echo statements | -0.0482 ± 0.0079 (p 8.56e-25) |
| context load log₂(1+k_ctx) at fixed k, lag-matched (bge) | -0.0021 ± 0.0082 (p 0.624) |

## Scorecard (period-specific axes)
- **C (adequacy):** 0. The load-dependent copy model does not beat the constant-copy null here: the pre-registered slope is ≤ 0 and the raw upper bound is small (+0.0052 per doubling, bge).
- **D (unfitted predictions):** 0. P1–P3 not met.

## Notes
- Replication folder (layer 1): one phase-diagram point, not an independent test. Per-period p-values are calibrated with κ from the constant-π synthetic worlds (card Amendment 1c).
- The near-coded copy share s is ≈ 0 in both k terciles wherever T = 0: agents almost never near-copy the message they address (the copy information left after the Miller–Madow correction is ≤ 0).
