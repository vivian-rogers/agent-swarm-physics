# H123 × G03: Holiday: do whatever you'd like! Next goal will begin soon (2025-05-12 → 2025-05-14)

**Verdict:** failed
**Role:** exploratory
**Period:** regime I · 4 agents · one room · 3 active days. Units: 3 (2025-05-12→2025-05-14, 3 d).

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
| 3 | self-clocked asynchronous | 0.022 (0.005) | 1.25 (1.18) | 0.58 | 0.86 | 1.12 [0.85, 1.50] | mixed |

**EP (O3/O4), talk and mode spins.**

| Unit · channel | N · steps | σ×(1) | σ×(2) | σ×(4) | floor q95 (lag 2) | σ_sweep − σ_rand (lag 2 / 4) | RMS J_s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3 · talk | 4 · 2514 | +0.24 | -0.94 | -1.97 | +1.19 | +1.61 / +0.56 | 0.163 |
| 3 · mode | 4 · 2514 | +1.80 ★ | +4.41 ★ | +9.48 ★ | +2.97 | -0.11 / +0.28 | 0.384 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 HH: sweep (η_ord ≥ 0.5, CV_gap ≤ 0.5) | self-clocked asynchronous in 1/1 units; η_ord ≤ 0.022 | HH failed; my P1 supported |
| P1c L_name ≤ 1.25 | see table | supported |
| P3 σ_sweep ≈ σ_rand ≈ 0 | abs(σ_sweep − σ_rand) ≤ 0.56×10⁻³ | supported |
| P4 no sweep signature | Units with σ× above the A1 floor: 3 (mode; σ×(1) also above: True). Where σ× clears the floor, lag 1 clears it too or is positive, and σ× is ≥ 5× abs(σ_sweep − σ_rand): not the sweep signature, and the HH kill clause (σ× ≫ σ_sweep) applies to that unit. With a 10–25% per-test floor size (synthetic), isolated hits are expected by chance. | supported |


## Scorecard (period-specific axes)
B 2 (update order audited: self-clocked, not a sweep) · C 1 (held-out bound vs floor and σ_rand; at the floor) · D 1 (sweep signature absent, as the audit implies).

## Notes
