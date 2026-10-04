# H123 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-20)

**Verdict:** failed
**Role:** exploratory
**Period:** regime I · 12 agents · one room · 5 active days. Units: 31a (2026-02-16→2026-02-17, 2 d), 31b (2026-02-18→2026-02-18, 1 d), 31c (2026-02-19→2026-02-19, 1 d), 31d (2026-02-20→2026-02-20, 1 d).

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
| 31a | self-clocked asynchronous | 0.021 (0.001) | 1.54 (1.05) | 0.29 | 1.00 | 1.04 [0.99, 1.07] | mixed |
| 31b | self-clocked asynchronous | 0.019 (0.004) | 1.54 (1.05) | 0.34 | 1.00 | 1.13 (1 day) | mixed |
| 31c | self-clocked asynchronous | 0.022 (0.003) | 2.08 (1.06) | 0.34 | 1.00 | 0.98 (1 day) | mixed |
| 31d | self-clocked asynchronous | 0.026 (0.003) | 1.97 (1.05) | 0.26 | 1.00 | 1.08 (1 day) | mixed |

**EP (O3/O4), talk and mode spins.**

| Unit · channel | N · steps | σ×(1) | σ×(2) | σ×(4) | floor q95 (lag 2) | σ_sweep − σ_rand (lag 2 / 4) | RMS J_s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 31a · talk | 11 · 11546 | -0.69 | -1.91 | -3.24 | +0.01 | +0.50 / +0.69 | 0.074 |
| 31a · mode | 11 · 11546 | -1.44 | -3.24 | -6.52 | -0.44 | +0.35 / +0.81 | 0.079 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 HH: sweep (η_ord ≥ 0.5, CV_gap ≤ 0.5) | self-clocked asynchronous in 4/4 units; η_ord ≤ 0.026 | HH failed; my P1 supported |
| P1c L_name ≤ 1.25 | see table | supported |
| P3 σ_sweep ≈ σ_rand ≈ 0 | abs(σ_sweep − σ_rand) ≤ 0.81×10⁻³ | supported |
| P4 no sweep signature | No unit has σ× above the A1 floor at any lag. | supported |


## Scorecard (period-specific axes)
B 2 (update order audited: self-clocked, not a sweep) · C 1 (held-out bound vs floor and σ_rand; at the floor) · D 1 (sweep signature absent, as the audit implies).

## Notes
