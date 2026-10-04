# H66 × G42: platform latency field on goal period #42 (units 42a, 42b)

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · units 42a, 42b.

## Why this period
Replication layer: the common estimator on every eligible non-holdout unit of the computer-use scaffold.

## Prediction
*Templated from the card (written 2026-10-04 19:15 UTC; cut-offs restated in Amendment 1 at ~20:05 UTC, before real data).* Where the residual co-activation E is significant, the latency field explains a minority of it (Δf < 0.10 → failed; Δf ≥ 0.35 with CI > 0 → supported; mixed otherwise); where E is not significant the unit is descriptive. The latency field ρ̄_lat is expected to be a provider field (same-lab ≥ 2× cross-lab).

## Result
*Run 2026-10-04 ~21:00 UTC. Data: `data/processed/H66-platform-latency-field/replication/<unit>.json`, `unit_table.parquet`.*

| unit | N | days | all-present min | E [95% CI] (block-shift p) | Δf [95% CI] | ρ̄_lat (p) | ρ̄_lat same-lab / cross-lab | corr(L, K) (post hoc) | rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 42a | 15 | 2 | 467 | -0.0003 [-0.0070, 0.0068] (p 0.50) | 5.87 [-5.30, 5.50] | -0.002 (p 0.56) | 0.028 / -0.012 | 0.11 | descriptive |
| 42b | 16 | 3 | 558 | 0.0014 [-0.0116, 0.0145] (p 0.46) | 1.15 [-12.10, 1.15] | 0.002 (p 0.26) | 0.011 / -0.000 | 0.16 | descriptive |

**Pre-registered rule:** descriptive. **Verdict after Amendment 2 (post hoc, 2026-10-04 ~21:20 UTC):** descriptive. In every unit the latency field rises with the number of active agents (corr(L, K) > 0), while a latency field that silences agents gives corr(L, K) < 0 (synthetic W2: −0.34 to −0.66). A congestion world with no latency action (W6) returns Δf ≈ 1.1–1.6, so a positive Δf here measures load, not drive. Where E is not significant, there is no residual to explain (descriptive).

## Scorecard (period-specific axes)
- C (adequacy): E against the trimmed block-shift null, per unit above.
- H (comparative): the field-vs-load sign test (post hoc) decides against the H66 field reading in every unit with a significant E.

## Notes
- Written by `analysis/summarize.py` (replication rows templated; native rows written from `native/results.json`).
