# H123 × G10: Complete as many games as you can in a week! (2025-08-18 → 2025-08-22)

**Verdict:** failed
**Role:** exploratory
**Period:** regime I · 7 agents · one room · 5 active days. Units: 10a (2025-08-18→2025-08-19, 2 d), 10b (2025-08-20→2025-08-22, 3 d).

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
| 10a | self-clocked asynchronous | 0.069 (0.003) | 1.03 (1.08) | 0.09 | 1.00 | 1.03 [1.03, 1.04] | mixed |
| 10b | self-clocked asynchronous | 0.063 (0.001) | 1.32 (1.08) | 0.10 | 1.00 | 0.96 [0.76, 1.26] | mixed |

**EP (O3/O4), talk and mode spins.**

| Unit · channel | N · steps | σ×(1) | σ×(2) | σ×(4) | floor q95 (lag 2) | σ_sweep − σ_rand (lag 2 / 4) | RMS J_s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10a · talk | 7 · 2547 | -2.66 | -3.86 | -6.67 | +4.84 | -0.99 / -1.88 | 0.157 |
| 10a · mode | 7 · 2547 | -9.39 | -19.14 | -40.85 | +4.59 | +1.11 / +0.72 | 0.218 |
| 10b · talk | 7 · 6256 | -0.32 | -0.96 | -2.63 | +0.72 | +0.11 / +0.29 | 0.121 |
| 10b · mode | 7 · 6256 | -0.17 | +0.09 | +0.11 | +2.10 | +0.28 / +0.13 | 0.143 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 HH: sweep (η_ord ≥ 0.5, CV_gap ≤ 0.5) | self-clocked asynchronous in 2/2 units; η_ord ≤ 0.069 | HH failed; my P1 supported |
| P1c L_name ≤ 1.25 | see table | supported |
| P3 σ_sweep ≈ σ_rand ≈ 0 | abs(σ_sweep − σ_rand) ≤ 1.88×10⁻³ | supported |
| P4 no sweep signature | No unit has σ× above the A1 floor at any lag. | supported |


## Scorecard (period-specific axes)
B 2 (update order audited: self-clocked, not a sweep) · C 1 (held-out bound vs floor and σ_rand; at the floor) · D 1 (sweep signature absent, as the audit implies).

## Notes
