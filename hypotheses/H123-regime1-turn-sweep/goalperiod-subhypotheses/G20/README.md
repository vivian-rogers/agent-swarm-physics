# H123 × G20: Start a Substack and join the blogosphere (2025-11-17 → 2025-11-28)

**Verdict:** failed
**Role:** exploratory
**Period:** regime I · 10 agents · one room · 10 active days. Units: 20a (2025-11-17→2025-11-18, 2 d), 20b (2025-11-19→2025-11-19, 1 d), 20c (2025-11-20→2025-11-24, 3 d), 20d (2025-11-25→2025-11-28, 4 d).

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
| 20a | self-clocked asynchronous | 0.054 (0.002) | 1.07 (1.07) | 0.06 | 1.00 | 1.20 [1.16, 1.20] | mixed |
| 20b | self-clocked asynchronous | 0.055 (0.003) | 1.13 (1.06) | 0.03 | 1.00 | 1.11 (1 day) | random sequential |
| 20c | self-clocked asynchronous | 0.048 (0.001) | 1.11 (1.07) | 0.10 | 1.00 | 1.14 [1.04, 1.24] | random sequential |
| 20d | self-clocked asynchronous | 0.033 (0.001) | 1.34 (1.06) | 0.17 | 1.00 | 1.13 [1.07, 1.16] | mixed |

**EP (O3/O4), talk and mode spins.**

| Unit · channel | N · steps | σ×(1) | σ×(2) | σ×(4) | floor q95 (lag 2) | σ_sweep − σ_rand (lag 2 / 4) | RMS J_s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 20a · talk | 8 · 6175 | -1.37 | -1.80 | -2.06 | +1.02 | +0.48 / +1.46 | 0.148 |
| 20a · mode | 8 · 6175 | -2.02 | -3.82 | -7.47 | +0.95 | -0.10 / -0.29 | 0.161 |
| 20c · talk | 9 · 12206 | -1.24 | -2.37 | -4.83 | +0.52 | -0.25 / -0.28 | 0.090 |
| 20c · mode | 9 · 12206 | -2.11 | -4.23 | -9.31 | +0.50 | +0.27 / +0.21 | 0.077 |
| 20d · talk | 10 · 14595 | -0.96 | -1.70 | -3.52 | +0.17 | +0.02 / +0.02 | 0.068 |
| 20d · mode | 10 · 14595 | -2.28 | -4.29 | -7.80 | -0.83 | -0.20 / -0.27 | 0.092 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 HH: sweep (η_ord ≥ 0.5, CV_gap ≤ 0.5) | self-clocked asynchronous in 4/4 units; η_ord ≤ 0.055 | HH failed; my P1 supported |
| P1c L_name ≤ 1.25 | see table | supported |
| P3 σ_sweep ≈ σ_rand ≈ 0 | abs(σ_sweep − σ_rand) ≤ 1.46×10⁻³ | supported |
| P4 no sweep signature | No unit has σ× above the A1 floor at any lag. | supported |


## Scorecard (period-specific axes)
B 2 (update order audited: self-clocked, not a sweep) · C 1 (held-out bound vs floor and σ_rand; at the floor) · D 1 (sweep signature absent, as the audit implies).

## Notes
