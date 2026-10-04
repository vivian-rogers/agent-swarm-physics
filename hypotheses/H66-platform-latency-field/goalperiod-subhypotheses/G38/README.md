# H66 × G38: platform latency field on goal period #38 (units 38a, 38b, 38c, 38d, 38e)

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · units 38a, 38b, 38c, 38d, 38e.

## Why this period
Replication layer: the common estimator on every eligible non-holdout unit of the computer-use scaffold.

## Prediction
*Templated from the card (written 2026-10-04 19:15 UTC; cut-offs restated in Amendment 1 at ~20:05 UTC, before real data).* Where the residual co-activation E is significant, the latency field explains a minority of it (Δf < 0.10 → failed; Δf ≥ 0.35 with CI > 0 → supported; mixed otherwise); where E is not significant the unit is descriptive. The latency field ρ̄_lat is expected to be a provider field (same-lab ≥ 2× cross-lab).

## Result
*Run 2026-10-04 ~21:00 UTC. Data: `data/processed/H66-platform-latency-field/replication/<unit>.json`, `unit_table.parquet`.*

| unit | N | days | all-present min | E [95% CI] (block-shift p) | Δf [95% CI] | ρ̄_lat (p) | ρ̄_lat same-lab / cross-lab | corr(L, K) (post hoc) | rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 38a | 12 | 8 | 1742 | 0.0018 [-0.0038, 0.0068] (p 0.29) | 0.20 [-1.17, 1.30] | -0.009 (p 1.00) | -0.014 / -0.007 | 0.09 | descriptive |
| 38b | 12 | 3 | 474 | 0.0018 [-0.0043, 0.0095] (p 0.42) | 1.58 [-5.36, 1.58] | -0.014 (p 0.94) | -0.008 / -0.016 | 0.07 | descriptive |
| 38c | 13 | 1 | 218 | -0.0263 [-0.0393, -0.0111] (p 1.00) | -0.07 [-0.46, 0.15] | -0.021 (p 0.98) | -0.014 / -0.024 | 0.20 | descriptive |
| 38d | 13 | 2 | 255 | -0.0056 [-0.0215, 0.0083] (p 0.70) | 0.03 [-3.70, 1.77] | -0.018 (p 0.96) | -0.016 / -0.019 | 0.06 | descriptive |
| 38e | 14 | 3 | 453 | -0.0035 [-0.0153, 0.0216] (p 0.69) | -0.73 [-0.73, 29.65] | 0.006 (p 0.32) | -0.001 / 0.008 | 0.15 | descriptive |

**Pre-registered rule:** descriptive. **Verdict after Amendment 2 (post hoc, 2026-10-04 ~21:20 UTC):** descriptive. In every unit the latency field rises with the number of active agents (corr(L, K) > 0), while a latency field that silences agents gives corr(L, K) < 0 (synthetic W2: −0.34 to −0.66). A congestion world with no latency action (W6) returns Δf ≈ 1.1–1.6, so a positive Δf here measures load, not drive. Where E is not significant, there is no residual to explain (descriptive).

## Scorecard (period-specific axes)
- C (adequacy): E against the trimmed block-shift null, per unit above.
- H (comparative): the field-vs-load sign test (post hoc) decides against the H66 field reading in every unit with a significant E.

## Notes
- Written by `analysis/summarize.py` (replication rows templated; native rows written from `native/results.json`).
