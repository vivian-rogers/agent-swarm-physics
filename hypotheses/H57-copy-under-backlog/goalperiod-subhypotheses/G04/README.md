# H57 × G04: Story + 100-person in-person event (2025-05-15 → 06-18)

**Verdict:** failed (pre-registered rule; the chance-corrected slopes are biased negative by contemporaneous convergence, card Amendment 2; raw-echo upper bound +0.0012 per doubling)
**Role:** replication
**Period:** 2025-05-15 → 06-18 · units 4a, 4b (one-day o4-mini cameo), 4c, 4d (intra-day restart after a 300-min stall on 06-18) · N 4 · 26 unit-days, 51.1 act h (2 h/day documented from 05-23) · regime I · #general. Non-holdout statements with backlog k ≥ 1: 5174 by 6 agents.

## Why this period
Layer 1 (replication): the common H57 estimator on every eligible goal period, so the per-period slopes are comparable points on a phase diagram (copying vs backlog against period size, regime and median k). This folder is one such point, not an independent native test.

## Prediction
*Written 2026-10-04 07:09 UTC, before running H57 on this period. Templated replication prediction (layer 1), as the two-layer rule allows.*
- **P1:** the within-agent slope of the chance-corrected read-set echo on log₂(1 + k) is positive in both embedding models (β_echo,bge > 0 and β_echo,gte > 0).
- **P2:** the chance-corrected marker near-copy slope β_mk is positive.
- **P3:** the copy share of the near-coded addressed channel rises from the bottom to the top k tercile (T > 0).
- **Power:** at this size the slope SE is roughly 0.005 per doubling of k (scaled from the synthetic #40 worlds), so only slopes above ~0.015 are reliably detectable here. The synthetic load world plants ≈ 0.03.
- **Verdict rule (card):** supported if β_echo (both models) and β_mk are > 0 with at least one one-sided p < 0.05 and none significantly negative; failed if any of them is significantly negative or all are ≤ 0; mixed otherwise.
- **Against:** slopes ≤ 0, or significantly negative.

## Result
*Run 2026-10-04 (non-holdout). Numbers: `data/processed/H57-copy-under-backlog/results/G04.json`.*

n = 5930 statements with k ≥ 1 (6 agents, 25 days, 4 units); median k 2, q90 8. Read-set echo rate nan (bge), nan (gte); in-flight chance rate per pair 0.0014 (bge). corr(log k, first day) 0.015.

| Prediction (dated) | Predicted | Observed (95% CI) | Verdict |
| --- | --- | --- | --- |
| P1 β_echo, bge (chance-corrected) | > 0 | -0.0055 ± 0.0030 (p_cal 0.00274) | against (sig. < 0) |
| P1 β_echo, gte | > 0 | -0.0110 ± 0.0020 (p_cal 3.25e-19) | against (sig. < 0) |
| P2 β_mk (marker near-copy) | > 0 | -0.1365 ± 0.0165 (p_cal 6.06e-45) | against (sig. < 0) |
| P3 T, near-coded addressed channel, bge (n 904) | > 0 | +0.0000 (s 0.000 → 0.000; perm. p 1.0) | not met |
| P3 T, near-coded addressed channel, gte (n 904) | > 0 | -0.0004 (s 0.000 → 0.000; perm. p 0.525) | not met |

**Post hoc and robustness (not part of the verdict):**

| Statistic | Slope per doubling of k (95% CI) |
| --- | --- |
| raw read-set echo, bge (upper bound; no chance correction) | +0.0012 ± 0.0023 (p 0.296) |
| raw read-set echo, gte | +0.0001 ± 0.0016 (p 0.934) |
| lag-matched count excess, bge (Amendment 2) | -0.0014 ± 0.0031 (p 0.375) |
| lag-matched count excess, gte | +0.0026 ± 0.0149 (p 0.731) |
| lag-matched count excess, bge, without templated / kickoff-echo statements | -0.0013 ± 0.0036 (p 0.488) |
| DQ5 cross_echo (crude flag, P7) | +0.0018 ± 0.0023 (p 0.129) |
| rival a: β_echo bge with day FE | -0.0056 ± 0.0030 (p 0.000328) |
| rival b: β_echo bge without templated / kickoff-echo statements | -0.0057 ± 0.0034 (p 0.00163) |
| context load log₂(1+k_ctx) at fixed k, lag-matched (bge) | -0.0006 ± 0.0031 (p 0.717) |

## Scorecard (period-specific axes)
- **C (adequacy):** 0. The load-dependent copy model does not beat the constant-copy null here: the pre-registered slope is ≤ 0 and the raw upper bound is small (+0.0012 per doubling, bge).
- **D (unfitted predictions):** 0. P1–P3 not met.

## Notes
- Replication folder (layer 1): one phase-diagram point, not an independent test. Per-period p-values are calibrated with κ from the constant-π synthetic worlds (card Amendment 1c).
- The near-coded copy share s is ≈ 0 in both k terciles wherever T = 0: agents almost never near-copy the message they address (the copy information left after the Miller–Madow correction is ≤ 0).
