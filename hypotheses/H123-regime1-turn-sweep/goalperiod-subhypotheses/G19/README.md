# H123 × G19: Create a popular daily puzzle game like Wordle (2025-11-03 → 2025-11-14)

**Verdict:** failed
**Role:** exploratory
**Period:** regime I · 8 agents · one room · 10 active days. Units: 19a (2025-11-03→2025-11-13, 9 d), 19b (2025-11-14→2025-11-14, 1 d).

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
| 19a | self-clocked asynchronous | 0.052 (0.000) | 1.39 (1.09) | 0.14 | 1.00 | 1.31 [1.23, 1.39] | mixed |
| 19b | self-clocked asynchronous | 0.047 (0.004) | 1.55 (1.08) | 0.16 | 1.00 | 1.32 (1 day) | mixed |

**EP (O3/O4), talk and mode spins.**

| Unit · channel | N · steps | σ×(1) | σ×(2) | σ×(4) | floor q95 (lag 2) | σ_sweep − σ_rand (lag 2 / 4) | RMS J_s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 19a · talk | 7 · 22932 | -0.08 | -0.11 | -0.29 | +0.45 | -0.02 / +0.02 | 0.102 |
| 19a · mode | 7 · 22932 | +0.33 | +0.88 ★ | +2.28 ★ | +0.64 | +0.01 / +0.20 | 0.137 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 HH: sweep (η_ord ≥ 0.5, CV_gap ≤ 0.5) | self-clocked asynchronous in 2/2 units; η_ord ≤ 0.052 | HH failed; my P1 supported |
| P1c L_name ≤ 1.25 | see table | partly (weak lift > 1.25 in some unit, < 1.5) |
| P3 σ_sweep ≈ σ_rand ≈ 0 | abs(σ_sweep − σ_rand) ≤ 0.20×10⁻³ | supported |
| P4 no sweep signature | Units with σ× above the A1 floor: 19a (mode; σ×(1) also above: False). Where σ× clears the floor, lag 1 clears it too or is positive, and σ× is ≥ 5× abs(σ_sweep − σ_rand): not the sweep signature, and the HH kill clause (σ× ≫ σ_sweep) applies to that unit. With a 10–25% per-test floor size (synthetic), isolated hits are expected by chance. | supported |


## Scorecard (period-specific axes)
B 2 (update order audited: self-clocked, not a sweep) · C 1 (held-out bound vs floor and σ_rand; at the floor) · D 1 (sweep signature absent, as the audit implies).

## Notes
