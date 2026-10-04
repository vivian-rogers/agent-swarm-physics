# H123 × G27: Hack the OWASP Juice Shop hacking playground. Compete to see which agent can complete the most challenges (2026-01-12 → 2026-01-23)

**Verdict:** failed (HH: not a sweep; native N3 also not a sweep)
**Role:** exploratory
**Period:** regime I · 10 agents · one room · 10 active days. Units: 27 (2026-01-12→2026-01-23, 10 d).

## Why this period
Primary period. Ten non-holdout days, N = 10, one unit with no step change; the goal-period file ranks model 02 first for #27. It also hosts native N3 (chat-mode sub-sequence, the turn pointer's domain). Layer role: exploratory · replication + native N3 (primary).

## Prediction
*Written 2026-10-04 ~22:03 UTC, before running on this period (card predictions applied here).*
- P1 (audit, all calls): not a sweep; class self-clocked asynchronous (κ_par ≥ 0.3, η_ord < 0.2). HH counter-prediction: sweep (η_ord ≥ 0.5, CV_gap ≤ 0.5). Random sequential would kill the HH.
- P1c: L_name ≤ 1.25 (being named does not pull the next call).
- P3 (EP, talk spin, after the audit): σ_sweep ≈ σ_rand ≈ 0 (< 10⁻⁴ nats/step); σ_× at the floor. Kill (HH): σ_× > 3 σ_sweep with CI excluding it.
- P4: no lag-1-zero / lag-2-positive sweep signature.
- N3 (chat-mode calls only): not a sweep (η_ord < 0.3); the HH reading needs η_ord ≥ 0.5 and CV_gap ≤ 0.5.

## Result
*Run 2026-10-04 22:06 UTC (audit, `analysis/audit.py`) and 22:11–22:17 UTC (EP, `analysis/run.py`); data `data/processed/H123-regime1-turn-sweep/results/{audit,ep}.parquet`; cross-period figures `../../figures/audit.pdf`, `../../figures/ep_talk.pdf`.* EP in 10⁻³ nats per step (one step = one model call); ★ = above the A1 floor (block-flip q95 and σ_rand q95).

**Audit (O1, run first).**

| Unit | Class (all calls) | η_ord (shuffle) | CV_gap (shuffle) | r/r₀ | κ_par | L_name [95% CI] | Class (chat-mode calls) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 27 | self-clocked asynchronous | 0.017 (0.000) | 1.67 (1.06) | 0.37 | 1.00 | 0.98 [0.95, 1.00] | mixed |

**EP (O3/O4), talk and mode spins.**

| Unit · channel | N · steps | σ×(1) | σ×(2) | σ×(4) | floor q95 (lag 2) | σ_sweep − σ_rand (lag 2 / 4) | RMS J_s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 27 · talk | 10 · 44083 | -0.37 | -0.72 | -1.45 | +0.11 | +0.04 / +0.08 | 0.053 |
| 27 · mode | 10 · 44083 | -0.30 | -0.48 | -0.82 | +0.31 | +0.07 / +0.19 | 0.049 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 HH: sweep (η_ord ≥ 0.5, CV_gap ≤ 0.5) | self-clocked asynchronous in 1/1 units; η_ord ≤ 0.017 | HH failed; my P1 supported |
| P1c L_name ≤ 1.25 | see table | supported |
| P3 σ_sweep ≈ σ_rand ≈ 0 | abs(σ_sweep − σ_rand) ≤ 0.19×10⁻³ | supported |
| P4 no sweep signature | No unit has σ× above the A1 floor at any lag. | supported |


**Native N3 (chat-mode calls only, the turn pointer's domain).** 5,340 chat-mode calls: class *mixed* (not a sweep). η_ord 0.005 vs shuffle 0.004; CV_gap 1.11 vs shuffle 1.04 (burstier than random, the opposite of a sweep's 0); modal-successor share 0.167 vs 0.168; r/r₀ 0.79. The chat-mode sub-sequence is indistinguishable from a random order. **N3 verdict: HH reading failed; my prediction (η_ord < 0.3) supported.**

**Sensitivity (talk, lag 2):** no edge cut σ×(2) −0.28×10⁻³ (floor q95 +0.21); first day dropped −0.50×10⁻³ (floor +0.08). Neither clears the floor. Per agent-hour, σ×(2) = −0.10 nats (1,377 calls per hour, 10 agents): consistent with zero.

**Synthetic on this period's order (axis F, `../../figures/synthetic.pdf`):** a symmetric-J kinetic Ising driven by G27's real call order makes no EP at any J₀ ≤ 2 (σ× within the random-order spread at lags 1, 2, 4), whereas the same J on an exact round robin gives σ×(4) above the floor in 95–100% of worlds.

## Scorecard (period-specific axes)
B 2 (update order audited: self-clocked, not a sweep) · C 1 (held-out bound vs floor and σ_rand; at the floor) · D 1 (sweep signature absent, as the audit implies).

## Notes
