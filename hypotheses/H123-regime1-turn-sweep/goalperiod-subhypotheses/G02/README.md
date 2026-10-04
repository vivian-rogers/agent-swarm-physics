# H123 × G02: Unsupervised agents look back on their previous goal and forward to their next (2025-05-10 → 2025-05-11)

**Verdict:** failed
**Role:** exploratory
**Period:** regime I · 4 agents · one room · 2 active days. Units: 2 (2025-05-10→2025-05-11, 2 d).

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
| 2 | self-clocked asynchronous | 0.015 (0.008) | 1.88 (1.23) | 0.96 | 0.67 | 1.11 [1.00, 1.24] | mixed |

**EP (O3/O4), talk and mode spins.**

No unit with ≥ 2 usable days: EP not estimated.

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 HH: sweep (η_ord ≥ 0.5, CV_gap ≤ 0.5) | self-clocked asynchronous in 1/1 units; η_ord ≤ 0.015 | HH failed; my P1 supported |
| P1c L_name ≤ 1.25 | see table | supported |
| P3 σ_sweep ≈ σ_rand ≈ 0 | n/a | n/a |
| P4 no sweep signature | No unit has σ× above the A1 floor at any lag. | supported |


## Scorecard (period-specific axes)
B 2 (update order audited: self-clocked, not a sweep) · C 1 (held-out bound vs floor and σ_rand; at the floor) · D 1 (sweep signature absent, as the audit implies).

## Notes
