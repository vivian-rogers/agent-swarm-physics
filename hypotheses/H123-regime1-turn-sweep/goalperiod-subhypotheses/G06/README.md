# H123 × G06: Create your own merch store. Whichever agent's store makes the most profit wins! (2025-06-26 → 2025-07-15)

**Verdict:** failed
**Role:** exploratory
**Period:** regime I · 4 agents · one room · 15 active days. Units: 6a (2025-06-26→2025-07-02, 6 d), 6b (2025-07-03→2025-07-15, 9 d).

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
| 6a | self-clocked asynchronous | 0.069 (0.000) | 1.35 (1.16) | 0.33 | 0.96 | 1.16 [0.93, 1.32] | random sequential |
| 6b | self-clocked asynchronous | 0.082 (0.002) | 1.11 (1.17) | 0.28 | 0.97 | 1.06 [0.95, 1.16] | mixed |

**EP (O3/O4), talk and mode spins.**

| Unit · channel | N · steps | σ×(1) | σ×(2) | σ×(4) | floor q95 (lag 2) | σ_sweep − σ_rand (lag 2 / 4) | RMS J_s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 6a · talk | 4 · 6805 | -0.38 | -0.23 | +0.22 | +0.93 | -0.11 / -0.08 | 0.090 |
| 6a · mode | 4 · 6805 | -0.92 | -1.98 | -4.10 | +0.47 | +0.03 / +0.04 | 0.109 |
| 6b · talk | 4 · 9895 | -0.12 | -0.22 | -0.21 | +0.57 | +0.00 / -0.13 | 0.062 |
| 6b · mode | 4 · 9895 | -0.37 | -0.81 | -1.69 | +0.18 | +0.10 / +0.08 | 0.025 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 HH: sweep (η_ord ≥ 0.5, CV_gap ≤ 0.5) | self-clocked asynchronous in 2/2 units; η_ord ≤ 0.082 | HH failed; my P1 supported |
| P1c L_name ≤ 1.25 | see table | supported |
| P3 σ_sweep ≈ σ_rand ≈ 0 | abs(σ_sweep − σ_rand) ≤ 0.13×10⁻³ | supported |
| P4 no sweep signature | No unit has σ× above the A1 floor at any lag. | supported |


## Scorecard (period-specific axes)
B 2 (update order audited: self-clocked, not a sweep) · C 1 (held-out bound vs floor and σ_rand; at the floor) · D 1 (sweep signature absent, as the audit implies).

## Notes
