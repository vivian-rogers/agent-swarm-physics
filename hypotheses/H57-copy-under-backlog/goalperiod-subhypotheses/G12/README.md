# H57 × G12: Debate tournament (10 debates) (2025-09-01 → 09-05)

**Verdict:** failed (pre-registered rule; the chance-corrected slopes are biased negative by contemporaneous convergence, card Amendment 2; raw-echo upper bound +0.0067 per doubling)
**Role:** replication
**Period:** 2025-09-01 → 09-05 · units 12a (debates 09-01 → 09-04), 12b (NE04 on 09-05; no debates) · N 7 · 5 d, 15.0 act h · regime I · #general. Non-holdout statements with backlog k ≥ 1: 3317 by 7 agents.

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
*Run 2026-10-04 (non-holdout). Numbers: `data/processed/H57-copy-under-backlog/results/G12.json`.*

n = 3317 statements with k ≥ 1 (7 agents, 5 days, 2 units); median k 3, q90 14. Read-set echo rate 0.0157 (bge), 0.0205 (gte); in-flight chance rate per pair 0.0049 (bge). corr(log k, first day) 0.016.

| Prediction (dated) | Predicted | Observed (95% CI) | Verdict |
| --- | --- | --- | --- |
| P1 β_echo, bge (chance-corrected) | > 0 | -0.0175 ± 0.0071 (p_cal 6.84e-05) | against (sig. < 0) |
| P1 β_echo, gte | > 0 | -0.0177 ± 0.0072 (p_cal 6.82e-05) | against (sig. < 0) |
| P2 β_mk (marker near-copy) | > 0 | -0.0926 ± 0.0303 (p_cal 2.06e-07) | against (sig. < 0) |
| P3 T, near-coded addressed channel, bge (n 616) | > 0 | +0.0000 (s 0.000 → 0.000; perm. p 0.994) | not met |
| P3 T, near-coded addressed channel, gte (n 616) | > 0 | +0.0000 (s 0.000 → 0.000; perm. p 1.0) | not met |

**Post hoc and robustness (not part of the verdict):**

| Statistic | Slope per doubling of k (95% CI) |
| --- | --- |
| raw read-set echo, bge (upper bound; no chance correction) | +0.0067 ± 0.0054 (p 0.022) |
| raw read-set echo, gte | +0.0082 ± 0.0050 (p 0.00294) |
| lag-matched count excess, bge (Amendment 2) | +0.0039 ± 0.0081 (p 0.358) |
| lag-matched count excess, gte | +0.0048 ± 0.0060 (p 0.129) |
| lag-matched count excess, bge, without templated / kickoff-echo statements | +0.0024 ± 0.0080 (p 0.559) |
| DQ5 cross_echo (crude flag, P7) | +0.0033 ± 0.0077 (p 0.407) |
| rival a: β_echo bge with day FE | -0.0175 ± 0.0071 (p 3.03e-05) |
| rival b: β_echo bge without templated / kickoff-echo statements | -0.0168 ± 0.0070 (p 4.13e-05) |
| context load log₂(1+k_ctx) at fixed k, lag-matched (bge) | -0.0013 ± 0.0020 (p 0.214) |

## Scorecard (period-specific axes)
- **C (adequacy):** 0. The load-dependent copy model does not beat the constant-copy null here: the pre-registered slope is ≤ 0 and the raw upper bound is small (+0.0067 per doubling, bge).
- **D (unfitted predictions):** 0. P1–P3 not met.

## Notes
- Replication folder (layer 1): one phase-diagram point, not an independent test. Per-period p-values are calibrated with κ from the constant-π synthetic worlds (card Amendment 1c).
- The near-coded copy share s is ≈ 0 in both k terciles wherever T = 0: agents almost never near-copy the message they address (the copy information left after the Miller–Madow correction is ≤ 0).
