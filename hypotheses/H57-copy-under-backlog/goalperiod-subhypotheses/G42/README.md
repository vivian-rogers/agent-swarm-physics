# H57 × G42: Run your own YouTube channel (2026-05-18 → 05-22)

**Verdict:** failed (pre-registered rule; the chance-corrected slopes are biased negative by contemporaneous convergence, card Amendment 2; raw-echo upper bound +0.0008 per doubling)
**Role:** replication
**Period:** 2026-05-18 → 05-22 · units 42a, 42b (Gemini 3.5 Flash joins 05-20) · N 15 → 16 · 5 d, 20.1 act h · regime III · #best / #rest. Non-holdout statements with backlog k ≥ 1: 940 by 15 agents.

## Why this period
Layer 1 (replication): the common H57 estimator on every eligible goal period, so the per-period slopes are comparable points on a phase diagram (copying vs backlog against period size, regime and median k). This folder is one such point, not an independent native test.

## Prediction
*Written 2026-10-04 07:09 UTC, before running H57 on this period. Templated replication prediction (layer 1), as the two-layer rule allows.*
- **P1:** the within-agent slope of the chance-corrected read-set echo on log₂(1 + k) is positive in both embedding models (β_echo,bge > 0 and β_echo,gte > 0).
- **P2:** the chance-corrected marker near-copy slope β_mk is positive.
- **P3:** the copy share of the near-coded addressed channel rises from the bottom to the top k tercile (T > 0).
- **Power:** at this size the slope SE is roughly 0.013 per doubling of k (scaled from the synthetic #40 worlds), so only slopes above ~0.035 are reliably detectable here. The synthetic load world plants ≈ 0.03.
- **Verdict rule (card):** supported if β_echo (both models) and β_mk are > 0 with at least one one-sided p < 0.05 and none significantly negative; failed if any of them is significantly negative or all are ≤ 0; mixed otherwise.
- **Against:** slopes ≤ 0, or significantly negative.

## Result
*Run 2026-10-04 (non-holdout). Numbers: `data/processed/H57-copy-under-backlog/results/G42.json`.*

n = 940 statements with k ≥ 1 (15 agents, 5 days, 2 units); median k 3, q90 9. Read-set echo rate 0.0011 (bge), 0.0000 (gte); in-flight chance rate per pair 0.0012 (bge). corr(log k, first day) -0.027.

| Prediction (dated) | Predicted | Observed (95% CI) | Verdict |
| --- | --- | --- | --- |
| P1 β_echo, bge (chance-corrected) | > 0 | -0.0036 ± 0.0018 (p_cal 0.000977) | against (sig. < 0) |
| P1 β_echo, gte | > 0 | -0.0044 ± 0.0005 (p_cal 3.61e-56) | against (sig. < 0) |
| P2 β_mk (marker near-copy) | > 0 | -0.0246 ± 0.0120 (p_cal 0.000481) | against (sig. < 0) |
| P3 T, near-coded addressed channel, bge (n 272) | > 0 | +0.0000 (s 0.000 → 0.000; perm. p 1.0) | not met |
| P3 T, near-coded addressed channel, gte (n 272) | > 0 | +0.0000 (s 0.000 → 0.000; perm. p 1.0) | not met |

**Post hoc and robustness (not part of the verdict):**

| Statistic | Slope per doubling of k (95% CI) |
| --- | --- |
| raw read-set echo, bge (upper bound; no chance correction) | +0.0008 ± 0.0017 (p 0.38) |
| raw read-set echo, gte | +0.0000 ± 0.0000 |
| lag-matched count excess, bge (Amendment 2) | -0.0032 ± 0.0018 (p 0.000614) |
| lag-matched count excess, gte | -0.0040 ± 0.0003 (p 2.12e-35) |
| lag-matched count excess, bge, without templated / kickoff-echo statements | -0.0040 ± 0.0003 (p 6.31e-35) |
| DQ5 cross_echo (crude flag, P7) | +0.0016 ± 0.0023 (p 0.18) |
| rival a: β_echo bge with day FE | -0.0035 ± 0.0021 (p 0.00179) |
| rival b: β_echo bge without templated / kickoff-echo statements | -0.0045 ± 0.0004 (p 8.44e-30) |
| context load log₂(1+k_ctx) at fixed k, lag-matched (bge) | -0.0017 ± 0.0027 (p 0.208) |

## Scorecard (period-specific axes)
- **C (adequacy):** 0. The load-dependent copy model does not beat the constant-copy null here: the pre-registered slope is ≤ 0 and the raw upper bound is small (+0.0008 per doubling, bge).
- **D (unfitted predictions):** 0. P1–P3 not met.

## Notes
- Replication folder (layer 1): one phase-diagram point, not an independent test. Per-period p-values are calibrated with κ from the constant-π synthetic worlds (card Amendment 1c).
- The near-coded copy share s is ≈ 0 in both k terciles wherever T = 0: agents almost never near-copy the message they address (the copy information left after the Miller–Madow correction is ≤ 0).
