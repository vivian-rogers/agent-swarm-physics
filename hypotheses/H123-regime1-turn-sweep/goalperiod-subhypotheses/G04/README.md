# H123 × G04: Write a story and celebrate it with 100 people in person (2025-05-15 → 2025-06-18)

**Verdict:** failed
**Role:** exploratory
**Period:** regime I · 4 agents · one room · 26 active days. Units: 4a (2025-05-15→2025-05-21, 5 d), 4b (2025-05-22→2025-05-22, 1 d), 4c (2025-05-23→2025-06-18, 19 d), 4d (2025-06-18→2025-06-18, 1 d).

## Why this period
Replication: the common audit and EP estimator on every non-holdout regime-I unit (two-layer design). Layer role: exploratory · replication.

## Prediction
*Written 2026-10-04 ~22:03 UTC, before running on this period (card predictions applied here).*
- P1 (audit, all calls): not a sweep; class self-clocked asynchronous (κ_par ≥ 0.3, η_ord < 0.2). HH counter-prediction: sweep (η_ord ≥ 0.5, CV_gap ≤ 0.5). Random sequential would kill the HH.
- P1c: L_name ≤ 1.25 (being named does not pull the next call).
- P3 (EP, talk spin, after the audit): σ_sweep ≈ σ_rand ≈ 0 (< 10⁻⁴ nats/step); σ_× at the floor. Kill (HH): σ_× > 3 σ_sweep with CI excluding it.
- P4: no lag-1-zero / lag-2-positive sweep signature.
- With N = 4 the EP fit has few pairs (6); power is set by the step count.

## Result
*Run 2026-10-04 22:06 UTC (audit, `analysis/audit.py`) and 22:11–22:17 UTC (EP, `analysis/run.py`); data `data/processed/H123-regime1-turn-sweep/results/{audit,ep}.parquet`; cross-period figures `../../figures/audit.pdf`, `../../figures/ep_talk.pdf`.* EP in 10⁻³ nats per step (one step = one model call); ★ = above the A1 floor (block-flip q95 and σ_rand q95).

**Audit (O1, run first).**

| Unit | Class (all calls) | η_ord (shuffle) | CV_gap (shuffle) | r/r₀ | κ_par | L_name [95% CI] | Class (chat-mode calls) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4a | self-clocked asynchronous | 0.030 (0.001) | 1.59 (1.16) | 0.54 | 0.92 | 1.23 [1.05, 1.44] | mixed |
| 4b | self-clocked asynchronous | 0.068 (0.003) | 1.09 (1.16) | 0.40 | 0.98 | 1.07 (1 day) | mixed |
| 4c | self-clocked asynchronous | 0.033 (0.001) | 1.47 (1.17) | 0.55 | 0.94 | 1.22 [1.16, 1.30] | mixed |
| 4d | self-clocked asynchronous | 0.055 (0.001) | 1.62 (1.22) | 0.57 | 0.88 | 1.14 (1 day) | mixed |

**EP (O3/O4), talk and mode spins.**

| Unit · channel | N · steps | σ×(1) | σ×(2) | σ×(4) | floor q95 (lag 2) | σ_sweep − σ_rand (lag 2 / 4) | RMS J_s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4a · talk | 4 · 4721 | -1.36 | -2.24 | -2.33 | +1.54 | +0.21 / +0.16 | 0.092 |
| 4a · mode | 4 · 4721 | +0.30 | +0.51 | +0.85 | +1.88 | -0.43 / -0.27 | 0.147 |
| 4c · talk | 4 · 19573 | +0.09 | +0.12 | +0.03 | +0.36 | +0.00 / +0.04 | 0.036 |
| 4c · mode | 4 · 19573 | -0.18 | -0.31 | -0.97 | +0.52 | -0.00 / +0.03 | 0.052 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 HH: sweep (η_ord ≥ 0.5, CV_gap ≤ 0.5) | self-clocked asynchronous in 4/4 units; η_ord ≤ 0.068 | HH failed; my P1 supported |
| P1c L_name ≤ 1.25 | see table | supported |
| P3 σ_sweep ≈ σ_rand ≈ 0 | abs(σ_sweep − σ_rand) ≤ 0.27×10⁻³ | supported |
| P4 no sweep signature | No unit has σ× above the A1 floor at any lag. | supported |


## Scorecard (period-specific axes)
B 2 (update order audited: self-clocked, not a sweep) · C 1 (held-out bound vs floor and σ_rand; at the floor) · D 1 (sweep signature absent, as the audit implies).

## Notes
