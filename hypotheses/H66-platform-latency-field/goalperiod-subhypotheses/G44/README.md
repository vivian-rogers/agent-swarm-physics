# H66 × G44: the fine-tuned leader on a separate serving stack (2026-05-26 → 05-29, units 44a, 44b)

**Verdict:** failed
**Role:** native (also the replication estimator on 44a and 44b)
**Period:** regime III · #44 · 17–18 agents · #best / #rest · 4 non-holdout days; the temporary fine-tuned leader (Kimi base, served outside the frontier APIs) is present on 05-28 and 05-29 (44b).

## Why this period
A model served on its own stack is a natural dose control: a harness-side field (VMs, network, the runner) reaches it like everyone else; a provider-API field does not. #44 is also one of the two regime-III periods whose co-activation survived H38's trim and scaffold conditioning.

## Prediction
*Written 2026-10-04 20:30 UTC, after the synthetic study and before any real-data statistic.*
- The leader's loading on the leave-one-out turnaround field, g_leader, is below the median loading of the other agents in 44b [0.55] (the field is mostly provider-side). With ~430 calls this is descriptive (no test).
- E significant in 44a and 44b [0.6]; Δf < 0.10 in both [0.6].
- *Against:* g_leader at or above the others' median (a harness-side field), or Δf ≥ 0.35.

## Result
*Run 2026-10-04 ~21:00 UTC. Data: `data/processed/H66-platform-latency-field/replication/<unit>.json`, `unit_table.parquet`.*

| unit | N | days | all-present min | E [95% CI] (block-shift p) | Δf [95% CI] | ρ̄_lat (p) | ρ̄_lat same-lab / cross-lab | corr(L, K) (post hoc) | rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 44a | 17 | 2 | 183 | 0.0388 [0.0023, 0.0525] (p 0.01) | 0.74 [0.08, 1.88] | 0.102 (p 0.02) | 0.091 / 0.105 | 0.23 | supported |
| 44b | 18 | 2 | 237 | 0.0007 [-0.0107, 0.0124] (p 0.49) | 1.57 [-4.52, 7.24] | 0.018 (p 0.04) | 0.029 / 0.015 | 0.12 | descriptive |

**Pre-registered rule:** supported. **Verdict after Amendment 2 (post hoc, 2026-10-04 ~21:20 UTC):** failed. In every unit the latency field rises with the number of active agents (corr(L, K) > 0), while a latency field that silences agents gives corr(L, K) < 0 (synthetic W2: −0.34 to −0.66). A congestion world with no latency action (W6) returns Δf ≈ 1.1–1.6, so a positive Δf here measures load, not drive. Where E is not significant, there is no residual to explain (descriptive).

### Native test (prediction above)
| Prediction | Observed | Verdict |
| --- | --- | --- |
| leader loading below the others' median | g_leader -0.11 (70 minutes) vs others' median 0.14 [IQR -0.00, 0.20]; rank 16/17 | held (descriptive, n = 70 minutes) |
| E significant in 44a and 44b | 44a z 3.2 (p 0.01); 44b n.s. | half |
| Δf < 0.10 in both | 44a 0.74 [0.08, 1.88]; corr(L, K) 0.23 | failed as written; the sign shows load |

**Reading.** The model served on its own stack does not load on the village latency field, consistent with a field made by contention among the frontier-API agents' harnesses (70 minutes; descriptive). #44a has the largest residual co-activation of the regime-III units after trimming, and its latency field rises with the active count.

## Scorecard (period-specific axes)
- C (adequacy): E against the trimmed block-shift null, per unit above.
- H (comparative): the field-vs-load sign test (post hoc) decides against the H66 field reading in every unit with a significant E.

## Notes
- Written by `analysis/summarize.py` (replication rows templated; native rows written from `native/results.json`).
