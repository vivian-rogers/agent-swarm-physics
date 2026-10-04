# H123 × G18: Reduce global poverty as much as you can (2025-10-20 → 2025-10-31)

**Verdict:** failed
**Role:** exploratory
**Period:** regime I · 8 agents · one room · 10 active days. Units: 18a (2025-10-20→2025-10-21, 2 d), 18b (2025-10-22→2025-10-28, 5 d), 18c (2025-10-29→2025-10-31, 3 d).

## Why this period
Replication: the common audit and EP estimator on every non-holdout regime-I unit (two-layer design). Layer role: exploratory · replication.

## Prediction
*Written 2026-10-04 ~22:03 UTC, before running on this period (card predictions applied here).*
- P1 (audit, all calls): not a sweep; class self-clocked asynchronous (κ_par ≥ 0.3, η_ord < 0.2). HH counter-prediction: sweep (η_ord ≥ 0.5, CV_gap ≤ 0.5). Random sequential would kill the HH.
- P1c: L_name ≤ 1.25 (being named does not pull the next call).
- P3 (EP, talk spin, after the audit): σ_sweep ≈ σ_rand ≈ 0 (< 10⁻⁴ nats/step); σ_× at the floor. Kill (HH): σ_× > 3 σ_sweep with CI excluding it.
- P4: no lag-1-zero / lag-2-positive sweep signature.

## Result
*Run 2026-10-04 22:06 UTC (audit, `analysis/audit.py`) and 22:11–22:17 UTC (EP, `analysis/run.py`); data `data/processed/H123-regime1-turn-sweep/results/{audit,ep}.parquet`; cross-period figures `../../figures/audit.pdf`, `../../figures/ep_talk.pdf`.* EP in 10⁻³ nats per step (one step = one model call); ★ = above the A1 floor (block-flip q95 and σ_rand q95).

**Audit (O1, run first).**

| Unit | Class (all calls) | η_ord (shuffle) | CV_gap (shuffle) | r/r₀ | κ_par | L_name [95% CI] | Class (chat-mode calls) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 18a | self-clocked asynchronous | 0.034 (0.002) | 1.47 (1.09) | 0.38 | 0.99 | 1.30 [1.20, 1.41] | mixed |
| 18b | self-clocked asynchronous | 0.033 (0.001) | 1.57 (1.08) | 0.27 | 0.99 | 1.31 [1.14, 1.46] | mixed |
| 18c | self-clocked asynchronous | 0.052 (0.001) | 1.31 (1.08) | 0.15 | 1.00 | 1.20 [1.08, 1.23] | mixed |

**EP (O3/O4), talk and mode spins.**

| Unit · channel | N · steps | σ×(1) | σ×(2) | σ×(4) | floor q95 (lag 2) | σ_sweep − σ_rand (lag 2 / 4) | RMS J_s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 18a · talk | 7 · 3312 | -2.24 | -3.86 | -8.71 | +0.35 | -0.82 / -0.77 | 0.123 |
| 18a · mode | 7 · 3312 | -3.72 | -6.52 | -12.57 | +2.17 | -0.82 / -1.40 | 0.267 |
| 18b · talk | 8 · 13657 | -0.64 | -1.25 | -1.57 | +0.97 | -0.02 / +0.21 | 0.117 |
| 18b · mode | 8 · 13657 | +0.58 ★ | +1.10 ★ | +2.81 ★ | +0.13 | -0.17 / -0.10 | 0.164 |
| 18c · talk | 7 · 8447 | -1.51 | -2.50 | -3.18 | +0.65 | -0.29 / -0.19 | 0.147 |
| 18c · mode | 7 · 8447 | -2.67 | -5.06 | -9.61 | +0.98 | -0.13 / -0.48 | 0.187 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 HH: sweep (η_ord ≥ 0.5, CV_gap ≤ 0.5) | self-clocked asynchronous in 3/3 units; η_ord ≤ 0.052 | HH failed; my P1 supported |
| P1c L_name ≤ 1.25 | see table | partly (weak lift > 1.25 in some unit, < 1.5) |
| P3 σ_sweep ≈ σ_rand ≈ 0 | abs(σ_sweep − σ_rand) ≤ 1.40×10⁻³ | supported |
| P4 no sweep signature | Units with σ× above the A1 floor: 18b (mode; σ×(1) also above: True). Where σ× clears the floor, lag 1 clears it too or is positive, and σ× is ≥ 5× abs(σ_sweep − σ_rand): not the sweep signature, and the HH kill clause (σ× ≫ σ_sweep) applies to that unit. With a 10–25% per-test floor size (synthetic), isolated hits are expected by chance. | supported |


## Scorecard (period-specific axes)
B 2 (update order audited: self-clocked, not a sweep) · C 1 (held-out bound vs floor and σ_rand; at the floor) · D 1 (sweep signature absent, as the audit implies).

## Notes
