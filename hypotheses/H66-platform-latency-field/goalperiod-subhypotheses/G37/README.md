# H66 × G37: platform latency field on goal period #37 (units 37)

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · units 37.

## Why this period
Replication layer: the common estimator on every eligible non-holdout unit of the computer-use scaffold.

## Prediction
*Templated from the card (written 2026-10-04 19:15 UTC; cut-offs restated in Amendment 1 at ~20:05 UTC, before real data).* Where the residual co-activation E is significant, the latency field explains a minority of it (Δf < 0.10 → failed; Δf ≥ 0.35 with CI > 0 → supported; mixed otherwise); where E is not significant the unit is descriptive. The latency field ρ̄_lat is expected to be a provider field (same-lab ≥ 2× cross-lab).

## Result
*Run 2026-10-04 ~21:00 UTC. Data: `data/processed/H66-platform-latency-field/replication/<unit>.json`, `unit_table.parquet`.*

| unit | N | days | all-present min | E [95% CI] (block-shift p) | Δf [95% CI] | ρ̄_lat (p) | ρ̄_lat same-lab / cross-lab | corr(L, K) (post hoc) | rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 37 | 12 | 3 | 450 | -0.0042 [-0.0183, 0.0223] (p 0.75) | -0.16 [-0.33, 0.25] | 0.001 (p 0.56) | 0.024 / -0.008 | 0.09 | descriptive |

**Pre-registered rule:** descriptive. **Verdict after Amendment 2 (post hoc, 2026-10-04 ~21:20 UTC):** descriptive. In every unit the latency field rises with the number of active agents (corr(L, K) > 0), while a latency field that silences agents gives corr(L, K) < 0 (synthetic W2: −0.34 to −0.66). A congestion world with no latency action (W6) returns Δf ≈ 1.1–1.6, so a positive Δf here measures load, not drive. Where E is not significant, there is no residual to explain (descriptive).

## Scorecard (period-specific axes)
- C (adequacy): E against the trimmed block-shift null, per unit above.
- H (comparative): the field-vs-load sign test (post hoc) decides against the H66 field reading in every unit with a significant E.

## Notes
- Written by `analysis/summarize.py` (replication rows templated; native rows written from `native/results.json`).
